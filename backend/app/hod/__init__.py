from flask import Blueprint

hod_bp = Blueprint('hod', __name__)

from backend.app.hod import routes  # noqa: E402, F401
