from flask import jsonify, request, url_for
from app.models import User
from app.api.errors import bad_request
from app.auth.routes import register_user_func
from app.api import bp



@bp.route('/users/register', methods=['POST'])
def register_user():

    data = request.get_json() or {}
    if "username" not in data or "password" not in data or "firstname" not in data or "lastname" not in data:
        return bad_request("Must include username, password, firstname and lastname")
    user_id = register_user_func(data["username"], data["firstname"], data["lastname"], data["password"])
    if not user_id:
        return bad_request("User couldn't be created. The name is probably already taken.")
    response = jsonify(id=user_id)
    response.status_code = 201
    return response
    #response.headers['Location'] = url_for('api.auth', user_id=user_id)

    # Body:
    # {
    #     "username": "MarkP",
    #     "firstname": "Mark",
    #     "lastname": "Peeters",
    #     "password": "MarkIsCool420"
    # }
    # Response:
    # 201, Content-Type:application/json
    # {
    #   "id": 14
    # }


@bp.route('/users/auth', methods=['POST'])
def auth():
    data = request.get_json() or {}
    if "username" not in data or "password" not in data:
        return bad_request("Must include username and password")
    user = User.query.filter_by(username=data["username"]).first()
    if not user.check_password(data["password"]):
        response = jsonify()
        response.status_code = 401
        return response
    response = jsonify(token=user.get_token())
    response.status_code = 200
    return response


#     # Body:
#     # {
#     #   "username": "MarkP",
#     #   "password": "MarkIsCool420"
#     # }
#     # Response:
#     # 200, Content-Type:application/json
#     # {
#     #   "token": "<token>"
#     # }
#     # 401 if invalid password
#     pass


@bp.route('/users/<int:id>', methods=['GET'])
def update_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())
