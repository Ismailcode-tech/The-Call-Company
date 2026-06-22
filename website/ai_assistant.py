from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma.vectorstores import Chroma
from .models import Plan
from config import Config
from flask import Blueprint, request, jsonify, g
from pydantic import BaseModel, ValidationError
from typing import Optional, TypedDict
import os
import re
import json
from sqlalchemy import create_engine, text
from website.auth.tokengeneration import token_required
import chromadb
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.chat_history import InMemoryChatMessageHistory

ai_bp = Blueprint("AI", __name__, url_prefix="/api/ai_assistant")



ai_bp = Blueprint("AI", __name__, url_prefix="/api/ai_assistant")
VALID_PROVIDERS = {"fone", "gap", "flipper"}
ALL_PROVIDER_PATTERNS = [
    r"\b(each|every|all)\s+providers?\b",
    r"\b(best|top|cheapest|recommended?)\s+plan(s?)\s+from\s+(each|all)\s+providers?\b",
    r"\b(compare|comparison)\b.*\b(providers?)\b",
    r"\b(other|remaining)\s+providers?\b",
]

# Helper function: checks if the user is asking to compare plans across all providers.
# It uses regular expressions to find keywords like "all", "each", "compare", or "every provider".
# If matched, we'll bypass single provider filters and retrieve a wider selection.
def user_requests_all_providers(question: str) -> bool:
    text = question.lower()
    return any(re.search(pattern, text) for pattern in ALL_PROVIDER_PATTERNS)


load_dotenv()
# Initialize ChatGroq LLM client using the specified model and our API key from the config.
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=Config.GROQ_API_KEY
)

# Pydantic schema used to validate the structured filters extracted from the user's message.
# It ensures type safety and filters out any garbage keys.
class PlanFilter(BaseModel):
    provider: Optional[str] = None
    price_lte: Optional[int] = None
    data_gb: Optional[int] = None
    has_phone: Optional[bool] = None


# Uses LLM to extract structured search filters from the user's message.
# We instruct the model to identify filter rules and output a JSON format.
# We then parse and validate the JSON using the PlanFilter model.
def extract_filter(question: str, chat_history=None) -> dict:

    prompt = f"""
    You are a telecom assistant.

    Extract filter from user message:

    Rules:
    - provider must be exactly one of: "fone", "gap", "flipper".
    - Use provider = null when the user asks about all providers, other providers, comparisons, or any request for best plans across more than one provider.
    - Do not invent provider names or return any provider not in the list.
    - price: under 10 → price_lte = 10
    - unlimited → data_gb = 9999
    - with phone → has_phone = true

    Return only valid JSON with keys: provider, price_lte, data_gb, has_phone.
    If no filters apply, return {{}}.

    Message:
    {question}
    """

    result = llm.invoke(prompt)
    text = getattr(result, 'content', str(result))
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')

    parsed_json = {}
    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError:
        # Fallback in case LLM wraps the response in extra text/markdown blocks
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                parsed_json = json.loads(match.group(0))
            except json.JSONDecodeError:
                parsed_json = {}

    try:
        validated = PlanFilter(**parsed_json)
        return validated.model_dump(exclude_none=True)
    except ValidationError as e:
        print(f"Validation error in extract_filter: {e}")
        return {}

# Fetch all mobile plans from the MySQL database using SQLAlchemy.
# We join the 'plans' table with the 'network_providers' table to get the name of each provider.
def fetch_plans_from_db():

    db_url = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not db_url:
        raise ValueError("SQLALCHEMY_DATABASE_URI is not set in environment variables.")


    engine = create_engine(db_url)


    query="""

        SELECT 
            p.id,
            p.provider_id,
            n.name AS provider_name,   -- Fetches the network provider name (e.g. O2)
            p.name AS plan_name,        -- Fetches the plan name (e.g. Super Saver)
            p.data_gb,
            p.unlimited_data,
            p.calls,
            p.texts,
            p.phone_included,
            p.monthly_price
        FROM plans p
        INNER JOIN network_providers n ON p.provider_id = n.id

    """

    with engine.connect() as conn:
        result = conn.execute(text(query))

        # Convert row mapping objects to a standard list of dictionaries
        rows = [dict(row._mapping) for row in result]

    return rows


# fallback safety handler for comparison queries
# if the vector search missed any provider, this queries a cheap default plan
# for that missing provider from the database to guarantee all networks are represented
def get_missing_provider_plans(represented_providers):
    """Fetch one plan from each missing provider."""
    missing = VALID_PROVIDERS - represented_providers
    if not missing:
        return []

    db_url = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not db_url:
        return []

    engine = create_engine(db_url)
    plans = []
    
    for provider in missing:
        query = f"""
            SELECT 
                p.id,
                p.provider_id,
                n.name AS provider_name,
                p.name AS plan_name,
                p.data_gb,
                p.unlimited_data,
                p.calls,
                p.texts,
                p.phone_included,
                p.monthly_price
            FROM plans p
            INNER JOIN network_providers n ON p.provider_id = n.id
            WHERE LOWER(n.name) = LOWER('{provider}')
            ORDER BY p.monthly_price
            LIMIT 1
        """
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query))
                rows = [dict(row._mapping) for row in result]
                plans.extend(rows)
        except Exception as e:
            print(f"Error fetching plans for {provider}: {e}")
    
    return plans

# Converts database dict records into LangChain Document format.
#  page_content: contains formatted text describing the plan details.
#  metadata: structured attributes for quick key-value searches/filters in ChromaDB.
def build_document(records):

    docs=[]
    for r in records:
        # Get the provider name and plan name from the joined SQL query
        provider = r["provider_name"]  
        plan_name = r["plan_name"]      
        
        # 1. Resolve Data Info
        if r["unlimited_data"]:
            data_info = "Unlimited"
        elif r["data_gb"] is None or r["data_gb"] == 0:
            data_info = "No Data Included"
        else:
            data_info = f"{r['data_gb']} GB"
        # 2. Resolve Calls Info
        if r["calls"] == 'unl':
            calls_info = "Unlimited"
        elif r["calls"] is None:
            calls_info = "No Calls Included"
        else:
            calls_info = f"{r['calls']} minutes"

        # 3. Resolve Texts Info
        if r["texts"] == 'unl':
            text_info = "Unlimited"
        elif r["texts"] is None:
            text_info = "No Texts Included"
        else:
            text_info = f"{r['texts']} texts"

        # 4. Resolve Phone Info
        if r["phone_included"] is None:
            phone_info = "SIM Only (No Phone Included)"
        else:
            phone_info = f"Phone Included: {r['phone_included']}"
        
        page_content = (
            f"Provider Name: {provider}\n"
            f"Plan Name: {plan_name}\n"
            f"Data: {data_info}\n"
            f"Texts: {text_info}\n"
            f"Calls: {calls_info}\n"
            f"Phone Included: {phone_info}\n"
            f"Monthly Price: {r['monthly_price']}\n"

        )

        metadata = {

            "plan_id": int(r["id"]),
            "provider": r["provider_name"],               
            "plan_name": r["plan_name"],                  
            "price": int(r["monthly_price"]),         
            "data_gb": 9999 if r["unlimited_data"] else (0 if r["data_gb"] is None else int(r["data_gb"])),
            "phone_included": r["phone_included"],           
            "has_phone": r["phone_included"] is not None
            
        }
        docs.append(Document(page_content=page_content, metadata=metadata))
        
    return docs

# builds the vector store on system startup.
# it downloads/loads the SentenceTransformer model, connects to our ChromaDB client and embeds all database plans into the collection.

def create_vectore():
    print("Fetching plans from MySQL using SQLAlchemy")

    try:
        records = fetch_plans_from_db()
        print(f"Loaded {len(records)} plans.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    print("Constructing LangChain Documents")
    doc = build_document(records)
    if not doc:
        print("No document was built")
        return
    
    print("Generating embeddings")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    client = chromadb.CloudClient(
            api_key=Config.CHROMA_API_KEY,
            tenant=Config.CHROMA_TENANT,
            database=Config.CHROMA_DATABASE
    )
    
    print("Saving vector index into local ChromaDB")
    
    vectorestore = Chroma(
        
        embedding_function=embeddings,
        client=client,
        collection_name="plans"
    )
    vectorestore.add_documents(doc)
    
    print("ChromaDB index created successfully")
    
    return vectorestore

# Global initialization of vector store at startup
vectorestore=create_vectore()

# In-memory dictionary to store chat histories for active users
chat_histories = {}
       
      
# Get or create the message history logger for a specific member ID.
def get_chat_history(user_id):
    if user_id not in chat_histories:
        chat_histories[user_id] = InMemoryChatMessageHistory()
    return chat_histories[user_id]


# Uses LLM to rewrite follow up questions to be self-contained.
# for instance if the user previously asked about "Fone plans" and now asks "any cheaper?",
# it rewrites it to "Any cheaper plan from Fone?". This gives the vector search enough context.
def rewrite_question(question, chat_context):
    prompt = f"""
    Previous conversation:
    {chat_context}

    Current question:
    {question}
    Rewrite the current question so it becomes
    fully self contained.

    Examples:

    Recommend a Gap plan
    another plan

    

    Recommend another Gap plan

    Return only the rewritten question.




    """
    respoonse = llm.invoke(prompt)
    return respoonse.content.strip()

# Flask POST endpoint that coordinates the entire chat interaction:
# 1. Rewrites user question based on past conversational history
# 2. Extracts filters (provider, maximum price, phone option)
# 3. Invokes ChromaDB vector retrieval with filters
# 4. Merges missing providers if user requested provider comparison
# 5. Generates and returns a friendly answer
@ai_bp.route('/chat', methods=['POST'])
@token_required 
def chat():

    data = request.get_json()
    question = data.get("message")
    user_id = str(g.current_member.id)
    
    # Retrieve user's chat history context
    history = get_chat_history(str(user_id))
    previous_messages = history.messages
    chat_context = "\n".join(
        f"{msg.type}: {msg.content}"
        for msg in previous_messages
    )

    if not question:
        return jsonify({"error":"message is required"}), 400
    
    # Rewrite the question with history context
    rewritten_question  = rewrite_question(
        question,
        chat_context
    )

    # Extract filter settings using LLM
    structured_filter = extract_filter(rewritten_question)
    force_all_providers = user_requests_all_providers(rewritten_question)

    # Build metadata filter mapping for ChromaDB query
    filter_dict = {}
    if not force_all_providers:
        provider = structured_filter.get("provider") if isinstance(structured_filter, dict) else None
        if provider:
            provider_normalized = provider.strip().lower()
            if provider_normalized in VALID_PROVIDERS:
                filter_dict["provider"] = provider_normalized

    price_lte = structured_filter.get("price_lte") if isinstance(structured_filter, dict) else None
    if price_lte is not None:
        filter_dict["price"] = {"$lte": price_lte}

    data_gb = structured_filter.get("data_gb") if isinstance(structured_filter, dict) else None
    if data_gb is not None:
        filter_dict["data_gb"] = data_gb

    has_phone = structured_filter.get("has_phone") if isinstance(structured_filter, dict) else None
    if has_phone is not None:
        filter_dict["has_phone"] = has_phone

    # Configure top-k matches depending on whether we want to compare across all networks
    search_kwargs = {"k": 9 if force_all_providers else 3}
    # if filter_dict:
    #     ["filter"] = filter_dict

    if vectorestore is None:
        return jsonify({"error":"vector store unavailable"}), 500

    # Retrieve candidate plans from vector store
    retriever = vectorestore.as_retriever(search_kwargs=search_kwargs)
    
    results = retriever.invoke(rewritten_question)

    # Inject missing provider plans to guarantee completeness for comparisons
    if force_all_providers:

        represented_providers = set()
        for doc in results:
            if hasattr(doc, 'metadata') and 'provider' in doc.metadata:
                represented_providers.add(doc.metadata['provider'].lower())

        missing_plans = get_missing_provider_plans(represented_providers)

        if missing_plans:
            
            results.extend(build_document(missing_plans))

    context = "\n".join(doc.page_content for doc in results)

    # Prompt LLM to formulate the final answer using only retrieved information
    prompt = ChatPromptTemplate.from_template(
        """
        You are a telecom assistant
        You are a friendly and helpful assistant for The Call Company, 
        a UK mobile phone plan provider.
        We have three providers: Fone, Gap, and Flipper. 
        If the user asks for the best plan from each provider, recommend one plan from Fone, Gap, and Flipper.
        Help customers find the best plan for their needs. 
        If the user asks for another plan from the same provider, list at least two other plans from that provider”

        Answer only using this information:

        {context}
        Question:
        {question}
        """
    )

    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": rewritten_question,
    })
    
    # Save current messages to the persistent user history
    history.add_user_message(question)
    history.add_ai_message(response.content)

    return jsonify({"response": response.content})
