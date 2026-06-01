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
# this function validates the access token after it has decoded it
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
# this function gets the session token as a string from the header after requesting an authorization. It is later used to delete the token and log the user out of the session
def get_token_from_header() -> str:
    """Extracts the Bearer token from the Authorization header."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    parts = auth_header.split(' ')
    
    if len(parts) != 2 or parts[0] != 'Bearer':
        return None
    
    return parts[1]
# generate a random and unique one time passcode to verify the member's email
def otp(total):
    return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=total)))