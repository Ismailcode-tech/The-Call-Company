from flask import Blueprint

membership_bp = Blueprint("membership", __name__, url_prefix="/api/membership")
from . import routes