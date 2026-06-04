from flask import request, jsonify
from .services import login_user, register_user, verify_account, resend_otp, refresh_token, logout_user
from . import auth_bp




@auth_bp.route('signin', methods=['POST'])
def login():
    data = request.get_json()
    return login_user(data)

@auth_bp.route('/signup', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No input data provided'}), 400
    return register_user(data)

# this route is used for step 2 of the login. frontend sends email and otp, backend creates refresh and access tokens
@auth_bp.route('/verify-2fa', methods=['POST'])
def verify():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No input data provided'}), 400
    return verify_account(data)

@auth_bp.route('/resend-otp', methods=['POST'])
def resend():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No input data provided'}), 400
    return resend_otp(data)

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    return refresh_token()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return logout_user()
