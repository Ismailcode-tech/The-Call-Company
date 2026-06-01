from flask import current_app
from flask_mail import Message
from website import mail
def send_otp_email(member):
    """Sends an OTP verification code to the member's email."""
    msg = Message(
        subject='Verify your email - The Call',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[member.email]
    )
    msg.body = f'''
Hi {member.fname},
Your verification code is:
{member.verification_code}
Enter this code on the verification page to activate your account.
The Call Team
    '''
    mail.send(msg)
def send_membership_confirmation_email(member, membership):
    """Sends a confirmation email after signing up to a plan."""
    msg = Message(
        subject='Membership Confirmation - The Call',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[member.email]
    )

    
    msg.body = f'''
Hi {member.fname},
Your membership has been confirmed!
Membership ID: {membership.id}
Monthly Price: £{membership.monthly_price}
Start Date: {membership.start_date}
End Date: {membership.end_date}
Status: {membership.status}
The Call Team
    '''
    mail.send(msg)

    