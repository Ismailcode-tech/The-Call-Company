from website import db, Member
import jwt
import random, string
from flask import current_app
from datetime import datetime, timedelta

"""
since we are using JWT, in the config.py file you should enclude the following:

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)    # token expires after 1 hour
	
    in the .env:
    JWT_SECRET_KEY= random secret key



"""

# This function creates an access token and stores the data of the user in the payload (the jwt code)
def jwtEncode(member: Member) -> str:
	payload = {
            'sub': member.id,
            'iat': datetime.utcnow(),
            'exp' : datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
	return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

# this function vaidates the access token after it has decoded it
def jwtDecode(token) -> dict:
	decoded = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")
	return decoded

#generate a random and unique one time passcode to verify the member's email
def otp(total):
	return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=total)))


# add error handling functions for expired tokens and invalid tokens