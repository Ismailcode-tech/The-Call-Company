import enum
from flask import Blueprint, request, jsonify, session
from website import db
from website.models import NetworkProvider, Plan, Membership
from payment_validation import validate_card
import uuid
import datetime
payment_bp = Blueprint('payment', __name__)
@payment_bp.route('/select-plan', methods=['POST'])
def select_plan():
    data = request.get_json()
    plan_name = data['plan']
    age = data['age']()
    if age < 18:
        if Plan.monthly_price > 15:
            return jsonify({'error': 'This plan is too expensive for under 18s'}), 400
        session['age_restricted'] = True
        session['spending_cap'] = 15
    else:
        session['age_restricted'] = False
        session['spending_cap'] = None
    session['plan_id'] = Plan.id
    session['plan_name'] = Plan.name
    session['price'] = Plan.monthly_price
    return jsonify({'message': 'Plan saved!'})
@payment_bp.route('/checkout', methods=['POST'])
