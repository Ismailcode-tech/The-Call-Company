from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma.vectorstores import Chroma
from config import Config
from flask import Blueprint, request, jsonify, g
from pydantic import BaseModel, ValidationError
from typing import Optional
import os, re, json
from sqlalchemy import create_engine, text
from website.auth.tokengeneration import token_required
import chromadb
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()

ai_bp = Blueprint("AI", __name__, url_prefix="/api/ai_assistant")

VALID_PROVIDERS = {"fone", "gap", "flipper"}
ALL_PROVIDER_PATTERNS = [
    r"\b(each|every|all)\s+providers?\b",
    r"\b(best|top|cheapest|recommended?)\s+plan(s?)\s+from\s+(each|all)\s+providers?\b",
    r"\b(compare|comparison)\b.*\b(providers?)\b",
    r"\b(other|remaining)\s+providers?\b",
]

def user_requests_all_providers(question: str) -> bool:
    return any(re.search(p, question.lower()) for p in ALL_PROVIDER_PATTERNS)


# ── LLM (lazy) ────────────────────────────────────────────
llm = None

def get_llm():
    global llm
    if llm is None:
        api_key = getattr(Config, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
        if not api_key:
            print("GROQ_API_KEY not configured.")
            return None
        try:
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
        except Exception as e:
            print(f"LLM init failed: {e}")
            return None
    return llm


# ── CHANGE 1: PlanFilter — added calls_gte, texts_gte, unlimited_data ──
# Previously missing these fields so calls/texts were never extracted or filtered.
class PlanFilter(BaseModel):
    provider:       Optional[str]  = None
    price_lte:      Optional[int]  = None
    data_gb_gte:    Optional[int]  = None   # ← renamed from data_gb for clarity
    calls_gte:      Optional[int]  = None   # ← NEW
    texts_gte:      Optional[int]  = None   # ← NEW
    has_phone:      Optional[bool] = None
    unlimited_data: Optional[bool] = None   # ← NEW


# ── CHANGE 2: extract_filter — updated prompt to extract all new fields ──
# Previously the LLM was never told to look for calls, texts, or unlimited data.
def extract_filter(question: str) -> dict:
    llm_client = get_llm()
    if llm_client is None:
        return {}

    prompt = f"""
You are a telecom filter extraction assistant.

Extract structured search filters from the user message below.

Rules:
- provider must be exactly one of: "fone", "gap", "flipper". Use null for comparisons or all-provider queries.
- price_lte: maximum monthly price the user will pay (integer)
- data_gb_gte: minimum GB of data required (integer). Use 9999 for "unlimited".
- unlimited_data: true only if the user explicitly asks for unlimited data
- calls_gte: minimum call minutes required (integer). Use 9999 for "unlimited calls".
- texts_gte: minimum texts required (integer). Use 9999 for "unlimited texts".
- has_phone: true if user wants a handset included, false if SIM only, null if not mentioned.

Examples:
"Find me a Fone plan under £30 with at least 5GB"
→ {{"provider":"fone","price_lte":30,"data_gb_gte":5}}

"I need a plan with a phone, unlimited data and 750 minutes of calls under £60"
→ {{"price_lte":60,"unlimited_data":true,"data_gb_gte":9999,"calls_gte":750,"has_phone":true}}

"Cheapest SIM only plan"
→ {{"has_phone":false}}

Return ONLY valid JSON with those keys. If a field does not apply, omit it entirely.

Message: {question}
"""

    result   = llm_client.invoke(prompt)
    raw_text = getattr(result, "content", str(result))
    if isinstance(raw_text, bytes):
        raw_text = raw_text.decode("utf-8", errors="ignore")

    parsed = {}
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.S)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                parsed = {}

    try:
        validated = PlanFilter(**parsed)
        return validated.model_dump(exclude_none=True)
    except ValidationError as e:
        print(f"PlanFilter validation error: {e}")
        return {}


# ── Database helpers (unchanged) ──────────────────────────
def fetch_plans_from_db():
    db_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not db_url:
        raise ValueError("SQLALCHEMY_DATABASE_URI not set.")
    engine = create_engine(db_url)
    query  = """
        SELECT p.id, p.provider_id,
               n.name AS provider_name,
               p.name AS plan_name,
               p.data_gb, p.unlimited_data,
               p.calls, p.texts,
               p.phone_included, p.monthly_price
        FROM plans p
        INNER JOIN network_providers n ON p.provider_id = n.id
    """
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return [dict(row._mapping) for row in result]


def get_missing_provider_plans(represented_providers):
    missing = VALID_PROVIDERS - represented_providers
    if not missing:
        return []
    db_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    if not db_url:
        return []
    engine = create_engine(db_url)
    plans  = []
    for provider in missing:
        q = f"""
            SELECT p.id, p.provider_id,
                   n.name AS provider_name,
                   p.name AS plan_name,
                   p.data_gb, p.unlimited_data,
                   p.calls, p.texts,
                   p.phone_included, p.monthly_price
            FROM plans p
            INNER JOIN network_providers n ON p.provider_id = n.id
            WHERE LOWER(n.name) = LOWER('{provider}')
            ORDER BY p.monthly_price
            LIMIT 1
        """
        try:
            with engine.connect() as conn:
                result = conn.execute(text(q))
                plans.extend([dict(row._mapping) for row in result])
        except Exception as e:
            print(f"Missing provider fetch error ({provider}): {e}")
    return plans


# ── CHANGE 3: build_document — added calls_int and texts_int to metadata ──
# Previously calls and texts were only in page_content as strings like "500 minutes".
# ChromaDB $gte filtering requires integers in metadata.
# "unl" → 9999, None → 0, numeric string → int.
def build_document(records):
    docs = []
    for r in records:
        provider  = r["provider_name"]
        plan_name = r["plan_name"]

        # Resolve display strings for page_content
        data_info  = "Unlimited" if r["unlimited_data"] else (
                     "No Data"   if not r["data_gb"]   else f"{r['data_gb']} GB")
        calls_info = "Unlimited" if r["calls"] == "unl" else (
                     "No Calls"  if r["calls"] is None  else f"{r['calls']} minutes")
        text_info  = "Unlimited" if r["texts"] == "unl" else (
                     "No Texts"  if r["texts"] is None  else f"{r['texts']} texts")
        phone_info = "SIM Only"  if r["phone_included"] is None else f"Phone: {r['phone_included']}"

        page_content = (
            f"Provider Name: {provider}\n"
            f"Plan Name: {plan_name}\n"
            f"Data: {data_info}\n"
            f"Texts: {text_info}\n"
            f"Calls: {calls_info}\n"
            f"Phone Included: {phone_info}\n"
            f"Monthly Price: £{r['monthly_price']}\n"
        )

        # ← calls_int and texts_int added so $gte filtering works
        def to_int_calls(v):
            if v == "unl":    return 9999
            if v is None:     return 0
            try:              return int(v)
            except:           return 0

        metadata = {
            "plan_id":      int(r["id"]),
            "provider":     provider.lower(),        # ← lowercase for consistent filtering
            "plan_name":    plan_name,
            "price":        int(r["monthly_price"]),
            "data_gb":      9999 if r["unlimited_data"] else (
                            0    if r["data_gb"] is None else int(r["data_gb"])),
            "calls_int":    to_int_calls(r["calls"]),   # ← NEW integer field
            "texts_int":    to_int_calls(r["texts"]),   # ← NEW integer field
            "has_phone":    r["phone_included"] is not None,
            "phone_included": r["phone_included"],
        }
        docs.append(Document(page_content=page_content, metadata=metadata))
    return docs


# ── CHANGE 4: build_chroma_filter — new dedicated function ───────────────
# Previously filter conditions were built inline in chat() with scattered logic.
# Multiple conditions were not wrapped in $and so ChromaDB ignored all but one.
# This function produces correct single-condition or $and multi-condition filters.
def build_chroma_filter(structured_filter: dict, force_all_providers: bool) -> dict:
    conditions = []

    # Provider — only add when not a cross-provider comparison
    if not force_all_providers:
        provider = structured_filter.get("provider")
        if provider:
            normalized = provider.strip().lower()
            if normalized in VALID_PROVIDERS:
                conditions.append({"provider": normalized})

    if "price_lte" in structured_filter:
        conditions.append({"price": {"$lte": int(structured_filter["price_lte"])}})

    if structured_filter.get("unlimited_data"):
        # unlimited_data requested → data_gb must be 9999
        conditions.append({"data_gb": {"$gte": 9999}})
    elif "data_gb_gte" in structured_filter:
        conditions.append({"data_gb": {"$gte": int(structured_filter["data_gb_gte"])}})

    if "calls_gte" in structured_filter:
        conditions.append({"calls_int": {"$gte": int(structured_filter["calls_gte"])}})

    if "texts_gte" in structured_filter:
        conditions.append({"texts_int": {"$gte": int(structured_filter["texts_gte"])}})

    if "has_phone" in structured_filter:
        conditions.append({"has_phone": bool(structured_filter["has_phone"])})

    # Build correct ChromaDB filter syntax
    if len(conditions) == 0:
        return {}
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


# ── CHANGE 5: relaxed_search — new fallback when retrieval returns 0 ─────
# Previously empty results → empty context → LLM hallucinates.
# This progressively relaxes filters until at least one plan is returned.
def relaxed_search(vector_store, question: str, filter_dict: dict, k: int) -> list:
    # Ordered relaxation steps — remove strictest filters first
    relaxation_steps = [
        ["calls_int", "texts_int"],  # step 1: remove calls and texts
        ["texts_int"],               # step 2: remove texts only
        ["calls_int"],               # step 3: remove calls only
        ["data_gb"],                 # step 4: remove data requirement
    ]

    # Try with current filter first
    for step_keys in relaxation_steps:
        relaxed = _remove_keys_from_filter(filter_dict, step_keys)
        search_kwargs = {"k": k}
        if relaxed:
            search_kwargs["filter"] = relaxed
        retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
        results   = retriever.invoke(question)
        if results:
            print(f"Relaxed search succeeded after removing: {step_keys}")
            return results

    # Final fallback — no filters at all, return k cheapest
    print("All filters removed — returning top-k by similarity only")
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(question)


def _remove_keys_from_filter(filter_dict: dict, keys_to_remove: list) -> dict:
    """Remove specific leaf keys from a $and filter or a simple filter."""
    if not filter_dict:
        return {}

    if "$and" in filter_dict:
        kept = []
        for condition in filter_dict["$and"]:
            # Each condition is {field: value} — skip if field in keys_to_remove
            if not any(k in condition for k in keys_to_remove):
                kept.append(condition)
        if len(kept) == 0:  return {}
        if len(kept) == 1:  return kept[0]
        return {"$and": kept}

    # Simple single-condition filter
    if any(k in filter_dict for k in keys_to_remove):
        return {}
    return filter_dict


# ── Vector store (lazy) ───────────────────────────────────
vectorestore           = None
vector_store_init_error = None

def create_vectore():
    print("Fetching plans from MySQL…")
    try:
        records = fetch_plans_from_db()
        print(f"Loaded {len(records)} plans.")
    except Exception as e:
        print(f"DB error: {e}")
        return None

    docs = build_document(records)
    if not docs:
        print("No documents built.")
        return None

    print("Generating embeddings…")
    hf_token  = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    emb_kwargs = {"token": hf_token} if hf_token else {}
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        **emb_kwargs,
    )

    client = chromadb.CloudClient(
        api_key=Config.CHROMA_API_KEY,
        tenant=Config.CHROMA_TENANT,
        database=Config.CHROMA_DATABASE,
    )
    print("Indexing into ChromaDB…")
    store = Chroma(
        embedding_function=embeddings,
        client=client,
        collection_name="plans",
    )
    store.add_documents(docs)
    print("ChromaDB index ready.")
    return store


def get_vector_store():
    global vectorestore, vector_store_init_error
    if vectorestore is None and vector_store_init_error is None:
        try:
            vectorestore = create_vectore()
        except Exception as e:
            vector_store_init_error = str(e)
            print(f"Vector store init failed: {e}")
    return vectorestore


# ── Chat history ──────────────────────────────────────────
chat_histories = {}

def get_chat_history(user_id: str) -> InMemoryChatMessageHistory:
    if user_id not in chat_histories:
        chat_histories[user_id] = InMemoryChatMessageHistory()
    return chat_histories[user_id]


def rewrite_question(question: str, chat_context: str) -> str:
    client = get_llm()
    if client is None:
        return question
    prompt = f"""
Previous conversation:
{chat_context}

Current question:
{question}

Rewrite the current question so it is fully self-contained.
Do NOT invent providers, plans, prices, or requirements.
Only add missing context from the previous conversation.
Return ONLY the rewritten question.
"""
    return client.invoke(prompt).content.strip()


# ── CHANGE 6: updated prompt — LLM now ranks and explains matched/unmatched ──
ANSWER_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant for The Call Company, a UK mobile phone plan provider.
The only providers are: Fone, Gap, and Flipper.
NEVER mention EE, O2, Vodafone, Three, or any provider not listed above.
NEVER invent plans, prices, or data allowances.
Answer ONLY using the plans in the context below.

For each plan you recommend:
1. List it clearly with provider, plan name, price, data, calls, texts, and whether a phone is included.
2. Show a matched requirements section using ✔ for each requirement the plan satisfies.
3. Show an unmatched requirements section using ✘ for each requirement the plan does not fully satisfy.
4. If no plan is an exact match, recommend the closest plans and explain why.

If the user asks for a comparison across providers, recommend one plan from each provider.
Sort recommendations from best match to worst match.

Context (retrieved plans):
{context}

User question:
{question}
""")


# ── CHANGE 7: chat() — wired up all new functions ─────────────────────────
@ai_bp.route("/chat", methods=["POST"])
@token_required
def chat():
    data     = request.get_json()
    question = data.get("message")
    user_id  = str(g.current_member.id)

    if not question:
        return jsonify({"error": "message is required"}), 400

    # Chat history
    history          = get_chat_history(user_id)
    chat_context     = "\n".join(
        f"{m.type}: {m.content}" for m in history.messages
    )

    # Step 1 — rewrite follow-up
    rewritten = rewrite_question(question, chat_context)

    # Step 2 — extract filters
    structured_filter   = extract_filter(rewritten)
    force_all_providers = user_requests_all_providers(rewritten)

    print("=" * 60)
    print(f"Original:  {question}")
    print(f"Rewritten: {rewritten}")
    print(f"Filters:   {structured_filter}")
    print(f"AllProviders: {force_all_providers}")

    # Step 3 — build correct ChromaDB filter
    filter_dict = build_chroma_filter(structured_filter, force_all_providers)
    print(f"ChromaDB filter: {filter_dict}")

    # Step 4 — retrieve
    vector_store = get_vector_store()
    if vector_store is None:
        return jsonify({"error": "vector store unavailable"}), 503

    k             = 9 if force_all_providers else 4
    search_kwargs = {"k": k}
    if filter_dict:
        search_kwargs["filter"] = filter_dict

    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    results   = retriever.invoke(rewritten)

    print(f"Retrieved {len(results)} documents.")

    # Step 5 — fallback relaxation if no results
    if not results and filter_dict:
        print("No results — starting relaxed search…")
        results = relaxed_search(vector_store, rewritten, filter_dict, k)

    # Step 6 — inject missing providers for comparison queries
    if force_all_providers:
        represented = {
            doc.metadata.get("provider", "").lower()
            for doc in results
            if hasattr(doc, "metadata")
        }
        missing_records = get_missing_provider_plans(represented)
        if missing_records:
            results.extend(build_document(missing_records))

    for i, doc in enumerate(results, 1):
        print(f"--- Doc {i} ---\n{doc.page_content}\n{doc.metadata}\n")

    context = "\n\n".join(doc.page_content for doc in results)

    if not context.strip():
        return jsonify({"response": "I could not find any matching plans. Please try adjusting your requirements."}), 200

    # Step 7 — generate answer with ranking and explanation
    chain    = ANSWER_PROMPT | get_llm()
    response = chain.invoke({"context": context, "question": rewritten})

    # Persist history
    history.add_user_message(question)
    history.add_ai_message(response.content)

    return jsonify({"response": response.content})











# from langchain_groq import ChatGroq
# from langchain_core.documents import Document
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma.vectorstores import Chroma
# from .models import Plan
# from config import Config
# from flask import Blueprint, request, jsonify, g
# from pydantic import BaseModel, ValidationError
# from typing import Optional, TypedDict
# import os
# import re
# import json
# from sqlalchemy import create_engine, text
# from website.auth.tokengeneration import token_required
# import chromadb
# from langchain_core.prompts import ChatPromptTemplate
# from dotenv import load_dotenv
# from langchain_core.chat_history import InMemoryChatMessageHistory

# ai_bp = Blueprint("AI", __name__, url_prefix="/api/ai_assistant")



# ai_bp = Blueprint("AI", __name__, url_prefix="/api/ai_assistant")
# VALID_PROVIDERS = {"fone", "gap", "flipper"}
# ALL_PROVIDER_PATTERNS = [
#     r"\b(each|every|all)\s+providers?\b",
#     r"\b(best|top|cheapest|recommended?)\s+plan(s?)\s+from\s+(each|all)\s+providers?\b",
#     r"\b(compare|comparison)\b.*\b(providers?)\b",
#     r"\b(other|remaining)\s+providers?\b",
# ]

# # Helper function: checks if the user is asking to compare plans across all providers.
# # It uses regular expressions to find keywords like "all", "each", "compare", or "every provider".
# # If matched, we'll bypass single provider filters and retrieve a wider selection.
# def user_requests_all_providers(question: str) -> bool:
#     text = question.lower()
#     return any(re.search(pattern, text) for pattern in ALL_PROVIDER_PATTERNS)


# load_dotenv()

# llm = None


# def get_llm():
#     global llm
#     if llm is None:
#         api_key = getattr(Config, "GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
#         if not api_key:
#             print("GROQ_API_KEY is not configured; AI assistant features will be unavailable.")
#             return None

#         try:
#             llm = ChatGroq(
#                 model="llama-3.3-70b-versatile",
#                 api_key=api_key,
#             )
#         except Exception as exc:
#             print(f"Failed to initialize LLM client: {exc}")
#             return None

#     return llm

# # Pydantic schema used to validate the structured filters extracted from the user's message.
# # It ensures type safety and filters out any garbage keys.
# class PlanFilter(BaseModel):
#     provider: Optional[str] = None
#     price_lte: Optional[int] = None
#     data_gb: Optional[int] = None
#     has_phone: Optional[bool] = None


# # Uses LLM to extract structured search filters from the user's message.
# # We instruct the model to identify filter rules and output a JSON format.
# # We then parse and validate the JSON using the PlanFilter model.
# def extract_filter(question: str, chat_history=None) -> dict:
#     llm_client = get_llm()
#     if llm_client is None:
#         return {}

#     prompt = f"""
#     You are a telecom assistant.

#     Extract filter from user message:

#     Rules:
#     - provider must be exactly one of: "fone", "gap", "flipper".
#     - Use provider = null when the user asks about all providers, other providers, comparisons, or any request for best plans across more than one provider.
#     - Do not invent provider names or return any provider not in the list.
#     - price: under 10 → price_lte = 10
#     - unlimited → data_gb = 9999
#     - with phone → has_phone = true

#     Return only valid JSON with keys: provider, price_lte, data_gb, has_phone.
#     If no filters apply, return {{}}.

#     Message:
#     {question}
#     """

#     result = llm_client.invoke(prompt)
#     text = getattr(result, 'content', str(result))
#     if isinstance(text, bytes):
#         text = text.decode('utf-8', errors='ignore')

#     parsed_json = {}
#     try:
#         parsed_json = json.loads(text)
#     except json.JSONDecodeError:
#         # Fallback in case LLM wraps the response in extra text/markdown blocks
#         match = re.search(r"\{.*\}", text, re.S)
#         if match:
#             try:
#                 parsed_json = json.loads(match.group(0))
#             except json.JSONDecodeError:
#                 parsed_json = {}

#     try:
#         validated = PlanFilter(**parsed_json)
#         return validated.model_dump(exclude_none=True)
#     except ValidationError as e:
#         print(f"Validation error in extract_filter: {e}")
#         return {}

# # Fetch all mobile plans from the MySQL database using SQLAlchemy.
# # We join the 'plans' table with the 'network_providers' table to get the name of each provider.
# def fetch_plans_from_db():

#     db_url = os.getenv('SQLALCHEMY_DATABASE_URI')
#     if not db_url:
#         raise ValueError("SQLALCHEMY_DATABASE_URI is not set in environment variables.")


#     engine = create_engine(db_url)


#     query="""

#         SELECT 
#             p.id,
#             p.provider_id,
#             n.name AS provider_name,   -- Fetches the network provider name (e.g. O2)
#             p.name AS plan_name,        -- Fetches the plan name (e.g. Super Saver)
#             p.data_gb,
#             p.unlimited_data,
#             p.calls,
#             p.texts,
#             p.phone_included,
#             p.monthly_price
#         FROM plans p
#         INNER JOIN network_providers n ON p.provider_id = n.id

#     """

#     with engine.connect() as conn:
#         result = conn.execute(text(query))

#         # Convert row mapping objects to a standard list of dictionaries
#         rows = [dict(row._mapping) for row in result]

#     return rows


# # fallback safety handler for comparison queries
# # if the vector search missed any provider, this queries a cheap default plan
# # for that missing provider from the database to guarantee all networks are represented
# def get_missing_provider_plans(represented_providers):
#     """Fetch one plan from each missing provider."""
#     missing = VALID_PROVIDERS - represented_providers
#     if not missing:
#         return []

#     db_url = os.getenv('SQLALCHEMY_DATABASE_URI')
#     if not db_url:
#         return []

#     engine = create_engine(db_url)
#     plans = []
    
#     for provider in missing:
#         query = f"""
#             SELECT 
#                 p.id,
#                 p.provider_id,
#                 n.name AS provider_name,
#                 p.name AS plan_name,
#                 p.data_gb,
#                 p.unlimited_data,
#                 p.calls,
#                 p.texts,
#                 p.phone_included,
#                 p.monthly_price
#             FROM plans p
#             INNER JOIN network_providers n ON p.provider_id = n.id
#             WHERE LOWER(n.name) = LOWER('{provider}')
#             ORDER BY p.monthly_price
#             LIMIT 1
#         """
#         try:
#             with engine.connect() as conn:
#                 result = conn.execute(text(query))
#                 rows = [dict(row._mapping) for row in result]
#                 plans.extend(rows)
#         except Exception as e:
#             print(f"Error fetching plans for {provider}: {e}")
    
#     return plans

# # Converts database dict records into LangChain Document format.
# #  page_content: contains formatted text describing the plan details.
# #  metadata: structured attributes for quick key-value searches/filters in ChromaDB.
# def build_document(records):

#     docs=[]
#     for r in records:
#         # Get the provider name and plan name from the joined SQL query
#         provider = r["provider_name"]  
#         plan_name = r["plan_name"]      
        
#         # 1. Resolve Data Info
#         if r["unlimited_data"]:
#             data_info = "Unlimited"
#         elif r["data_gb"] is None or r["data_gb"] == 0:
#             data_info = "No Data Included"
#         else:
#             data_info = f"{r['data_gb']} GB"
#         # 2. Resolve Calls Info
#         if r["calls"] == 'unl':
#             calls_info = "Unlimited"
#         elif r["calls"] is None:
#             calls_info = "No Calls Included"
#         else:
#             calls_info = f"{r['calls']} minutes"

#         # 3. Resolve Texts Info
#         if r["texts"] == 'unl':
#             text_info = "Unlimited"
#         elif r["texts"] is None:
#             text_info = "No Texts Included"
#         else:
#             text_info = f"{r['texts']} texts"

#         # 4. Resolve Phone Info
#         if r["phone_included"] is None:
#             phone_info = "SIM Only (No Phone Included)"
#         else:
#             phone_info = f"Phone Included: {r['phone_included']}"
        
#         page_content = (
#             f"Provider Name: {provider}\n"
#             f"Plan Name: {plan_name}\n"
#             f"Data: {data_info}\n"
#             f"Texts: {text_info}\n"
#             f"Calls: {calls_info}\n"
#             f"Phone Included: {phone_info}\n"
#             f"Monthly Price: {r['monthly_price']}\n"

#         )

#         metadata = {

#             "plan_id": int(r["id"]),
#             "provider": r["provider_name"],               
#             "plan_name": r["plan_name"],                  
#             "price": int(r["monthly_price"]),         
#             "data_gb": 9999 if r["unlimited_data"] else (0 if r["data_gb"] is None else int(r["data_gb"])),
#             "phone_included": r["phone_included"],           
#             "has_phone": r["phone_included"] is not None
            
#         }
#         docs.append(Document(page_content=page_content, metadata=metadata))
        
#     return docs

# # builds the vector store on system startup.
# # it downloads/loads the SentenceTransformer model, connects to our ChromaDB client and embeds all database plans into the collection.

# def create_vectore():
#     print("Fetching plans from MySQL using SQLAlchemy")

#     try:
#         records = fetch_plans_from_db()
#         print(f"Loaded {len(records)} plans.")
#     except Exception as e:
#         print(f"Error connecting to database: {e}")
#         return
    
#     print("Constructing LangChain Documents")
#     doc = build_document(records)
#     if not doc:
#         print("No document was built")
#         return
    
#     print("Generating embeddings")
#     hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
#     embedding_kwargs = {}
#     if hf_token:
#         embedding_kwargs["token"] = hf_token
#     else:
#         print("HF_TOKEN not set; using unauthenticated Hugging Face access.")

#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2",
#         **embedding_kwargs,
#     )

#     client = chromadb.CloudClient(
#             api_key=Config.CHROMA_API_KEY,
#             tenant=Config.CHROMA_TENANT,
#             database=Config.CHROMA_DATABASE
#     )
    
#     print("Saving vector index into local ChromaDB")
    
#     vectorestore = Chroma(
        
#         embedding_function=embeddings,
#         client=client,
#         collection_name="plans"
#     )
#     vectorestore.add_documents(doc)
    
#     print("ChromaDB index created successfully")
    
#     return vectorestore

# # Initialize the vector store lazily to avoid memory spikes during app startup.
# vectorestore = None
# vector_store_init_error = None


# def get_vector_store():
#     global vectorestore, vector_store_init_error

#     if vectorestore is None and vector_store_init_error is None:
#         try:
#             vectorestore = create_vectore()
#         except Exception as exc:
#             vector_store_init_error = str(exc)
#             print(f"Vector store initialization failed: {exc}")

#     return vectorestore


# # In-memory dictionary to store chat histories for active users
# chat_histories = {}
       
      
# # Get or create the message history logger for a specific member ID.
# def get_chat_history(user_id):
#     if user_id not in chat_histories:
#         chat_histories[user_id] = InMemoryChatMessageHistory()
#     return chat_histories[user_id]


# # Uses LLM to rewrite follow up questions to be self-contained.
# # for instance if the user previously asked about "Fone plans" and now asks "any cheaper?",
# # it rewrites it to "Any cheaper plan from Fone?". This gives the vector search enough context.
# def rewrite_question(question, chat_context):
#     llm_client = get_llm()
#     if llm_client is None:
#         return question

#     prompt = f"""
#     Previous conversation:
#     {chat_context}

#     Current question:
#     {question}
#     Rewrite the current question so that it is fully self-contained.

#     Do NOT:

#       invent providers
#       invent phone brands
#       invent prices
#       invent requirements
#       change the meaning

#     Only add missing context from the previous conversation.

#     Return ONLY the rewritten question.





#     """
#     respoonse = llm_client.invoke(prompt)
#     return respoonse.content.strip()

# # Flask POST endpoint that coordinates the entire chat interaction:
# # 1. Rewrites user question based on past conversational history
# # 2. Extracts filters (provider, maximum price, phone option)
# # 3. Invokes ChromaDB vector retrieval with filters
# # 4. Merges missing providers if user requested provider comparison
# # 5. Generates and returns a friendly answer
# @ai_bp.route('/chat', methods=['POST'])
# @token_required 
# def chat():

#     data = request.get_json()
#     question = data.get("message")
#     user_id = str(g.current_member.id)
    
#     # Retrieve user's chat history context
#     history = get_chat_history(str(user_id))
#     previous_messages = history.messages
#     chat_context = "\n".join(
#         f"{msg.type}: {msg.content}"
#         for msg in previous_messages
#     )

#     if not question:
#         return jsonify({"error":"message is required"}), 400
    
#     # Rewrite the question with history context
#     rewritten_question  = rewrite_question(
#         question,
#         chat_context
#     )

#     # Extract filter settings using LLM
#     structured_filter = extract_filter(rewritten_question)
#     force_all_providers = user_requests_all_providers(rewritten_question)

#     # Build metadata filter mapping for ChromaDB query
#     filter_dict = {}
#     if not force_all_providers:
#         provider = structured_filter.get("provider") if isinstance(structured_filter, dict) else None
#         if provider:
#             provider_normalized = provider.strip().lower()
#             if provider_normalized in VALID_PROVIDERS:
#                 filter_dict["provider"] = provider_normalized

#     price_lte = structured_filter.get("price_lte") if isinstance(structured_filter, dict) else None
#     if price_lte is not None:
#         filter_dict["price"] = {"$lte": price_lte}

#     data_gb = structured_filter.get("data_gb") if isinstance(structured_filter, dict) else None
#     if data_gb is not None:
#         filter_dict["data_gb"] = {
#             "$gte": data_gb
#         }

#     has_phone = structured_filter.get("has_phone") if isinstance(structured_filter, dict) else None
#     if has_phone is not None:
#         filter_dict["has_phone"] = has_phone

#     # Configure top-k matches depending on whether we want to compare across all networks
#     search_kwargs = {"k": 9 if force_all_providers else 3}
#     if filter_dict:
#         search_kwargs["filter"] = filter_dict

#     vector_store = get_vector_store()
#     if vector_store is None:
#         return jsonify({"error":"vector store unavailable"}), 503

#     # Retrieve candidate plans from vector store
#     retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
#     print("=" * 60)
#     print("Original Question:")
#     print(question)

#     print("\nRewritten Question:")
#     print(rewritten_question)

#     print("\nExtracted Filter:")
#     print(filter_dict)

#     print("=" * 60)
    
#     results = retriever.invoke(rewritten_question)
#     print("\nRetrieved Documents:\n")

#     for i, doc in enumerate(results, 1):
#         print(f"----- Document {i} -----")
#         print(doc.page_content)
#         print(doc.metadata)
#         print()

#     # Inject missing provider plans to guarantee completeness for comparisons
#     if force_all_providers:

#         represented_providers = set()
#         for doc in results:
#             if hasattr(doc, 'metadata') and 'provider' in doc.metadata:
#                 represented_providers.add(doc.metadata['provider'].lower())

#         missing_plans = get_missing_provider_plans(represented_providers)

#         if missing_plans:
            
#             results.extend(build_document(missing_plans))

#     context = "\n".join(doc.page_content for doc in results)

#     # Prompt LLM to formulate the final answer using only retrieved information
#     prompt = ChatPromptTemplate.from_template(
#         """
#         You are a telecom assistant
#         You are a friendly and helpful assistant for The Call Company, 
#         a UK mobile phone plan provider.
#         We have three providers: Fone, Gap, and Flipper. 
#         If the user asks for the best plan from each provider, recommend one plan from Fone, Gap, and Flipper.
#         Help customers find the best plan for their needs. 
#         If the user asks for another plan from the same provider, list at least two other plans from that provider”

            
#     You MUST answer ONLY using the plans in the context.

#     Rules:

#       Never invent providers.
#       Never invent plans.
#       Never mention EE, O2, Vodafone or Three.
#       The only providers are:
#       Fone
#       Gap
#       Flipper

#     If no plan matches exactly:

#       Recommend the closest plans.
#       Explain which requirements matched.
#       Explain which requirements did not match.

#     If multiple plans are similar:

#       Sort them by best overall match.

#         {context}
#         Question:
#         {question}
#         """
#     )

#     chain = prompt | get_llm()
#     print("=" * 60)
#     print(context)
#     print("=" * 60)

#     response = chain.invoke({
#         "context": context,
#         "question": rewritten_question,
#     })
    
#     # Save current messages to the persistent user history
#     history.add_user_message(question)
#     history.add_ai_message(response.content)

#     return jsonify({"response": response.content})
