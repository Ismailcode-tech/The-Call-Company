from flask import jsonify
from flask_login import login_user as flask_login_user, logout_user as flask_logout_user
from cerberus import Validator
from datetime import date
from ...models import db
from ..models import Member

# define the schema of the email and password entered by the user
login_schema = {
    'email': {
        'type': 'string',
        'required': True,
        'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    },
    'password': {
        'type': 'string',
        'required': True,
        'minlength': 6
    }
}

def login_user(data):
    # validate input: It checks if the data entered by the user is the correct format before even going to the database
    v = Validator(login_schema)
    if not v.validate(data):
        return jsonify({'success': False, 'message': 'Validation failed', 'errors': v.errors}), 400


    email = data.get('email')
    password = data.get('password')

    # check if user exists
    member = Member.query.filter_by(email=email).first()
    if not member:
        return jsonify({'success': False, 'message': 'No account found with that email'}), 404

    # check if password is correct
    if not member.check_password(password):
        return jsonify({'success': False, 'message': 'Incorrect password'}), 401

    #user has successfuly logged in and flask starts a session for them
    flask_login_user(member)

    return jsonify({ #this sends a response to the frontend
        'success': True,
        'message': 'Logged in successfully',
        'user': {
            'id': member.id,
            'fname': member.fname,
            'lname': member.lname,
            'email': member.email,
            'age': member.age
        }
    }), 200