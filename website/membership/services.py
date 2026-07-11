
from datetime import datetime, timedelta
from website.models import Membership, Member, Plan, db
from sqlalchemy.exc import SQLAlchemyError
from website.payment.services import get_payment 
from website.auth.emails import send_membership_confirmation_email
import random


def generate_membership_id():

    while True:
        new_id = random.randint(100000, 999999)  # 6-digit number, never starts with 0
        existing = Membership.query.filter_by(membership_id=new_id).first()
        if not existing:
            return new_id


def activate_membership(member_id, plan_id, spending_cap_amount=None):
 
    try:
        # 1. Fetch the member and selected plan
        member = db.session.get(Member, member_id)

        if not member:
            return False, "Member not found"

        plan = db.session.get(Plan, plan_id)

        if not plan:
            return False, "Selected plan not found"

        payment = get_payment(plan_id)

        if not payment:
            return False, "Membership cannot be activated without payment"

        existing_active = Membership.query.filter_by(
            member_id=member_id,
            status="active"
        ).first()

        if existing_active:
            existing_active.status = "cancelled"

        
        # 3. Create a new unique membership ID
        new_membership_id = generate_membership_id()
        
        # 4. Set start and contract end dates (2 years contract)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=730)


        # 5. Check if age restrictions apply
        age_restricted = member.age < 18 if member.age is not None else False
        
        # 6. Instantiate the new Membership record
        membership = Membership(
            membership_id=new_membership_id,
            member_id=member_id,
            plan_id=plan_id,
            monthly_price=plan.monthly_price,
            spending_cap_active=spending_cap_amount is not None,
            spending_cap_amount=spending_cap_amount,
            age_restricted=age_restricted,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        db.session.add(membership)
        db.session.commit()

        # Send confirmation email that contains membership details.
        try:
            send_membership_confirmation_email(member, membership)
        except Exception:
            pass # Continue even if email sending fails

        return True, {
            "membershipId": str(membership.membership_id),
            "planId": str(membership.plan_id),
            "startedAt": membership.start_date.isoformat(),
            "renewalDate": membership.end_date.isoformat()
        } 

    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)
    

def get_current_membership(member_id):
    """
    Retrieves details of the currently active membership for a member.

    """
    membership = Membership.query.filter_by(member_id=member_id, status='active').first()
    if not membership:
        return None
        
    return {
        "membershipId": str(membership.membership_id),
        "planId": str(membership.plan_id),
        "startedAt": membership.start_date.isoformat(),
        "renewalDate": membership.end_date.isoformat(),
    }


def get_membership_history(member_id):

    memberships = Membership.query.filter_by(member_id=member_id).order_by(Membership.start_date.desc()).all()
    
    history = []
    for m in memberships:
        plan = db.session.get(Plan, m.plan_id)
        history.append({
            "membership_id": str(m.membership_id),
            "plan_name": str(plan.name),
            "startedAt": (
                m.start_date.isoformat()
                if m.start_date
                else None
            ),
            "renewalDate": (
                m.end_date.isoformat()
                if m.end_date
                else None
            ),
            "endedAt": (
                m.end_date.isoformat()
                if m.status != "active"
                else None
            ),
            "planSnapshot": {
                "id": plan.id,
                "name": plan.name,
                "providerId": plan.provider_id,
                "dataGb": float(plan.data_gb)
                if plan.data_gb is not None
                else None,
                "unlimitedData": plan.unlimited_data,
                "calls": plan.calls,
                "texts": plan.texts,
                "phoneIncluded": plan.phone_included,
                "monthlyPrice": float(plan.monthly_price)
            } if plan else None
        })

    return history