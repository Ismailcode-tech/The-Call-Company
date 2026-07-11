from flask import request, jsonify
from flask_login import login_required
from . import payment_bp
from .services import confirm_payment


#  POST /api/payment/confirm 
@payment_bp.route("/confirm", methods=["POST"])
@login_required
def confirm():
    data = request.get_json()

    plan_id     = data.get("planId")
    card_number = data.get("cardNumber")
    expiry      = data.get("expiry")
    cvv         = data.get("cvv")

    if not all([plan_id, card_number, expiry, cvv]):
        return jsonify({
            "ok":    False,
            "error": "All fields are required"
        }), 400
    clean_card_number = card_number.replace(" ", "")

    result, error = confirm_payment(
        plan_id     = int(plan_id),
        card_number = clean_card_number,
        expiry      = expiry,
        cvv         = cvv,
    )

    if error:
        return jsonify({
            "ok":    False,
            "error": error
        }), 400

    return jsonify(result), 200


