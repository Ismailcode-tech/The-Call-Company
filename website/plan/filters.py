
from flask_sqlalchemy import query
from ..models import NetworkProvider, Plan
from sqlalchemy import or_, and_, func


# Calculates the total cost of the plan over a standard 24-month contract period.
def calculate_two_year_cost(monthly_price):
    return monthly_price * 24

# Filters the database of mobile plans based on the user's selected criteria.
# Returns a list of Plan objects that match all provided filters.
def filter_plans(providers=None, plan_type=None, budget=None, data=None, brand=None, calls=None):

    # Start with a base query joining Plans with NetworkProviders so we can filter by provider name
    query = Plan.query.join(NetworkProvider)

    # 1. Filter by Provider (Fone, Gap, Flipper)
    if providers:
        provider_list = [p.strip() for p in providers.split(",")]
        # Match against the lowercase provider name in the database
        query = query.filter(func.lower(NetworkProvider.name).in_(provider_list))

    # 2. Filter by Plan Type (SIM Only or With Phone)
    if plan_type and plan_type != "all":
        if plan_type == "sim":
            # SIM only plans do not have a phone included (it is None)
            query = query.filter(Plan.phone_included.is_(None))
        elif plan_type == "phone":
            # Phone plans must have a phone model specified
            query = query.filter(Plan.phone_included.isnot(None))

    # 3. Filter by Maximum Monthly Budget
    if budget:
        # Ensure the monthly price is less than or equal to the user's budget
        query = query.filter(Plan.monthly_price <= float(budget))

    # 4. Filter by Data Allowance (5GB, 100GB, Unlimited)
    if data:
        data_values = [d.strip() for d in data.split(",")]
        conditions = []

        for d in data_values:
            d_float = float(d)
            if d_float == -1:
                # -1 is used as a special value to represent "Unlimited" data
                conditions.append(Plan.unlimited_data.is_(True))
            else:
                # Otherwise match the exact GB amount
                conditions.append(Plan.data_gb == d_float)

        # Apply an OR condition so any of the selected data amounts will match
        query = query.filter(or_(*conditions))

    # 5. Filter by Phone Brand (Apple or Samsung)
    if brand and brand != "any":
        if brand == "apple":
            # Search for 'iPhone' anywhere in the phone_included string
            query = query.filter(Plan.phone_included.ilike("%iPhone%"))
        elif brand == "samsung":
            # Search for 'Samsung' anywhere in the phone_included string
            query = query.filter(Plan.phone_included.ilike("%Samsung%"))

    # 6. Filter by Calls & Texts Allowance (Limited or Unlimited)
    if calls and calls != "any":
        if calls == "unlimited":
            # Both calls and texts must explicitly be set to 'unl' (unlimited)
            query = query.filter(Plan.calls == "unl", Plan.texts == "unl")
        elif calls == "limited":
            # For limited plans, calls/texts cannot be 'unl' and they must have a value (not None)
            query = query.filter(
                and_(
                    Plan.calls != "unl",
                    Plan.texts != "unl",
                    Plan.calls.isnot(None),
                    Plan.texts.isnot(None)
                )
            )

    # Execute the query and return the matching Plan objects
    return query.all()



# Transforms the SQLAlchemy Plan objects into a list of dictionaries.
# This formats the data perfectly for the frontend API response.
def format_results(Plans):
    results = []
    for plan in Plans:

        # Extract the phone brand based on the phone model string
        if plan.phone_included and "iPhone" in plan.phone_included:
            phone_brand = "apple"
        elif plan.phone_included and "Samsung" in plan.phone_included:
            phone_brand = "samsung"
        else:
            phone_brand = None

        # Determine how to display the data allowance
        if plan.unlimited_data:
            data = -1
            data_label = "Unlimited"
        elif plan.data_gb is None:
            data = 0
            data_label = "No SIM"
        else:
            data = float(plan.data_gb)
            data_label = f"{plan.data_gb}GB"


        # Categorize the plan into a pricing tier based on what it includes
        if plan.phone_included and (plan.unlimited_data or plan.data_gb is not None):
            tier = "All-in"      # Includes both a phone and a data plan
        elif plan.phone_included:
            tier = "Just Phone"  # Includes a phone but no sim plan
        else:
            tier = "SIM Only"    # Includes a sim plan but no phone     

        # Build the final dictionary object for the frontend
        results.append({
            "id":               plan.id,
            "provider" :        plan.provider.name.lower(),
            "name" :            plan.name,
            "tier" :            tier,
            "type" :            "phone" if plan.phone_included else "sim",
            "data" :            data,
            "dataLabel" :       data_label,
            "callsTexts" :      "unlimited" if plan.calls == "unl" else "limited",
            "calls" :           plan.calls,
            "texts" :           plan.texts,
            "phoneBrand" :      phone_brand,
            "phoneModel" :      plan.phone_included,
            "monthlyPrice" :    float(plan.monthly_price),
            "contractMonths" :  24, # Standard 24-month contract assumed
            "twoYearCost" :     calculate_two_year_cost(plan.monthly_price)         
        })
    return results


