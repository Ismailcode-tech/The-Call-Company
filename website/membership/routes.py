from . import membership_bp
from flask import jsonify, request
from flask_login import login_required, current_user
from website.membership.services import (
    activate_membership_service,
    get_current_membership,
    get_membership_history
@membership_bp.route('', methods=['GET'])
@login_required
def getMembership():
    membership = get_current_membership(current_user.id)
    return jsonify(membership), 200
@membership_bp.route('/activate', methods=['POST'])
@login_required
def activate_membership():
    data    = request.get_json()
    plan_id = data.get('plan_id')
    if not data or not plan_id:
        return jsonify({'error': 'plan_id is required'}), 400
    ok, result = activate_membership_service(current_user.id, plan_id)
    if ok == False:
        return jsonify({'error': result}), 400
    return jsonify({
        'message':       'Membership activated',
        'membership_id': result
    }), 200
