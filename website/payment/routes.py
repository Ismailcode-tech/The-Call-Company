from . import payment_bp
from flask import request, jsonify, session
from flask_login import login_required, current_user
from website import db
from website.plan.models import Plan, Membership, Member
from website.payment.services import validate_card
import datetime
@payment_bp.route('/select-plan', methods=['POST'])
@login_required
def select_plan():
    data = request.get_json()
    plan_name = data.get('plan')
    # get age from the logged in user directly
    age = current_user.age
    plan = Plan.query.filter_by(name=plan_name).first()
    if plan is None:
        return jsonify({'error': 'Plan not found'}), 404
    if age < 18:
        if plan.monthly_price > 15:
            return jsonify({'error': 'Under 18s cannot pick plans over £15'}), 400
        session['age_restricted'] = True
        session['spending_cap_active'] = True
        session['spending_cap_amount'] = 15
    else:
        session['age_restricted'] = False
        session['spending_cap_active'] = False
        session['spending_cap_amount'] = None
    session['plan_id'] = plan.id
    session['plan_name'] = plan.name
    session['price'] = float(plan.monthly_price)
    return jsonify({'message': 'Plan saved!'})
@payment_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    card_number = data.get('card_number')
    exp_month = data.get('exp_month')
    exp_year = data.get('exp_year')
    cvc = data.get('cvc')
    # validate card using Luhn + expiry + CVC
    card_ok, result = validate_card(card_number, exp_month, exp_year, cvc)
    if card_ok == False:
        return jsonify({'error': result}), 400
    # generate membership ID
    count = Membership.query.count() + 1
    membership_id = 'CALL-2026-' + str(count).zfill(5)
    # start date = today, end date = 2 years from today
    start_date = datetime.datetime.today()
    end_date = datetime.datetime(start_date.year + 2, start_date.month, start_date.day)
    # create new membership using Celia's exact field names
    new_membership = Membership(
        membership_id        = membership_id,
        member_id            = current_user.id,
        plan_id              = session.get('plan_id'),
        monthly_price        = session.get('price'),
        age_restricted       = session.get('age_restricted', False),
        spending_cap_active  = session.get('spending_cap_active', False),
        spending_cap_amount  = session.get('spending_cap_amount', None),
        start_date           = start_date,
        end_date             = end_date,
        status               = 'active'
    )
    db.session.add(new_membership)
    db.session.commit()
    # clear session
    session.pop('plan_id', None)
    session.pop('plan_name', None)
    session.pop('price', None)
    session.pop('age_restricted', None)
    session.pop('spending_cap_active', None)
    session.pop('spending_cap_amount', None)
    return jsonify({
        'message': 'Payment successful!',
        'membership_id': membership_id
    })
@payment_bp.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    membership_id = data.get('membership_id')
    membership = Membership.query.filter_by(membership_id=membership_id).first()
    if membership is None:
        return jsonify({'error': 'Membership not found'}), 404
    # get member details from Member table
    member = Member.query.filter_by(id=membership.member_id).first()
    plan = Plan.query.filter_by(id=membership.plan_id).first()
    return jsonify({
        'membership_id':  membership.membership_id,
        'name':           member.fname + ' ' + member.lname,
        'plan':           plan.name,
        'price':          float(membership.monthly_price),
        'start_date':     str(membership.start_date),
        'status':         membership.status
    })
@payment_bp.route('/my-membership', methods=['GET'])
@login_required
def my_membership():
    membership = Membership.query.filter_by(member_id=current_user.id).first()
    if membership is None:
        return jsonify({'error': 'No membership found'}), 404
    plan = Plan.query.filter_by(id=membership.plan_id).first()
    return jsonify({
        'membership_id':       membership.membership_id,
        'name':                current_user.fname + ' ' + current_user.lname,
        'plan':                plan.name,
        'price':               float(membership.monthly_price),
        'age_restricted':      membership.age_restricted,
        'spending_cap_active': membership.spending_cap_active,
        'spending_cap_amount': float(membership.spending_cap_amount) if membership.spending_cap_amount else None,
        'start_date':          str(membership.start_date),
        'end_date':            str(membership.end_date),
        'status':              membership.status
    })
