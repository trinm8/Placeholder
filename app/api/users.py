from flask import jsonify, request, url_for
from app.api.errors import bad_request
from app.routes import register_user_func
from app.api import bp



@bp.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    if "username" not in data or "password" not in data or "firstname" not in data or "lastname" not in data:
        return bad_request("Must include username, password, firstname and lastname")
    user_id = register_user_func(data["username"], data["firstname"], data["lastname"], data["password"])
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


# @bp.route('/users/auth', methods=['POST'])
# def auth():
#     data = request.get_json() or {}
#
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


@bp.route('/users/<int:id>/followers', methods=['GET'])
def get_followers(id):
    pass


@bp.route('/users/<int:id>/followed', methods=['GET'])
def get_followed(id):
    pass


@bp.route('/users', methods=['POST'])
def create_user():
    pass


@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass
