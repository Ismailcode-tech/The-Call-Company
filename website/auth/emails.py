from . import mail
from flask_mail import Message

def send_registration_email(member):
    msg = Message(
        subject='Welcome to The Call',
        sender='your@gmail.com',
        recipients=[member.email]
    )
    msg.body = f'''
    Hi {member.fname} {member.lname},

    Welcome to The Call! Your account has been created successfully.

    You can now log in and browse our plans from Fone, Gap, and Flipper.

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

    