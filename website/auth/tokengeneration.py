from website import db
from website.models import Member
import jwt
import random
import string
from flask import current_app, request
from datetime import datetime, timedelta
"""
since we are using JWT, in the config.py file you should enclude the following:

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)    # token expires after 1 hour
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days = 30)
	ALGORITHM = "HS256"
	
    in the .env:
    JWT_SECRET_KEY= random secret key



"""

# This function creates an access token and stores the data of the user in the payload (the jwt code)
def jwtEncode(member: Member, is_refresh=False) -> str:
    jwt_secret = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'fallback_secret_key'
    
    if is_refresh:
        expire = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    else:
        expire = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        
    payload = {
        'sub': member.id,
        'type': 'refresh' if is_refresh else 'access',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expire
    }
    
    
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    return jwt.encode(payload, jwt_secret, algorithm=algorithm)



def jwtDecode(token) -> dict:
    jwt_secret = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'fallback_secret_key'
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[algorithm])
        member = db.session.get(Member, payload.get('sub'))
        
        if not member:
            return None
        
        return payload
    
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    

# generate a random and unique one time passcode to verify the member's email
def otp(total):
    return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=total)))


def set_auth_cookies(response, access_token, refresh_token):
    #Sets the access and refresh tokens in secure HTTP-only cookies.
    access_expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
    refresh_expires = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    
    response.set_cookie(
        'access_token',
        access_token,
        max_age=int(access_expires.total_seconds()),
        # Prevents XSS attacks
        httponly=True,
        secure=True,
        samesite='Lax',
        path='/'
    )
    response.set_cookie(
        'refresh_token',
        refresh_token,
        max_age=int(refresh_expires.total_seconds()),
        httponly=True,
        secure=True,
        samesite='Lax',
        path='/'
    )


def clear_auth_cookies(response):
    #Clears both access and refresh token cookies.
    response.set_cookie(
        'access_token',
        '',
        max_age=0,
        expires=0,
        httponly=True,
        secure=True,
        samesite='Lax',
        path='/'
    )
    response.set_cookie(
        'refresh_token',
        '',
        max_age=0,
        expires=0,
        httponly=True,
        secure=True,
        samesite='Lax',
        path='/'
    )


from functools import wraps
from flask import g, jsonify

def token_required(f):
    #Decorator to require a valid access token stored in the request cookies, we place this decorator before every route for extra protection and security
    @wraps(f)
    def decorated(*args, **kwargs):
        #checks if the access token is valid
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({'success': False, 'message': 'Authentication token is missing'}), 401
        
        payload = jwtDecode(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({'success': False, 'message': 'Token is invalid or expired'}), 401
        
        #fetches the records of the memeber from the database and save it as a flask global object so that the route can use it
        member = db.session.get(Member, payload.get('sub'))
        if not member:
            return jsonify({'success': False, 'message': 'Member not found'}), 401
        
        g.current_member = member
        return f(*args, **kwargs)
    return decorated
