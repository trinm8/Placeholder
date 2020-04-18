import jwt
from flask import jsonify, g, current_app, request
from app import db
from app.api import bp
from app.api.auth import auth, token_auth
from datetime import datetime
from app.models import User
import functools
from app.api.errors import bad_request


@bp.route('/tokens', methods=['POST'])
@auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204


# A simple decorator to verify the login
def login_required(func):
    @functools.wraps(func)
    def check_token(*args, **kwargs):
        try:
            auth_type, token = request.headers['Authorization'].split(None, 1)
            if auth_type != "Bearer":
                raise

            data = jwt.decode(token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
            # TODO: fix expire
            # if data["exp"] < datetime.now():
            #     raise
            user = User.query.get_or_404(data["user_id"])
            g.current_user = user
            return func(*args, **kwargs)
        except:
            return bad_request("Please be sure your login is correct")
    return check_token
