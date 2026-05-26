from flask import jsonify, make_response
from cerberus import Validator
from datetime import date, datetime as dt, timedelta
from sqlalchemy.exc import SQLAlchemyError
from . import db
from ..models import Member
from tokengeneration import otp, jwtEncode, jwtDecode, get_token_from_header
from emails import send_otp_email


# helper responses to avoid repetition

def success(data, message: str = None, code: int = 200):
    """Returns a standardised success response."""
    data['status'] = 'Success'
    data['message'] = message
    data['success'] = True
    return make_response(jsonify(data), code)


def error(data, message: str, code: int):
    """Returns a standardised error response."""
    data['status'] = 'Error'
    data['message'] = message
    data['success'] = False
    return make_response(jsonify(data), code)


#schemas for formatting the user input

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

verify_schema = {
    'otp': {
        'type': 'string',
        'required': True,
        'minlength': 6
    },
    'email': {
        'type': 'string',
        'required': True
    }
}

refresh_token_schema = {
    'refresh_token': {
        'type': 'string',
        'required': True
    }
}


# functions 

def login_user(data):
    #Logs in a member and returns JWT tokens to remeber the session
    v = Validator(login_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)

    email = data.get('email')
    password = data.get('password')

    member = Member.query.filter_by(email=email).first()
    if not member:
        return error({}, 'No account found with that email', 404)

    if not member.check_password(password):
        return error({}, 'Incorrect password', 401)

    # check if email is verified
    if not member.is_verified:
        return error({}, 'Please verify your email before logging in', 403)

    access_token = jwtEncode(member)
    refresh_token = jwtEncode(member, is_refresh=True)

    return success({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': member.id,
            'fname': member.fname,
            'lname': member.lname,
            'email': member.email,
            'age': member.age
        }
    }, 'Logged in successfully', 200)


def register_user(data):
    #Registers a new member and sends OTP verification email
    v = Validator(register_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)

    email = data.get('email')

    member = Member.query.filter_by(email=email).first()
    if member:
        return error({}, 'You are already a member, try logging in', 409)

    try:
        born = date.fromisoformat(data.get('date_of_birth'))
        today = date.today()
        age = today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )

        # generate otp verification code
        verification_code = otp(6)

        new_member = Member(
            email=data.get('email'),
            fname=data.get('fname'),
            lname=data.get('lname'),
            phone_number=data.get('phone_number'),
            date_of_birth=born,
            age=age,
            otp_code=verification_code,
            is_verified=False
        )
        new_member.set_password(data.get('password'))

        db.session.add(new_member)
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)

    # send otp email, continue even if it fails
    try:
        send_otp_email(new_member)
    except Exception:
        pass

    return success({
        'user': {
            'id': new_member.id,
            'fname': new_member.fname,
            'lname': new_member.lname,
            'email': new_member.email
        }
    }, 'Registration successful, check your email for your OTP verification code', 201)


def verify_account(data):
    #Verifies a member's email using the OTP code
    v = Validator(verify_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)

    otp_code = data.get('otp')
    email = data.get('email')

    member = Member.query.filter_by(email=email).first()
    if not member:
        return error({}, 'No account found with that email', 404)

    if member.is_verified:
        return error({}, 'Account already verified', 400)

    # check if otp matches
    if member.otp_code != otp_code:
        return error({}, 'Invalid OTP code', 401)

    try:
        member.is_verified = True
        member.otp_code = None      # clear otp after verification
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)

    #There are two types of tokens: access tokens after the user logs in for the first time and refresh tokens to go back to the session after the access token expires
    access_token = jwtEncode(member)
    refresh_token = jwtEncode(member, is_refresh=True)

    return success({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': member.id,
            'fname': member.fname,
            'lname': member.lname,
            'email': member.email,
            'age': member.age
        }
    }, 'Email verified successfully, welcome to The Call', 200)


def refresh_token(data):
    #Generates a new access token using a valid refresh token."""
    v = Validator(refresh_token_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)

    token = data.get('refresh_token')

    # decode the refresh token
    payload = jwtDecode(token)
    if not payload:
        return error({}, 'Token expired or invalid, please login again', 401)

    # make sure it is a refresh token not an access token
    if payload.get('type') != 'refresh':
        return error({}, 'Invalid token type', 401)

    member = Member.query.get(payload.get('sub'))
    if not member:
        return error({}, 'User not found', 404)

    # generate new access token
    new_access_token = jwtEncode(member)

    return success({
        'access_token': new_access_token
    }, 'Token refreshed successfully', 200)


def logout_user():
    """Logs out the current user by marking them as logged out."""
    token = get_token_from_header()

    if not token:
        return error({}, 'No token provided', 401)

    payload = jwtDecode(token)
    if not payload:
        return error({}, 'Invalid or expired token', 401)

    member = Member.query.get(payload.get('sub'))
    if not member:
        return error({}, 'User not found', 404)

    try:
        member.is_logged_out = True
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)

    return success({}, 'Logged out successfully', 200)


def resend_otp(data):
    """Resends a new OTP code to the member's email."""
    email = data.get('email')
    if not email:
        return error({}, 'Email is required', 400)

    member = Member.query.filter_by(email=email).first()
    if not member:
        return error({}, 'No account found with that email', 404)

    if member.is_verified:
        return error({}, 'Account already verified', 400)

    try:
        member.otp_code = otp(6)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)

    try:
        send_otp_email(member)
    except Exception:
        pass

    return success({}, 'New OTP code sent to your email', 200)

"""
This is the javascript function to delete the session token from the local stotage which logs the user out
 
async function logout() {
    const token = localStorage.getItem('access_token')

    if (!token) {
        // no token found, just redirect
        window.location.href = 'login.html'
        return
    }

    try {
        // tell backend to mark user as logged out
        const response = await fetch('http://localhost:5000/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })

        const data = await response.json()
        console.log(data.message)

    } catch (error) {
        console.error('Logout failed:', error)

    } finally {
        // always delete tokens and redirect, even if backend call fails
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = 'login.html'
    }
}
"""
    



	
	


          





    
