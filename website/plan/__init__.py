from flask import Blueprint
plan_bp = Blueprint("plan", __name__, url_prefix="/api/plans")
from . import routes


