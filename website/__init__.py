from flask import Config, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from .auth import auth_bp
    from .membership import membership_bp
    from .payment import payment_bp
    from .plan import plan_bp
    from .main import main_bp
    from .ai_assistant import ai_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(membership_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(ai_bp)




    return app






