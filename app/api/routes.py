from flask import jsonify, request, url_for, g
from app.models import Route, RouteRequest, User
from app.api import bp
from app.api.errors import bad_request
from app import db
from app.api.auth import auth, token_auth
from app.routes_drive.routes import edit_route, filter_routes
from app.api.tokens import login_required

@bp.route('/drives/<int:drive_id>', methods=['GET'])
def get_route(drive_id):
    return jsonify(Route.query.get_or_404(drive_id).to_dict())


@bp.route('/drives', methods=['POST'])
@login_required
def create_route():
    data = request.get_json() or {}
    if data.get("from") is None or data.get("to") is None or data.get("passenger-places") is None \
            or data.get("arrive-by") is None:
        return bad_request("Must include from, to passenger-places and time")
    route = Route()
    route.from_dict(data)
    route.driver_id = g.current_user.id
    db.session.add(route)
    db.session.commit()
    response = jsonify(route.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_route', drive_id=route.id)
    return response


@bp.route('/drives/<int:id>', methods=['DELETE'])
@login_required
def delete_route(id):
    if not id:
        return bad_request("Must include id")
    Route.query.filter_by(id=id).delete()
    db.session.commit()

    response = jsonify({})
    response.status_code = 201

    return response

@bp.route('/drives/<int:id>', methods=['PUT'])
@login_required
def update_route(id):
    data = request.get_json() or {}
    route = Route.query.get_or_404(id)

    arrival_location = None
    departure_location = None
    time = None
    passenger_places = None
    if "from" in data:
        departure_location = data["from"]
    elif "to" in data:
        arrival_location = data["to"]
    elif "time" in data:
        time = data["time"]
    elif "passenger-places" in data:
        passenger_places = data["passenger-places"]
    edit_route(id, departure_location, arrival_location,
               time, passenger_places)  # TODO: check whether departure and arrival location are the right format
    route = Route.query.get(id)
    response = jsonify(route.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_route', drive_id=route.id)
    return response


@bp.route('/drives/<int:drive_id>/passenger-requests', methods=['GET'])
# @token_auth.login_required
@login_required
def get_passenger_requests(drive_id):
    # Is user the driver?
    drive = Route.query.get_or_404(drive_id)
    if g.current_user.id != drive.user_id:
        return bad_request('Only the driver can view requests for this drive.')

    # Return response
    response = jsonify([
        r.to_dict()
        for r in RouteRequest.query.filter_by(route_id=drive_id)
    ])
    response.status_code = 200
    return response


@bp.route('/drives/<int:drive_id>/passenger-requests', methods=['POST'])
@login_required
def create_passenger_request(drive_id):
    route_req = RouteRequest(drive_id, g.current_user.id)
    db.session.add(route_req)
    db.session.commit()
    response = jsonify(route_req.to_dict())
    response.status_code = 201
    # response.headers['Location'] = url_for('api.get_request', drive_id=route_req.route_id, user_id=route_req.user_id)
    # TODO: location to /drives/int/passenger-requests/int
    # Make another GET function for single passenger-requests?
    return response

@bp.route('/drives/<int:drive_id>/passenger-requests/<int:user_id>', methods=['DELETE'])
@login_required
def delete_request(drive_id, user_id):
    RouteRequest.query.filter_by(route_id=drive_id, user_id=user_id).delete()
    db.session.commit()

    response = jsonify({})
    response.status_code = 201

    return response

@bp.route('/drives/<int:drive_id>/passenger-requests/<int:user_id>', methods=['POST'])
@login_required
def change_request_status(drive_id, user_id):
    # Is user driver?
    drive = Route.query.get_or_404(drive_id)
    if g.current_user.id != drive.user_id:
        return bad_request('Only the driver can view requests for this drive.')

    data = request.get_json() or {}

    if 'action' not in data:
        return bad_request('Data must include action!')

    if data['action'] not in ['accept', 'reject']:
        return bad_request('Action must be accept or reject!')

    route_req = RouteRequest.query.get_or_404((drive_id, user_id))
    if data['action'] == 'accept':
        route_req.accept()
    else:
        route_req.reject()

    db.session.commit()
    response = jsonify(route_req.to_dict())
    response.status_code = 200
    # response.headers['Location'] = url_for('api.get_request', drive_id=route_req.route_id, user_id=route_req.user_id)
    # TODO: Idem as function above
    return response


@bp.route("/overview", methods=["GET"])
def overview():
    data = request.get_json() or {}
    if "from" not in data or "to" not in data or "passenger-places" not in data or "arrive-by" not in data:
        return bad_request("Must include from, to passenger-places and time")

    lat_from = data["from"][0]
    long_from = data["from"][1]
    lat_to = data["to"][0]
    long_to = data["to"][1]
    datetime = data["time"]  # Should only be the date
    time = datetime.strptime(datetime, '%Y-%m-%d %H:%M:%S')

    routes = filter_routes(5, (lat_to, long_to), (lat_from, long_from), time)
    return jsonify(routes.to_dict())

@bp.route('/user/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    # Is user the driver?
    user = User.query.get_or_404(id)
    # Return response
    response = jsonify(user.to_dict())
    response.status_code = 200
    return response


@bp.route('/user', methods=['DELETE'])
@login_required
def delete_user():
    User.query.get_or_404(g.current_user.id).delete()
    db.session.commit()

    response = jsonify({})
    response.status_code = 201
    return response

# TODO: edit user