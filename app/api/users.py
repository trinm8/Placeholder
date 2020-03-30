from app.api import bp


@bp.route('/users/register', methods=['POST'])
def register_user():
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
    pass


@bp.route('/users/auth', methods=['POST'])
def auth():
    # Body:
    # {
    #   "username": "MarkP",
    #   "password": "MarkIsCool420"
    # }
    # Response:
    # 200, Content-Type:application/json
    # {
    #   "token": "<token>"
    # }
    # 401 if invalid password
    pass


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
