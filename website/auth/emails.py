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

    