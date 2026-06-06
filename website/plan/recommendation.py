# plan/recommendations.py
from ..models import Plan, NetworkProvider
from sqlalchemy import or_


# weights for scoring
WEIGHTS = {
    "data":        3.0,
    "price":       2.5,
    "calls":       1.5,
    "provider":    1.0,
    "exact_match": 2.0,
    "penalty":     4.0,
}


def calculate_two_year_cost(monthly_price):
    return float(monthly_price) * 24


# light filter — only removes clearly wrong plans 
def build_base_query(path, budget, providers):
    query = Plan.query.join(NetworkProvider)

    # type filter
    if path == "sim":
        query = query.filter(Plan.phone_included.is_(None))
    elif path == "phone":
        query = query.filter(Plan.phone_included.isnot(None))

    # soft budget — allow 30% over budget so scorer can rank
    if budget:
        query = query.filter(
            Plan.monthly_price <= float(budget) * 1.3   #  soft limit
        )


    if providers:
        provider_list = [p.strip().capitalize() for p in providers.split(",")]
        query = query.filter(
            or_(*[NetworkProvider.name == p for p in provider_list])
        )

    return query


# score each plan against user preferences
def score_plan(plan, user):                              
    score = 0

    # data score
    if user["data"] is not None:
        if plan.unlimited_data:
            score += WEIGHTS["data"] * 2               
        elif plan.data_gb is not None:
            diff = float(plan.data_gb) - float(user["data"])
            if diff >= 0:
                score += WEIGHTS["data"]
                score += min(diff * 0.1, 2)
            else:
                score -= abs(diff) * 0.2

    # price score
    if user["budget"]:
        budget = float(user["budget"])
        price  = float(plan.monthly_price)
        if price <= budget:
            score += WEIGHTS["price"] * 2
        else:
            # penalise over-budget plans
            score -= WEIGHTS["penalty"] * (price - budget) * 0.1

    # calls score
    if user["calls"] == "-1":                         #  -1 means unlimited
        if plan.calls == "unl":
            score += WEIGHTS["calls"] * 2
        else:
            score -= 1
    elif user["calls"] and plan.calls:
        try:
            if int(plan.calls) >= int(user["calls"]):
                score += WEIGHTS["calls"]
        except ValueError:
            if plan.calls == "unl":
                score += WEIGHTS["calls"]

    # exact match bonus
    if user["data"] and plan.data_gb:
        if float(user["data"]) == float(plan.data_gb):
            score += WEIGHTS["exact_match"]

    if user["calls"] and plan.calls:
        if str(user["calls"]) == plan.calls:
            score += WEIGHTS["exact_match"]

 
    score = ml_adjust_score(score, plan, user)

    return score


#  small boosts for generally good plans 
def ml_adjust_score(score, plan, user):
    boost = 0
    if float(plan.monthly_price) < 20:
        boost += 0.5
    if user["data"] and float(user["data"]) >= 35:
        if plan.unlimited_data:
            boost += 1.0
    if user["data"] and plan.data_gb:
        if float(plan.data_gb) >= float(user["data"]):
            boost += 0.8
    return score + boost


#  main recommendation function 
def get_recommended_plans(
    path=None,
    brand=None,
    data=None,
    calls=None,
    priority=None,
    budget=None,
    providers=None
):
    query = build_base_query(path, budget, providers)

   
    plans = query.all()

    # filter by brand AFTER loading
    if brand and brand != "any":
        if brand == "apple":
            plans = [p for p in plans if p.phone_included and "iPhone" in p.phone_included]
        elif brand == "samsung":
            plans = [p for p in plans if p.phone_included and "Samsung" in p.phone_included]

    user = {
        "data":   data,
        "calls":  calls,
        "budget": budget,
    }

    # score and rank
    scored = [(p, score_plan(p, user)) for p in plans] # list of (plan, score) tuples list comprehensions 
    scored.sort(key=lambda x: x[1], reverse=True)

    results = [p for p, s in scored]

    # fallback — never return empty
    if len(results) == 0:
        return fallback_recommendation(user)

    return results


#  fallback  always returns something
def fallback_recommendation(user):
    query = Plan.query

    # very soft budget limit
    if user["budget"]:
        query = query.filter(
            Plan.monthly_price <= float(user["budget"]) * 1.5
        )

    plans = query.all()

    # score with reduced weight
    scored = [(p, score_plan(p, user) * 0.7) for p in plans]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [p for p, s in scored]


#  format for frontend 
def format_results(filtered):
    results = []
    for r in filtered:

        if r.phone_included and "iPhone" in r.phone_included:
            phone_brand = "apple"
        elif r.phone_included and "Samsung" in r.phone_included:
            phone_brand = "samsung"
        else:
            phone_brand = None

        if r.phone_included and (r.unlimited_data or r.data_gb is not None):
            tier = "All-in"
        elif r.phone_included:
            tier = "Just Phone"
        else:
            tier = "SIM Only"

        if r.unlimited_data:
            data       = -1
            data_label = "Unlimited"
        elif r.data_gb is None:
            data       = 0
            data_label = "No SIM"
        else:
            data       = float(r.data_gb)
            data_label = f"{r.data_gb}GB"

        results.append({
            "id":             r.id,
            "provider":       r.provider.name.lower(),
            "name":           r.name,
            "tier":           tier,
            "type":           "phone" if r.phone_included else "sim",
            "data":           data,
            "dataLabel":      data_label,
            "callsTexts":     "unlimited" if r.calls == "unl" else "limited",
            "calls":          r.calls,
            "texts":          r.texts,
            "phoneBrand":     phone_brand,
            "phoneModel":     r.phone_included,
            "monthlyPrice":   float(r.monthly_price),
            "contractMonths": 24,
            "twoYearCost":    calculate_two_year_cost(r.monthly_price),
        })
    return results








































# from ..models import Plan, NetworkProvider
# import math
# from sqlalchemy import or_, and_, any_



# WEIGHTS = {
#     "data": 3.0,
#     "price": 2.5,
#     "calls": 1.5,
#     "provider": 1.0,
#     "exact_match": 2.0,
#     "penalty": 4.0
# }


# def calculate_two_year_cost(monthly_price):
#     return float(monthly_price) * 24


# def build_base_query(path, budget, providers):
#     query = Plan.query.join(NetworkProvider)


#     if path == "sim":
#         query = query.filter(Plan.phone_included.is_(None))
    
#     elif path == "phone":
#         query = query.filter(Plan.phone_included.isnot(None))

#     if budget:
#         query = query.filter(Plan.monthly_price <= float(budget))

#     if providers:
#         provider_list = [p.strip().lower() for p in providers.split(",")]
#         query = query.filter(NetworkProvider.name.ilike(any_(provider_list)))

#     return query


# def score_plan(plan, user):
#     score = 0
# # DATA SCORE

#     if user["data"] is not None:
#         if plan.unlimited_data:
#             score += WEIGHTS["data_match"] * 2
#         elif plan.data_gb is not None:
#             diff = plan.data_gb - user["data"]

#             if diff >= 0:
#                 score += WEIGHTS["data_match"]
#                 score += min(diff * 0.1, 2)
#             else:
#                 score -= abs(diff) *0.2    


# # PRICE SCORE

#     if user["budget"]:
#         budget = float(user["budget"])
#         price = float(plan.monthly_price)


#         if price <= budget:
#             score += WEIGHTS["price"] * 2
#         else:
#             score -= WEIGHTS["penalty"] * (price - budget) * 0.1


# # CALLS SCORE

#     if user["calls"] == "unl":
#         if plan.calls == "unl":
#             score += WEIGHTS["calls"] *2
#         else:
#             score -= 1




# # EXACT MATCH BONUS

#     if user["data"] == plan.data_gb:
#         score += WEIGHTS["exact_match"]

#     if user["calls"] == plan.calls:
#         score += WEIGHTS["exact_match"]


#     return score




# def get_recommended_plans(   
#     path=None,
#     brand=None,
#     data=None,
#     calls=None,
#     priority=None,
#     budget=None,
#     providers=None
# ):
#     query = build_base_query(path, budget, providers)
#     plans = query.all()

#     user ={
#         "data": float(data) if data and data != -1 else None,
#         "calls": calls,
#         "budget": budget
#     }
#     scored = [(p, score_plan(p, user)) for p in plans]
#     scored.sort(key=lambda x: x[1], reverse=True)

#     results = [p for p, s in scored]

#     # fallback trigger

#     if len(results) == 0:
#         return fallback_recommendation(user)
    
#     return results





# def fallback_recommendation(user):
#     query = Plan.query

#     if user["budget"]:
#         query = query.filter(Plan.monthly_price <= float(user["budget"]) * 1.3)

#     plans = query.all()

#     scored = [(p, score_plan(p, user) * 0.7) for p in plans]
#     scored.sort(key=lambda x: x[1], reverse=True)

#     return [p for p, s in scored]



# def ml_adjust_score(score, plan, user):
#     boost = 0

#     if plan.monthly_price < 20:
#         boost += 0.5

#     if plan.unlimited_data:
#         boost += 1.0

#     if user["data"] and plan.data_gb:
#         if plan.data_gb >= user["data"]:
#             boost += 0.8

#     return score + boost                 


# def format_results(filtered):
#     results = []
#     for r in filtered:

#         # calculate phone_brand from phone_included
#         if r.phone_included and "iPhone" in r.phone_included:
#             phone_brand = "apple"
#         elif r.phone_included and "Samsung" in r.phone_included:
#             phone_brand = "samsung"
#         else:
#             phone_brand = None

#         if r.phone_included and (r.unlimited_data or r.data_gb is not None):
#             tier = "All-in"
#         elif r.phone_included:
#             tier = "Just Phone"
#         else:
#             tier = "SIM Only"


#         if r.unlimited_data:
#             data = -1
#             data_label = "Unlimited"
#         elif r.data_gb is None:
#             data = 0
#             data_label = "No SIM"
#         else:
#             data = float(r.data_gb)
#             data_label = f"{r.data_gb}GB"        

#         results.append({

#             "id":               r.id,
#             "provider" :        r.provider.name.lower(),
#             "name" :            r.name,
#             "tier" :            tier,
#             "type" :            "phone" if r.phone_included else "sim",
#             "data" :            data,
#             "dataLabel" :       data_label,
#             "callsTexts" :      "unlimited" if r.calls == "unl" else "limited",
#             "calls" :           r.calls,
#             "texts" :           r.texts,
#             "phoneBrand" :      phone_brand,
#             "phoneModel" :      r.phone_included,
#             "monthlyPrice" :    float(r.monthly_price),
#             "contractMonths" :  24,
#             "twoYearCost" :    calculate_two_year_cost(r.monthly_price)
#         })
#     return results


