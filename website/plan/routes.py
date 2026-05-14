from . import plan_bp



@plan_bp.route("/plans", methods=["GET"])
def get_plans():
    return {"plans": ["Basic", "Pro", "Enterprise"]}, 200

