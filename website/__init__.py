
from flask_cors import CORS
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)
    
    app.config.from_object(Config)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from . import models

    create_database(app)


    from .auth import auth_bp
    from .membership import membership_bp
    from .payment import payment_bp
    from .plan import plan_bp

    from .ai_assistant import ai_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(membership_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(ai_bp)


    return app

def create_database(app):          
    with app.app_context():
        db.create_all()
        print('Created Database!')


@login_manager.user_loader
def load_user(user_id):
    from website.models import Member
    try:
        return db.session.get(Member, int(user_id))
    except (ValueError, TypeError):
        return None


@login_manager.request_loader
def load_user_from_request(request):
    from website.auth.tokengeneration import jwtDecode
    from website.models import Member

    token = request.cookies.get('access_token')
    if not token:
        return None

    payload = jwtDecode(token)
    if not payload or payload.get('type') != 'access':
        return None

    try:
        return db.session.get(Member, int(payload.get('sub')))
    except (ValueError, TypeError):
        return None






