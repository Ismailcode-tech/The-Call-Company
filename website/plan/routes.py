from . import plan_bp

from flask import request, jsonify
from .recommendation import format_results, get_best_offer



@plan_bp.route("/recommend", methods=["GET"])
def get_plans():
    path = request.args.get("path")
    brand = request.args.get("brand")
    data = request.args.get("data")
    calls = request.args.get("calls")
    priority = request.args.get("priority")
    budget = request.args.get("budget")
    filtered = get_best_offer(path,brand,data,calls,priority,budget)
    results = format_results(filtered)
    return jsonify(results)






    
    




