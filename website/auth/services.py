from flask import jsonify
from flask_login import login_user as flask_login_user
from cerberus import Validator
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from . import db
from ..models import Member
from . import send_registration_email


login_schema = {
    'email': {
        'type': 'string',
        'required': True,
        'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    },
    'password': {
        'type': 'string',
        'required': True,
        'minlength': 6
    }
}


register_schema = {
    'email': {
        'type': 'string',
        'required': True,
        'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    },
    'password': {
        'type': 'string',
        'required': True,
        'minlength': 6
    },
    'fname': {
        'type': 'string',
        'required': True,
        'minlength': 2
    },
    'lname': {
        'type': 'string',
        'required': True,
        'minlength': 2
    },
    'phone_number': {
        'type': 'string',
        'required': True,
        'minlength': 10,
        'maxlength': 15
    },
    'date_of_birth': {
        'type': 'string',
        'required': True,
        'regex': r'^\d{4}-\d{2}-\d{2}$'
    }
}


def login_user(data):

    v = Validator(login_schema)

    if not v.validate(data):
        return jsonify({
            'success': False,
            'message': 'Validation failed',
            'errors': v.errors
        }), 400

    email = data.get('email')
    password = data.get('password')

    member = Member.query.filter_by(email=email).first()

    if not member:
        return jsonify({
            'success': False,
            'message': 'No account found with that email'
        }), 404

    if not member.check_password(password):
        return jsonify({
            'success': False,
            'message': 'Incorrect password'
        }), 401

    flask_login_user(member)

    return jsonify({
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


def register_user(data):

    v = Validator(register_schema)

    if not v.validate(data):
        return jsonify({'success': False,'message': 'Validation failed','errors': v.errors}), 400

    email = data.get('email')

    member = Member.query.filter_by(email=email).first()

    if member:
        return jsonify({
            'success': False,
            'message': 'You are already a member, try logging in'
        }), 409

    try:

        born = date.fromisoformat(data.get('date_of_birth'))

        today = date.today()

        age = today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )

        new_member = Member(
            email=email,
            fname=data.get('fname'),
            lname=data.get('lname'),
            phone_number=data.get('phone_number'),
            date_of_birth=born,
            age=age
        )

        new_member.set_password(data.get('password'))

        db.session.add(new_member)
        db.session.commit()

    except SQLAlchemyError as e:

        db.session.rollback()

        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    
    try:
        send_registration_email(new_member)
    except Exception:
        pass


    flask_login_user(new_member)

    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'user': {
            'id': new_member.id,
            'fname': new_member.fname,
            'lname': new_member.lname,
            'email': new_member.email,
            'age': new_member.age
        }
    }), 201
	


          





    
