from . import payment_bp
from flask import request, jsonify, session
from flask_login import login_required, current_user
from website import db
from website.plan.models import Plan, Membership
from website.payment.services import validate_card
import datetime
@payment_bp.route('/select-plan', methods=['POST'])
@login_required
def select_plan():
    data = request.get_json()
    plan_name = data.get('plan')
    age = data.get('age')
    plan = Plan.query.filter_by(name=plan_name).first()
    if plan is None:
        return jsonify({'error': 'Plan not found'}), 404
    if age < 18:
        if plan.monthly_price > 15:
            return jsonify({'error': 'Under 18s cannot pick plans over £15'}), 400
        session['age_restricted'] = True
        session['spending_cap'] = 15
    else:
        session['age_restricted'] = False
        session['spending_cap'] = None
    session['plan_id'] = plan.id
    session['plan_name'] = plan.name
    session['price'] = plan.monthly_price
    return jsonify({'message': 'Plan saved!'})
@payment_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    card_number = data.get('card_number')
    exp_month = data.get('exp_month')
    exp_year = data.get('exp_year')
    cvc = data.get('cvc')
    card_ok, result = validate_card(card_number, exp_month, exp_year, cvc)
    if card_ok == False:
        return jsonify({'error': result}), 400
    count = Membership.query.count() + 1
    membership_id = 'CALL-2026-' + str(count).zfill(5)
    new_member = Membership(
        membership_id = membership_id,
        user_name = current_user.username,
        user_age = current_user.age,
        plan_id = session.get('plan_id'),
        age_restricted = session.get('age_restricted'),
        spending_cap = session.get('spending_cap'),
        date_joined = datetime.date.today()
    )
    db.session.add(new_member)
    db.session.commit()
    session.pop('plan_id', None)
    session.pop('plan_name', None)
    session.pop('price', None)
    session.pop('age_restricted', None)
    session.pop('spending_cap', None)
    return jsonify({'message': 'Payment successful!', 'membership_id': membership_id})
@payment_bp.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    membership_id = data.get('membership_id')
    member = Membership.query.filter_by(membership_id=membership_id).first()
    if member is None:
        return jsonify({'error': 'Membership not found'}), 404
    plan = Plan.query.filter_by(id=member.plan_id).first()
    return jsonify({
        'membership_id': member.membership_id,
        'name': member.user_name,
        'plan': plan.name,
        'price': plan.monthly_price,
        'date_joined': str(member.date_joined)
    })
@payment_bp.route('/my-membership', methods=['GET'])
@login_required
def my_membership():
    member = Membership.query.filter_by(user_name=current_user.username).first()
    if member is None:
        return jsonify({'error': 'No membership found'}), 404
    plan = Plan.query.filter_by(id=member.plan_id).first()
    return jsonify({
        'membership_id': member.membership_id,
        'name': member.user_name,
        'plan': plan.name,
        'price': plan.monthly_price,
        'age_restricted': member.age_restricted,
        'date_joined': str(member.date_joined)
    })
