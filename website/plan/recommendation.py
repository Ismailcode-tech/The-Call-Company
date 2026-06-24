
from ..models import Plan, NetworkProvider
from sqlalchemy import or_, and_
import math


def calculate_two_year_cost(monthly_price):
    if monthly_price is None:
        return 0
    return float(monthly_price) * 24



# light filter — only removes clearly wrong plans 
def build_base_query(path, budget, just_phone=False, under18 = False):
    query = Plan.query.join(NetworkProvider)

    # type filter
    if just_phone:
        query = query.filter(Plan.phone_included.isnot(None), Plan.data_gb.isnot(None), Plan.unlimited_data.is_(False))



    elif path == "both":
        query = query.filter(Plan.phone_included.isnot(None), or_(Plan.data_gb.isnot(None),Plan.unlimited_data.is_(True)))


    elif path == "sim":
        query = query.filter(Plan.phone_included.is_(None))


    if budget:
        query = query.filter(
            Plan.monthly_price <= float(budget)
        )

    if under18:
        query = query.filter(Plan.monthly_price <= 15)





    

    return query





def data_score(plan, user):
    if user["data"] is None:
        return 0

    required = float(user["data"])
    if required == -1:
        return 10 if plan.unlimited_data else 0

    if plan.data_gb is None:
        return 0
    
    actual = float(plan.data_gb)

    if actual >= required:
        return 10

    diff = abs(actual - required)

    return 10 * math.exp(-diff / required)
    




def pric_score(plan, user):
    if not user["budget"]:
        return 0

    if plan.monthly_price is None:
        return 0

    budget = float(user["budget"])
    price = float(plan.monthly_price)

    if price < budget:
        return 10 * math.exp(-price / budget)

    return 0
    


def calls_score(plan, user):
    if not user["calls"]:
        return 0
    
    try:
        required = float(user["calls"])

        if required == -1:
            return 10 if plan.calls == "unl" else 0
        # if plan.calls == "unl":
        #     return 10
        actual = float(plan.calls)

        if actual >= required:
            return 10

        diff = abs(actual - required)

        return 10 * math.exp(-diff / required)

    except:
        return 0 








def score_plan(plan, user, priority):
    data = data_score(plan, user)
    price = pric_score(plan, user)
    calls = calls_score(plan, user)

    score = data + price + calls


    if priority == "data":
        score += data * 0.5

    if priority == "price":
        score += price * 0.5
    if priority == "calls":
        score += calls * 0.5

    return score







    









#  main recommendation function 
def get_recommended_plans(
    path,
    brand,
    data,
    calls,
    priority,
    budget,
    just_phone = False,
    isUnder18 = False
    
):
    query = build_base_query(path, budget, just_phone, isUnder18)

   
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
        "priority": priority
    }

    # score and rank
    scored = [(p, score_plan(p, user, priority)) for p in plans] # list of (plan, score) tuples list comprehensions 
    scored.sort(key=lambda x: x[1], reverse=True)

    results = [p for p, s in scored[:3]]

    # fallback — never return empty
    if len(results) == 0:
        return fallback_recommendation(user, priority)

    return results

       


#  fallback  always returns something
def fallback_recommendation(user, priority):
    query = Plan.query

    # very soft budget limit
    if user["budget"]:
        query = query.filter(
            Plan.monthly_price <= float(user["budget"]) * 1.5
        )

    plans = query.all()

    # score with reduced weight
    scored = [(p, score_plan(p, user, priority)) for p in plans]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [p for p, s in scored[:3]]  




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
































