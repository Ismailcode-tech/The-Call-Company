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

{member.otp_code}

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



    """
    in the .env
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    MAIL_USE_SSL = 'True' == os.environ.get("MAIL_USE_SSL")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    MAIL_DEBUG = 'True' == os.environ.get("MAIL_DEBUG")
    MAIL_SUPPRESS_SEND = False


    
    in the config.py 
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_USERNAME=abc@gmail.com
    MAIL_PASSWORD password here
    MAIL_DEFAULT_SENDER=abc@gmail.com
    MAIL_DEBUG=False


    """

    