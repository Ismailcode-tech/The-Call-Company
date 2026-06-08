from flask import jsonify, make_response, current_app, request
from cerberus import Validator
from datetime import date, datetime as dt, timedelta
from sqlalchemy.exc import SQLAlchemyError
from website import db
from website.models import Member, RefreshToken
from .tokengeneration import (otp, jwtEncode, jwtDecode, set_auth_cookies, clear_auth_cookies)
from .emails import send_otp_email


def success(data, message: str = "", code: int = 200):
    #Returns a standardised success response.
    if not isinstance(data, dict):
        data = {'data': data}
    data['status'] = 'Success'
    data['success'] = True
    if message:
        data['message'] = message
    return make_response(jsonify(data), code)



def error(data, message: str, code: int):
    """Returns a standardised error response."""
    data['status'] = 'Error'
    data['message'] = message
    data['success'] = False
    return make_response(jsonify(data), code)


#the purpose of this function is to format the Member model in the database to match the user interface
#and display readable values
def format_user_response(member):
    """Formats a Member object to match the frontend User interface."""
    #formates the created_at timestamp into a human readaable date
    member_since = member.created_at.strftime("%b %Y") if member.created_at else ""
    is_under_18 = member.age < 18 if member.age is not None else False
    
    # Try to find an active membership ID
    membership_id = ""
    active_membership = next((m for m in member.memberships if m.status == 'active'), None)
    if active_membership:
        membership_id = str(active_membership.membership_id)
        
    return {
        'id': str(member.id),
        'fname' : member.fname,
        'lname' : member.lname,
        'email': member.email,
        'dateOfBirth': member.date_of_birth.isoformat() if member.date_of_birth else "",
        'membershipId': membership_id,
        'memberSince': member_since,
        'isUnder18': is_under_18
    }


#schemas for formatting the user input

login_schema = {
    #we can log in either using the email or the membership id
    'emailOrId': {
        'type': 'string',
        'required': True
    },
    # 'email': {
    #     'type': 'string',
    #     'required': True,
    #     'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    # },
    'password': {
        'type': 'string',
        'required': True,
        'minlength': 6
    }
}
#here I used first name and last name instead of full name as it is more convinient
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
        'required': False,
        'regex': r'^\d{4}-\d{2}-\d{2}$'
    }
}

verify_schema = {
    'otp_code': {
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
    """Logs in a member by validating credentials and determining if 2FA code is needed."""
    v = Validator(login_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)
    
    email_or_id = data.get('emailOrId') or data.get('email')
    password = data.get('password')

    if not email_or_id:
        return error({}, 'Email or ID is required', 400)
    
    member = None
    #check if it is an email or the membership id
    if '@' in email_or_id:
        #if it is an email, get the email from the members table in the database
        member = Member.query.filter_by(email=email_or_id).first()
    else:
        if email_or_id.isdigit():
            member = db.session.get(Member, int(email_or_id))
        if not member:
            # Fallback check against memberships table
            from website.models import Membership
            m_record = Membership.query.filter_by(membership_id=email_or_id).first()
            if m_record:
                member = db.session.get(Member, m_record.member_id)


    if not member:
        return error({}, 'No account found with that email or ID', 404)
    

    if not member.check_password(password):
        return error({}, 'Incorrect password', 401)
 
    #Here I have implemented a 2 factor authentication on login
    try:
        verification_code = otp(6)
        member.verification_code = verification_code
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)
    

    try:
        send_otp_email(member)
    except Exception:
        pass
    return jsonify({
        'requires2FA': True,
        'email': member.email
    }), 200

def register_user(data):
    #Registers a new member and sends OTP verification email
    v = Validator(register_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)

    email = data.get('email')
    fname = data.get('fname', '')
    lname = data.get('lname', '')

    if not fname or not lname:
        return error({}, 'First name and Last Name are required ', 400)

    DoB = data.get('date_of_birth')
    if not DoB:
        return error({}, 'Date of birth is required', 400)
    

    member = Member.query.filter_by(email=email).first()
    if member:
        return error({}, 'You are already a member, try logging in', 409)

    try:
        born = date.fromisoformat(data.get('date_of_birth'))
        today = date.today()
        age = today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )

        # generate otp verification code of 6 alphanumeric values
        verification_code = otp(6)

        new_member = Member(
            email=data.get('email'),
            fname=data.get('fname'),
            lname=data.get('lname'),
            phone_number=data.get('phone_number'),
            date_of_birth=born,
            age=age,
            verification_code=verification_code,
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
    'member': {
        'email': new_member.email
    }
}, 'Registration successful, check your email for your OTP verification code', 200)



def verify_account(data):
    #Verifies a member's email using the OTP code
    v = Validator(verify_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)

    code = data.get('otp_code')
    email = data.get('email')

    member = Member.query.filter_by(email=email).first()

    if not member:
        return error({}, 'No account found with that email', 404)

    if not member.verification_code or member.verification_code != code:
        return error({}, 'Invalid verification code', 401)

    

    try:
        if not member.is_verified:
            member.is_verified = True
        member.verification_code = None      # clear otp after verification
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)


    access_token = jwtEncode(member, is_refresh= False)
    refresh_token = jwtEncode(member, is_refresh=True)

    try:
        # Clear any existing tokens for this member and save the new refresh token
        RefreshToken.query.filter_by(member_id=member.id).delete()
        
        expire_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
        expired_at = dt.utcnow() + expire_delta
        
        db_token = RefreshToken(
            token=refresh_token,
            member_id=member.id,
            expired_at=expired_at
        )
        db.session.add(db_token)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)
    user_res = format_user_response(member)
    response = make_response(jsonify(user_res), 200)
    set_auth_cookies(response, access_token, refresh_token)
    return response


def refresh_token():
    #Generates a new access token using a valid refresh token cookie.
    token = request.cookies.get('refresh_token')
    if not token:
        return error({}, 'Refresh token is missing, please login again', 401)

    # decode the refresh token
    payload = jwtDecode(token)
    if not payload or payload.get('type') != 'refresh':
        return error({}, 'Token expired or invalid, please login again', 401)

    # Verify token exists in database and is not expired
    db_token = RefreshToken.query.filter_by(token=token).first()
    if not db_token or db_token.expired_at < dt.utcnow():
        if db_token:
            db.session.delete(db_token)
            db.session.commit()
        return error({}, 'Session expired or invalid, please login again', 401)

    member = db.session.get(Member, payload.get('sub'))
    if not member:
        return error({}, 'Member not found', 404)

    # generate new access token
    new_access_token = jwtEncode(member)

    user_res = format_user_response(member)
    response = make_response(jsonify(user_res), 200)
    
    # Update access token cookie
    access_expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
    response.set_cookie(
        'access_token',
        new_access_token,
        max_age=int(access_expires.total_seconds()),
        httponly=True,
        secure=True,
        samesite='Lax',
        path='/'
    )
    return response


def logout_user():
    #Logs out the current user by clearing cookies and deleting the refresh token fromt he database
    token = request.cookies.get('refresh_token')
    if token:
        try:
            #delete token from the database
            RefreshToken.query.filter_by(token=token).delete()
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()

    response = make_response(jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200)
    clear_auth_cookies(response)
    return response


#Resends a new OTP code to the member's email when the user clicks on resend code.
def resend_otp(data):
    
    email = data.get('email')
    if not email:
        return error({}, 'Email is required', 400)
    member = Member.query.filter_by(email=email).first()
    if not member:
        return error({}, 'No account found with that email', 404)
    
    if member.is_verified:
        return error({}, 'Account already verified', 400)
    try:
        member.verification_code = otp(6)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)
    try:
        send_otp_email(member)
    except Exception:
        pass
    return success({}, 'New OTP code sent to your email', 200)


    



	
	


          





    
