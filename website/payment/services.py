
import random
import string
from datetime import datetime
from website.models import db, Payment, Plan
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError


def generate_reference():
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(random.choices(chars, k=6))
    return f"PAY-{random_part}"


def validate_card(card_number: str, expiry: str, cvv: str):
    # clean card number
    card_number = card_number.replace(" ", "").replace("-", "")

    #  check length
    if len(card_number) not in [15, 16]:
        return False, "Invalid card number length"

    #  check digits only
    if not card_number.isdigit():
        return False, "Card number must contain only digits"

    #  Luhn algorithm
    total = 0
    reverse = card_number[::-1]
    for i, digit in enumerate(reverse):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    if total % 10 != 0:
        return False, "Invalid card number"

    #  validate expiry format MM/YY
    expiry = expiry.replace(" ", "")
    if "/" not in expiry:
        return False, "Invalid expiry format — use MM/YY"
    parts = expiry.split("/")
    try:
        month = int(parts[0])
        year  = int(parts[1])
    except ValueError:
        return False, "Invalid expiry date"

    #  check month range
    if month < 1 or month > 12:
        return False, "Invalid expiry month"

    #  check not expired
    now       = datetime.utcnow()
    full_year = 2000 + year if year < 100 else year
    if full_year < now.year or (full_year == now.year and month < now.month):
        return False, "Card has expired"

    #  validate CVV
    cvv = cvv.strip()
    if not cvv.isdigit() or len(cvv) not in [3, 4]:
        return False, "Invalid CVV"

    return True, "Valid"


#  1 confirm payment 
def confirm_payment(plan_id: int, card_number: str, expiry: str, cvv: str):

    # validate card first
    valid, message = validate_card(card_number, expiry, cvv)
    if not valid:
        return None, message

    # check plan exists
    plan = Plan.query.get(plan_id)
    if not plan:
        return None, "Plan not found"

    try:
        payment = Payment(
            member_id = current_user.id,
            plan_id = plan_id,
            is_payment_confirmed = True,
            monthly_price = plan.monthly_price,
        )
        
        db.session.add(payment)
        db.session.commit()

        return {
            "ok":          True,
            "planId":      str(plan_id),
            "amount":      float(plan.monthly_price),
            "message":     "Payment confirmed successfully"
        }, None

    except SQLAlchemyError as e:
        db.session.rollback()
        return None, str(e)


#  2 get payment by plan 
def get_payment(plan_id: int):
    return Payment.query.filter_by(
        member_id = current_user.id,
        plan_id = plan_id,
        is_payment_confirmed = True
    ).first()
