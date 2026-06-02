from website.models import Plan

from . import plan_bp

from flask import request, jsonify
from .recommendation import format_results, get_best_offer
from .filters import filterPlan


@plan_bp.route("/recommend", methods=["GET"])
def get_plan():
    path = request.args.get("path")
    brand = request.args.get("brand")
    data = request.args.get("data")
    calls = request.args.get("calls")
    priority = request.args.get("priority")
    budget = request.args.get("budget")
    filtered = get_best_offer(path,brand,data,calls,priority,budget)
    results = format_results(filtered)
    return jsonify(results)



@plan_bp.route("/plans", methods=["GET"])
def get_filtered_plans():
    providers = request.args.get("providers")
    type = request.args.get("type")
    budget = request.args.get("budget")
    data = request.args.get("data")
    brand = request.args.get("brand")
    calls = request.args.get("calls")

    filtered = filterPlan(providers, type, budget, data, brand, calls)

    results = format_results(filtered)
    return jsonify(results)


@plan_bp.route("", methods=["GET"])
@plan_bp.route("/", methods=["GET"])
def all_plans():
    return jsonify(format_results(Plan.query.all()))






    
    




