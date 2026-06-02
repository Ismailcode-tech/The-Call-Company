
from flask_sqlalchemy import query

from ..models import NetworkProvider, Plan
from sqlalchemy import or_
  
def calculate_two_year_cost(monthly_price):
    return float(monthly_price) * 24

def calculate_two_year_cost(monthly_price):
    return float(monthly_price) * 24

def filterPlan(providers=None, plan_type=None, budget=None, data=None, brand=None, calls=None):
        

        query = Plan.query.join(NetworkProvider)
        if providers:
            provider_list = [p.strip() for p in providers.split(",")]
            query = query.filter(
            NetworkProvider.name.in_([p.capitalize() for p in provider_list])
            )

        if plan_type and plan_type != "all":
            if plan_type == "sim":
                query = query.filter(Plan.phone_included == None)
            elif plan_type == "phone":
                query = query.filter(Plan.phone_included != None)


        if budget:
             query = query.filter(Plan.monthly_price <= float(budget))
        if data:
            data_values = [d.strip() for d in data.split(",")]
            conditions = []

            for d in data_values:
                d_float = float(d)
                if d_float == -1:
                    conditions.append(Plan.unlimited_data == True)
                else:
                     conditions.append(Plan.data_gb == d_float)
            if conditions:
                 query = query.filter(or_(*conditions)) 
        if brand and brand != "any":
            if brand == "apple": 
                query = query.filter(Plan.phone_included.ilike("%iPhone%"))
            elif brand == "samsung":
                 query = query.filter(Plan.phone_included.ilike("%Samsung%"))
        if calls:
            if calls == "unl":
                query = query.filter(Plan.calls == "unl", Plan.texts == "unl")
            elif calls == "limited":
                 query = query.filter((Plan.calls != "unl", Plan.texts != "unl") and (Plan.calls != None, Plan.texts != None))
        Plans =  query.all()


    



def format_results(Plans):
    results = []
    for plan in Plans:

        # calculate phone_brand from phone_included
        if plan.phone_included and "iPhone" in plan.phone_included:
            phone_brand = "apple"
        elif plan.phone_included and "Samsung" in plan.phone_included:
            phone_brand = "samsung"
        else:
            phone_brand = None


        if plan.unlimited_data:
            data = -1
            data_label = "Unlimited"
        elif plan.data_gb is None:
            data = 0
            data_label = "No SIM"
        else:
            data = float(plan.data_gb)
            data_label = f"{plan.data_gb}GB"



        if plan.phone_included and (plan.unlimited_data or plan.data_gb is not None):
            tier = "All-in"
        elif plan.phone_included:
            tier = "Just Phone"
        else:
            tier = "SIM Only"          

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
            "contractMonths" :  24,
            "twoYearCost" :    calculate_two_year_cost(plan.monthly_price)         
        })
    return results




                
             















