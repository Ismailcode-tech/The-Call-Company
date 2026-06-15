from . import payment_bp
from flask import request, jsonify, session
from flask_login import login_required, current_user
from website.payment.services import confirm_payment
@payment_bp.route('/pay', methods=['POST'])
@login_required
def pay():
    data        = request.get_json()
    card_number = data.get('card_number')
    expiry      = data.get('expiry')     
    cvc         = data.get('cvc')
    plan_id     = data.get('plan_id')
    ok, result = confirm_payment(
        card_number = card_number,
        expiry      = expiry,
        cvc         = cvc,
        plan_id     = plan_id,
        member_id   = current_user.id
    )
    if ok == False:
        return jsonify({'error': result}), 400
    return jsonify({
        'message':   'Payment successful!',
        'reference': result
    }), 200
