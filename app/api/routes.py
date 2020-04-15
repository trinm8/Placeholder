from flask import jsonify, request, url_for, g
from app.models import Route, RouteRequest
from app.api import bp
from app.api.errors import bad_request
from app import db
from app.api.auth import auth, token_auth


@bp.route('/drives/<int:drive_id>', methods=['GET'])
def get_route(drive_id):
    return jsonify(Route.query.get_or_404(drive_id).to_dict())


@bp.route('/drives', methods=['POST'])
def create_route():
    data = request.get_json() or {}
    if "from" not in data or "to" not in data or "passenger-places" not in data or "arrive-by" not in data:
        return bad_request("Must include from, to passenger-places and time")
    route = Route()
    route.from_dict(data)
    db.session.add(route)
    db.session.commit()
    response = jsonify(route.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_route', drive_id=route.id)
    return response


@bp.route('/drives/<int:drive_id>/passenger-requests', methods=['GET'])
@token_auth.login_required
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
@token_auth.login_required
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


@bp.route('/drives/<int:drive_id>/passenger-requests/<int:user_id>', methods=['POST'])
@token_auth.login_required
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
    distance = 1 / 768
    routes = Route.query \
        .filter((lat_from - Route.departure_location_lat) * (lat_from - Route.departure_location_lat) < distance) \
        .filter((long_from - Route.departure_location_long) * (long_from - Route.departure_location_long) < distance) \
        .filter((lat_to - Route.arrival_location_lat) * (lat_to - Route.arrival_location_lat) < distance) \
        .filter((long_to - Route.arrival_location_long) * (long_to - Route.arrival_location_long) < distance)
    return jsonify(routes.to_dict())
