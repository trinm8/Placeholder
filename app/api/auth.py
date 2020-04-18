import jwt
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask import g, current_app
from app.models import User
from app.api.errors import error_response

auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)

@auth.error_handler
def auth_error():
    return error_response(401)

@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    return error_response(401)
