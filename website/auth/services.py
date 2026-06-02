from flask import  jsonify
from flask import jsonify, make_response, current_app
from cerberus import Validator
from datetime import date, datetime as dt, timedelta
from sqlalchemy.exc import SQLAlchemyError
from website import db
from website.models import Member, RefreshToken
from .tokengeneration import otp, jwtEncode, jwtDecode, get_token_from_header
from .emails import send_otp_email



def login_user():
    return jsonify({"message": "Login successful"})


def error(data, message: str, code: int):
    """Returns a standardised error response."""
    data['status'] = 'Error'
    data['message'] = message
    data['success'] = False
    return make_response(jsonify(data), code)



def format_user_response(member):
    """Formats a Member object to match the frontend User interface."""
    member_since = member.created_at.strftime("%b %Y") if member.created_at else ""
    is_under_18 = member.age < 18 if member.age is not None else False
    
    # Try to find an active membership ID
    membership_id = ""
    active_membership = next((m for m in member.memberships if m.status == 'active'), None)
    if active_membership:
        membership_id = str(active_membership.membership_id)
        
    return {
        'id': str(member.id),
        'fullName': f"{member.fname} {member.lname}".strip(),
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
        'required': False
    },
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
    'fullName': {
        'type': 'string',
        'required': False,
        'minlength': 2
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
        born = date.fromisoformat(data.get(DoB))
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

    # Log them in automatically on signup by generating tokens
    access_token = jwtEncode(new_member)
    refresh_token = jwtEncode(new_member, is_refresh=True)
    try:
        expire_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
        expired_at = dt.utcnow() + expire_delta
        
        db_token = RefreshToken(
            token=refresh_token,
            member_id=new_member.id,
            expired_at=expired_at
        )


        db.session.add(db_token)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

    user_res = format_user_response(new_member)
    user_res['accessToken'] = access_token
    user_res['refreshToken'] = refresh_token
    return jsonify(user_res), 201



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
        member.is_verified = True
        member.otp_code = None      # clear otp after verification
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)

    #There are two types of tokens: access tokens after the user logs in for the first time and refresh tokens to go back to the session after the access token expires
    access_token = jwtEncode(member)
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
    user_res['accessToken'] = access_token
    user_res['refreshToken'] = refresh_token
    return jsonify(user_res), 200


def refresh_token(data):
    #Generates a new access token using a valid refresh token."""
    v = Validator(refresh_token_schema)
    if not v.validate(data):
        return error({'errors': v.errors}, 'Validation failed', 400)

    token = data.get('refresh_token')

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

    return success({
        'access_token': new_access_token
    }),200


def logout_user():
    """Logs out the current user by revoking all active refresh tokens in the database."""
    token = get_token_from_header()
    if not token:
        return error({}, 'No token provided', 401)
    payload = jwtDecode(token)
    if not payload:
        return error({}, 'Invalid or expired token', 401)
    member = db.session.get(Member, payload.get('sub'))
    if not member:
        return error({}, 'User not found', 404)
    try:
        # Revoke all active refresh tokens for this user
        RefreshToken.query.filter_by(member_id=member.id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return error({}, str(e), 400)
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200



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
    



	
	


          





    
