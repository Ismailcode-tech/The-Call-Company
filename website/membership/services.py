import datetime
import random
import string
from website import db
from website.membership.models import Membership
from website.plan.models import Plan
from website.auth.models import Member
def generate_membership_id():
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    membership_id = 'CALL-2026-' + random_part
   
  return membership_id
def activate_membership_service(member_id, plan_id):
    # check the plan exists in the database
    plan = Plan.query.filter_by(id=plan_id).first()
    if not plan:
        return False, 'Plan not found'
    existing = Membership.query.filter_by(member_id=member_id, status='active').first()
    if existing:
        return False, 'You already have an active membership'
    user = Member.query.filter_by(id=member_id).first()
    today = datetime.date.today()
    age = today.year - user.dob.year - ((today.month, today.day) < (user.dob.month, user.dob.day))
    under_18 = age < 18
    membership_id = generate_membership_id()
    start_date = datetime.datetime.today()
    end_date   = datetime.datetime(start_date.year + 2, start_date.month, start_date.day)
    new_membership = Membership(
        membership_id       = membership_id,
        member_id           = member_id,
        plan_id             = plan_id,
        monthly_price       = plan.monthly_price,
        age_restricted      = under_18,                    # set to True if under 18
        spending_cap_active = under_18,                    # spending cap on by default for under 18s
        spending_cap_amount = 15.00 if under_18 else None, # £15 cap for under 18s
        start_date          = start_date,
        end_date            = end_date,
        status              = 'active'
    )
    db.session.add(new_membership)
    db.session.commit()
    return True, membership_id
