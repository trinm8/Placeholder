from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from app.api import users, errors, tokens, routes, reviews