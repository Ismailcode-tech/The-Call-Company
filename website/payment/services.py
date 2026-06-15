import utils.luhn
import datetime
import random
import string
def generate_reference():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return 'CALL-2026-' + random_part
def validate_card(card_number, expiry, cvc):
    errors = []
    card_number = card_number.replace(' ', '')
    if len(card_number) != 16:
        errors.append('Card number must be 16 digits')
    elif not card_number.isdigit():
        errors.append('Card number must only contain numbers')
    elif not utils.luhn.luhn_check(card_number):
        errors.append('Card number is not valid')
    try:
        parts = expiry.replace('-', '/').split('/')
        month = int(parts[0])
        year  = int(parts[1])
        if month < 1 or month > 12:
            errors.append('Month must be between 1 and 12')
        else:
            today         = datetime.date.today()
            current_month = today.month
            current_year  = today.year % 100
            if year < current_year:
                errors.append('This card has expired')
            elif year == current_year and month < current_month:
                errors.append('This card has expired')
    except:
        errors.append('Expiry must be in MM/YY format e.g. 12/26')
    cvc = cvc.strip()
    if len(cvc) != 3:
        errors.append('CVC must be 3 digits')
    elif not cvc.isdigit():
        errors.append('CVC must only contain numbers')

    if len(errors) == 0:
        return True, 'Card is valid'
    else:
        return False, errors
def confirm_payment(card_number, expiry, cvc, plan_id, member_id):
    from website import db
    from website.plan.models import Membership, Plan

    # Step 1: validate the card
    card_ok, result = validate_card(card_number, expiry, cvc)

    # Step 2: if card failed return the errors
    if card_ok == False:
        return False, result
    reference = generate_reference()
    plan = Plan.query.filter_by(id=plan_id).first()
    start_date = datetime.datetime.today()
    end_date   = datetime.datetime(start_date.year + 2, start_date.month, start_date.day)
    new_membership = Membership(
        membership_id       = reference,
        member_id           = member_id,
        plan_id             = plan_id,
        monthly_price       = plan.monthly_price,
        age_restricted      = False,
        spending_cap_active = False,
        spending_cap_amount = None,
        start_date          = start_date,
        end_date            = end_date,
        status              = 'active'
    )
    db.session.add(new_membership)
    db.session.commit()
    return True, reference
