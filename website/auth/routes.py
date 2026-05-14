from flask import request
from .services import login_user
from . import auth_bp

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return login_user(data)