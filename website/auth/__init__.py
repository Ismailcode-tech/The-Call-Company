#from flask import Flask
#from flask_mail import Mail
# from flask_sqlalchemy import SQLAlchemy
# # from flask_login import LoginManager
# from os import path

# import os
# db = SQLAlchemy()
# DB_NAME = "database.db"
#mail = Mail()

# def create_app():
#     app = Flask(__name__)
    


#     db.init_app(app)
    
    
  

#     # from .auth import auth
    
    
#     # app.register_blueprint(views, url_prefix='/')
#     # app.register_blueprint(auth, url_prefix='/')  
#      mail.init_app(app) 



    
#     return app




# def create_database(app):
#     from ..models import User, Note

#     with app.app_context():
        
#         db.create_all()
#         print("Done! I just created the tables in MySQL.")

from flask import Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
from . import routes