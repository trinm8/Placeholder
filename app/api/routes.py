from flask import jsonify, request, url_for
from app.models import Route, RouteRequest
from app.api import bp
from app.api.errors import bad_request
from app import db


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


@bp.route('/drives/<int:drive_id>/requested_by/<int:user_id>', methods=['GET'])
def get_request(drive_id, user_id):
    return jsonify(RouteRequest.query.get_or_404((drive_id, user_id)).to_dict())


@bp.route('/requests', methods=['POST'])
def create_request():
    data = request.get_json() or {}
    if 'drive_id' not in data or 'user_id' not in data:
        return bad_request('Data must include drive_id and user_id!')
    route_req = RouteRequest(data['route_id'], data['user_id'])
    db.session.add(route_req)
    db.session.commit()
    response = jsonify(route_req.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_request', drive_id=route_req.route_id, user_id=route_req.user_id)
    return response


@bp.route('/requests/status', methods=['POST'])
def change_request_status():
    data = request.get_json() or {}
    if 'drive_id' not in data or 'user_id' not in data or 'is_accepted' not in data:
        return bad_request('Data must include drive_id, user_id and is_accepted!')
    route_req = RouteRequest.query.get_or_404((data['route_id'], data['user_id']))
    if data['is_accepted']:
        route_req.accept()
    else:
        route_req.reject()
    db.session.commit()
    response = jsonify(route_req.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_request', drive_id=route_req.route_id, user_id=route_req.user_id)
    return response
