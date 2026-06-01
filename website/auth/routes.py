from flask import request, jsonify
from .services import login_user, register_user, verify_account, refresh_token, logout_user, resend_otp
from . import auth_bp


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No input data provided'}), 400
    return login_user(data)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No input data provided'}), 400
    return register_user(data)


@auth_bp.route('/verify', methods=['POST'])
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
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No input data provided'}), 400
    return refresh_token(data)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return logout_user()