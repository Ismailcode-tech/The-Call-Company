
# def create_database(app):
#     from ..models import User, Note

#     with app.app_context():
        
#         db.create_all()
#         print("Done! I just created the tables in MySQL.")

from flask import Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
from . import routes
