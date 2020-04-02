from app import db
from app.models import User, Route, RouteRequest, RequestStatus, addr
from app.routes_drive import bp
from app.routes_drive.forms import RequestForm, SendRequestForm, AddRouteForm

from flask import flash, render_template, url_for, redirect, request
from flask_login import current_user, login_required


from geopy import Nominatim
from datetime import date  # Todo: Datetime


def createRoute(form, departurelocation, arrivallocation):
    creator = User.query.filter_by(id=current_user.get_id()).first()
    creatorname = creator.username
    # Driver id is None wanneer de creator geen driver is zodat er later een driver zich kan aanbieden voor de route
    if form.type.data == 'Driver':
        driverid = creator.id
    else:
        driverid = None
    # departure_location_lat = uniform(49.536612, 51.464020)
    # departure_location_long = uniform(2.634966, 6.115877)
    # arrival_location_lat = uniform(49.536612, 51.464020)
    # arrival_location_long = uniform(2.634966, 6.115877)
    d = form.date.data
    route = Route(creator=creatorname, departure_location_lat=departurelocation.latitude,
                  departure_location_long=departurelocation.longitude, arrival_location_lat=arrivallocation.latitude,
                  arrival_location_long=arrivallocation.longitude, driver_id=driverid, departure_time=d)
    db.session.add(route)
    db.session.commit()


@bp.route('/addroute', methods=['GET', 'POST'])
@login_required
def addRoute():
    # flash("Warning: this page won't submit anything to the database yet. We're working on it.")
    form = AddRouteForm()
    if form.validate_on_submit():
        geolocator = Nominatim(user_agent="[PlaceHolder]")
        departure_location = geolocator.geocode(form.start.data)
        if departure_location is None:
            flash("The Start address is invalid")
            return render_template('routes/addRoute.html', title='New Route', form=form)
        arrival_location = geolocator.geocode(form.destination.data)
        if arrival_location is None:
            flash("The destination address is invalid")
            return render_template('routes/addRoute.html', title='New Route', form=form)
        if form.type.data == 'Passenger':
            return redirect(
                url_for("routes_drive.overview", lat_from=departure_location.latitude,
                        long_from=departure_location.longitude,
                        lat_to=arrival_location.latitude, long_to=arrival_location.longitude))

        if form.date.data < date.today():  # TODO datetime
            flash("Date is invalid")
            return render_template('routes/addRoute.html', title='New Route', form=form)

        createRoute(form, departure_location, arrival_location)
        flash('New route added')
        return redirect(url_for('main.index'))
    return render_template('routes/addRoute.html', title='New Route', form=form)


@bp.route('/requests', methods=['GET'])
@login_required
def getRequests():
    # Get all requests for routes of which current_user is the driver
    # SELECT * FROM RouteRequests
    #   WHERE EXIST (SELECT * FROM Route WHERE current_user.id=Route.driver_id and Route.id = RouteRequest.route_id)
    requests = RouteRequest.query \
        .filter(Route.query
                .filter_by(driver_id=current_user.id)
                .filter_by(id=RouteRequest.route_id)
                .exists())

    # requests = RouteRequest.query.filter_by(user_id=current_user.get_id())
    # requests = []
    # for r in request_query:
    #     route = Route.query.get_or_404(r.route_id)
    #     # request = {
    #     #     'status': r.status,
    #     #     'user': 'John',
    #     #     'from': 'Somewhere',
    #     #     'to': 'Elsewhere',
    #     #     'time': route.departure_time
    #     # }
    #     requests.append(route)

    return render_template('routes/requests.html', title='Requests', requests=requests)


@bp.route('/drives/<drive_id>', methods=['GET', 'POST'])
@login_required
def drive(drive_id):
    form = SendRequestForm()
    trip = Route.query.get_or_404(drive_id)
    user = User.query.get(trip.driver_id)
    requested = bool(RouteRequest.query.filter_by(route_id=drive_id, user_id=current_user.id).first())

    # From routes that where registered without a drive, should be removed in the future
    if user is None:
        user = current_user

    if form.validate_on_submit():
        if requested:
            RouteRequest.query.filter_by(route_id=drive_id, user_id=current_user.id).delete()
            db.session.commit()
            flash("Request has been cancelled")
        else:
            request = RouteRequest(route_id=drive_id, user_id=current_user.id)
            db.session.add(request)
            db.session.commit()
            flash("Request has been made")
        return redirect(url_for("main.index"))

    return render_template('routes/request_route.html', form=form, user=user, trip=trip, requested=requested,
                           title='Route Request')


@bp.route('/drives/<drive_id>/passenger-requests/<user_id>', methods=['GET', 'POST'])
@login_required
def passenger_request(drive_id, user_id):
    form = RequestForm()
    trip = Route.query.filter_by(id=drive_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()
    request = RouteRequest.query.filter_by(route_id=drive_id, user_id=user_id).first_or_404()


    if request.status == RequestStatus.accepted:
        flash("This route request has already been accepted")
        return redirect(url_for("main.index"))
    if request.status == RequestStatus.rejected:
        flash("This route request has already been rejected")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        if form.accept.data:
            request.status = RequestStatus.accepted
            db.session.commit()
            flash("The route request was successfully accepted.")
        elif form.reject.data:
            request.status = RequestStatus.rejected
            db.session.commit()
            flash("The route request was successfully rejected.")
        return redirect(url_for("main.index"))

    return render_template('routes/route_request.html', form=form, user=user, trip=trip, title='Route Request')


@bp.route("/overview", methods=["GET"])
def overview():
    lat_from = request.args.get('lat_from')
    long_from = request.args.get('long_from')
    lat_to = request.args.get('lat_to')
    long_to = request.args.get('long_to')
    routes = Route.query \
        .filter((lat_from - Route.departure_location_lat) * (lat_from - Route.departure_location_lat) > -10) \
        .filter((long_from - Route.departure_location_long) * (long_from - Route.departure_location_long) > -10) \
        .filter((lat_to - Route.arrival_location_lat) * (lat_to - Route.arrival_location_lat) > -10) \
        .filter((long_to - Route.arrival_location_long) * (long_to - Route.arrival_location_long) > -10)
    return render_template('routes/route_overview.html', routes=routes, title="Search", src=addr(lat_from, long_from),
                           dest=addr(lat_to, long_to))
