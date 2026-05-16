# plan/recommendations.py
from models import Plan


def normalize(v):
    return float('inf') if v == 'unl' else int(v)


def calculate_two_year_cost(monthly_price):
    return float(monthly_price) * 24


def get_best_offer(path, brand, data, calls, priority, budget):
    offers = Plan.query.all()
    filtered = []

    for offer in offers:

        # 1. filter by type
        if path == "sim" and offer.phone_included:
            continue
        if path == "phone" and not offer.phone_included:
            continue
        if path == "both" and not offer.phone_included:
            continue

        # 2. filter by brand
        if brand and brand != "any" and path in ["phone", "both"]:
            if offer.phone_included and brand.lower() not in offer.phone_included.lower():
                continue

        # 3. filter by data
        if data is not None:
            data = float(data)
            if data == -1:
                if not offer.unlimited_data:
                    continue
            elif data == 1:
                if offer.data_gb is None or offer.data_gb > 1:
                    continue
            elif data <= 5:
                if offer.data_gb is None or offer.data_gb > 5:
                    continue
            elif data >= 35:
                if offer.data_gb is None or offer.data_gb < 35:
                    continue

        # 4. filter by calls & texts
        if calls is not None:
            calls = int(float(calls))
            if calls == -1:
                if offer.calls != "unl" or offer.texts != "unl":
                    continue
            elif calls == 500:
                if normalize(offer.calls) < 500:
                    continue
            elif calls == 750:
                if normalize(offer.calls) < 750:
                    continue

        # 5. filter by priority
        if priority == "unlimited":
            if offer.calls != "unl" or offer.texts != "unl":
                continue

        # 6. filter by budget
        if budget is not None:
            if offer.monthly_price > float(budget):
                continue

        filtered.append(offer)

    # 7. sort after the loop
    if priority == "price":
        filtered.sort(key=lambda x: x.monthly_price)
    elif priority == "data":
        filtered.sort(
            key=lambda x: x.data_gb if x.data_gb is not None else float('inf'),
            reverse=True
        )
    else:
        filtered.sort(key=lambda x: x.monthly_price)

    return filtered


def format_results(filtered):
    results = []
    for r in filtered:

        # calculate phone_brand from phone_included
        if r.phone_included and "iPhone" in r.phone_included:
            phone_brand = "apple"
        elif r.phone_included and "Samsung" in r.phone_included:
            phone_brand = "samsung"
        else:
            phone_brand = None

        results.append({

            "id":               r.id,
            "provider" :        r.provider.name.lower(),
            "name" :            r.name,
            "tier" :            r.tier,
            "type" :            "phone" if r.phone_includedd else "sim",
            "data" :            float(r.data_gb) if not r.unlimited_data else -1,
            "dataLabel" :       "Unlimited" if r.unlimited_data else f"{r.data_gb}GB",
            "callsTexts" :      "unlimited" if r.calls == "unl" else "limited",
            "calls" :           r.calls,
            "texts" :           r.texts,
            "phoneBrand" :      phone_brand,
            "phoneModel" :      r.phone_includedd,
            "monthlyPrice" :    float(r.monthly_price),
            "contractMonths" :  24,
            "twoYearCost" :    calculate_two_year_cost(r.monthly_price)
        })
    return results


