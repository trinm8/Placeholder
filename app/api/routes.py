from flask import jsonify, request, url_for
from app.models import Route
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
