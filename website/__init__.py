
from flask_cors import CORS
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
    
    app.config.from_object(Config)
    db.init_app(app)

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






