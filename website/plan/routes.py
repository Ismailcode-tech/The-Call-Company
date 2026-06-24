from website.models import Plan

from . import plan_bp

from flask import request, jsonify
from flask_login import current_user
from .recommendation import format_results as rec_format_results, get_recommended_plans
from .filters import format_results, filter_plans


@plan_bp.route("/recommend", methods=["GET"])
def get_plan():
    path = request.args.get("path")
    brand = request.args.get("brand")
    data = request.args.get("data")
    calls = request.args.get("calls")
    priority = request.args.get("priority")
    budget = request.args.get("budget")
    just_phone = request.args.get("justPhone") == "1"
    birth_year = request.args.get("birthYear")
    isUnder18 = False
    if birth_year:
        try:
            from datetime import datetime
            current_year = datetime.utcnow().year
            isUnder18 = current_year - int(birth_year) < 18
        except ValueError:
            isUnder18 = False
    elif current_user.is_authenticated:
        isUnder18 = current_user.age < 18 if current_user.age else False

    filtered = get_recommended_plans(path, brand, data, calls, priority, budget, just_phone, isUnder18)
    results = rec_format_results(filtered)
    return jsonify({"results": results, "isUnder18": isUnder18}), 200



@plan_bp.route("", methods=["GET"])
def get_plans():
    providers  = request.args.get("providers")
    plan_type  = request.args.get("type")
    budget     = request.args.get("budget")
    data       = request.args.get("data")
    brand      = request.args.get("brand")
    calls      = request.args.get("calls")
    plans = filter_plans(
        providers=providers,
        plan_type=plan_type,
        budget=budget,
        data=data,
        brand=brand,
        calls=calls,
    )
    return jsonify(format_results(plans)), 200


@plan_bp.route("/<int:plan_id>", methods=["GET"])
def get_plan_by_id(plan_id):
    plan = Plan.query.get(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify(format_results([plan])[0]), 200








    
    




