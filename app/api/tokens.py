import jwt
from flask import jsonify, g, current_app
from app import db
from app.api import bp
from app.api.auth import auth, token_auth
from datetime import datetime
from app.models import User


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


def get_user(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'],
                          algorithms=['HS256'])['reset_password']
        if data["exp"] > datetime.now():
            raise
        user = User.get_or_404(data["user_id"])
        g.current_user = user
        return user
    except:
        return None
