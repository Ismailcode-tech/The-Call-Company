from website import db
from website.models import Member
import jwt
import random
import string
from flask import current_app, request
from datetime import datetime, timedelta


# This function creates an access token and stores the data of the user in the payload (the jwt code)
def jwtEncode(member: Member, is_refresh=False) -> str:
    jwt_secret = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'fallback_secret_key'
    
    if is_refresh:
        expire = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    else:
        expire = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        
    payload = {
        # before it was  'sub': member.id this unacceptable
        'sub': str(member.id),
        'type': 'refresh' if is_refresh else 'access',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expire
    }
    
    
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    return jwt.encode(payload, jwt_secret, algorithm=algorithm)

#generate a reset token for the password reset logic that expires within 15 minutes
def generate_reset_token(member: Member):
    jwt_secret = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'fallback_secret_key'
    
    # Set the reset link expiration to 15 minutes
    expire = timedelta(minutes=15)
        
    payload = {
        'sub': str(member.id),
        'type': 'reset',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expire,
        'current_pass': member.password_hash
    }
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    return jwt.encode(payload, jwt_secret, algorithm=algorithm)

#slightly modified token decoding logic
def jwtDecode(token) -> dict:
    jwt_secret = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'fallback_secret_key'
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[algorithm])
        
        # Look up the member by their ID (primary key integer)
        member = db.session.get(Member, int(payload.get('sub')))
        if not member:
            print(f"[DEBUG jwtDecode] Member not found for sub={payload.get('sub')}")
            return None
        
        # If this is a password reset token (which has 5 attributes),
        # verify the password hash matches the current database record.
        # This invalidates the token once the password changes
        if payload.get('type') == 'reset':
            token_pwhash = payload.get('current_pass')
            if not token_pwhash or member.password_hash != token_pwhash:
                print("[DEBUG jwtDecode] Reset token invalid: password has already been changed.")
                return None
        
        return payload
    
    except jwt.ExpiredSignatureError:
        print("[DEBUG jwtDecode] Token EXPIRED")
        return None
    except jwt.InvalidTokenError as e:
        print(f"[DEBUG jwtDecode] InvalidTokenError: {e}")
        print(f"[DEBUG jwtDecode] Secret used: '{jwt_secret[:5]}...' (len={len(jwt_secret)})")
        return None



# generate a random and unique one time passcode to verify the member's email
def otp(total):
    return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=total)))




def set_auth_cookies(response, access_token, refresh_token):
    #Sets the access and refresh tokens in HTTP-only cookies.
    access_expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
    refresh_expires = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    # secure, samesite = get_cookie_settings()

    response.set_cookie(
        'access_token',
        access_token,
        max_age=int(access_expires.total_seconds()),
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )
    response.set_cookie(
        'refresh_token',
        refresh_token,
        max_age=int(refresh_expires.total_seconds()),
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )


def clear_auth_cookies(response):
    # secure, samesite = get_cookie_settings()
    #Clears both access and refresh token cookies.
    response.set_cookie(
        'access_token',
        '',
        max_age=0,
        expires=0,
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )
    response.set_cookie(
        'refresh_token',
        '',
        max_age=0,
        expires=0,
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/'
    )


from functools import wraps
from flask import g, jsonify

def token_required(f):
    #Decorator to require a valid access token stored in the request cookies, we place this decorator before every route for extra protection and security
    @wraps(f)
    def decorated(*args, **kwargs):
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

    



# from website import db
# from website.models import Member
# import jwt
# import random
# import string
# from flask import current_app, request
# from datetime import datetime, timedelta


# # This function creates an access token and stores the data of the user in the payload (the jwt code)
# def jwtEncode(member: Member, is_refresh=False) -> str:
#     jwt_secret = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'fallback_secret_key'
    
#     if is_refresh:
#         expire = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
#     else:
#         expire = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        
#     payload = {
#         # before it was  'sub': member.id this unacceptable
#         'sub': str(member.id),
#         'type': 'refresh' if is_refresh else 'access',
#         'iat': datetime.utcnow(),
#         'exp': datetime.utcnow() + expire
#     }
    
    
#     algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
#     return jwt.encode(payload, jwt_secret, algorithm=algorithm)



# def jwtDecode(token) -> dict:
#     jwt_secret = current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY') or 'fallback_secret_key'
#     algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    
#     try:
#         # we need to change it back to be integer
#         payload = jwt.decode(token, jwt_secret, algorithms=[algorithm])
#         member = db.session.get(Member, int(payload.get('sub')))
        
#         if not member:
#             print(f"[DEBUG jwtDecode] Member not found for sub={payload.get('sub')}")
#             return None
        
#         return payload
    
#     except jwt.ExpiredSignatureError:
#         print("[DEBUG jwtDecode] Token EXPIRED")
#         return None
#     except jwt.InvalidTokenError as e:
#         print(f"[DEBUG jwtDecode] InvalidTokenError: {e}")
#         print(f"[DEBUG jwtDecode] Secret used: '{jwt_secret[:5]}...' (len={len(jwt_secret)})")
#         return None
    

# # generate a random and unique one time passcode to verify the member's email
# def otp(total):
#     return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=total)))




# def set_auth_cookies(response, access_token, refresh_token):
#     #Sets the access and refresh tokens in HTTP-only cookies.
#     access_expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
#     refresh_expires = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
#     # secure, samesite = get_cookie_settings()

#     response.set_cookie(
#         'access_token',
#         access_token,
#         max_age=int(access_expires.total_seconds()),
#         httponly=True,
#         secure=False,
#         samesite='Lax',
#         path='/'
#     )
#     response.set_cookie(
#         'refresh_token',
#         refresh_token,
#         max_age=int(refresh_expires.total_seconds()),
#         httponly=True,
#         secure=False,
#         samesite='Lax',
#         path='/'
#     )


# def clear_auth_cookies(response):
#     #Clears both access and refresh token cookies.
#     response.set_cookie(
#         'access_token',
#         '',
#         max_age=0,
#         expires=0,
#         httponly=True,
#         secure=False,
#         samesite='Lax',
#         path='/'
#     )
#     response.set_cookie(
#         'refresh_token',
#         '',
#         max_age=0,
#         expires=0,
#         httponly=True,
#         secure=False,
#         samesite='Lax',
#         path='/'
#     )


# from functools import wraps
# from flask import g, jsonify

# def token_required(f):
#     #Decorator to require a valid access token stored in the request cookies, we place this decorator before every route for extra protection and security
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.cookies.get('access_token')
#         if not token:
#             return jsonify({'success': False, 'message': 'Authentication token is missing'}), 401
        
#         payload = jwtDecode(token)
#         if not payload or payload.get('type') != 'access':
#             return jsonify({'success': False, 'message': 'Token is invalid or expired'}), 401
        
#         #fetches the records of the memeber from the database and save it as a flask global object so that the route can use it
#         member = db.session.get(Member, payload.get('sub'))
#         if not member:
#             return jsonify({'success': False, 'message': 'Member not found'}), 401
        
#         g.current_member = member
#         return f(*args, **kwargs)
#     return decorated
