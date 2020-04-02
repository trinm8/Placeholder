from flask import Blueprint

bp = Blueprint('routes_drive', __name__)

from app.routes_drive import routes, forms
