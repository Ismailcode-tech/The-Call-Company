from website import db, Member
import jwt
import random
from flask import current_app, request
from datetime import datetime
from flask import request, string
from website import config

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
def jwtEncode(member: Member, is_refresh = False) -> str:
	expire = JWT_REFRESH_TOKEN_EXPIRES if is_refresh else JWT_ACCESS_TOKEN_EXPIRES
	payload = {
            'sub': member.id,
			'type': 'refresh' if is_refresh else 'access',
            'iat': datetime.utcnow(),
            'exp' : datetime.utcnow() + expire
        }
	return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

# this function validates the access token after it has decoded it
def jwtDecode(token) -> dict:
	
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=[ALGORITHM])
        member = Member.query.get(payload.get('sub'))
        
        if not member or member.is_logged_out:
            
            return None

        return payload
    
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


#this function get the session token as a string from the header after requesting an authorization. It is later used to delete the token and log the user out of the session
def get_token_from_header() -> str:
    """Extracts the Bearer token from the Authorization header."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    parts = auth_header.split(' ')
    
    if len(parts) != 2 or parts[0] != 'Bearer':
        return None
    
    return parts[1]
#generate a random and unique one time passcode to verify the member's email
def otp(total):
	return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=total)))

# add error handling functions for expired tokens and invalid tokens