from app import db
from app.models import User, Route, RouteRequest, RequestStatus, addr
from app.routes_drive import bp
from app.routes_drive.forms import RequestForm, SendRequestForm, AddRouteForm, RouteSearchForm, EditRouteForm

from flask import flash, render_template, url_for, redirect, request
from flask_login import current_user, login_required

from sqlalchemy import Date, cast, func

from geopy import Nominatim, Location
from geopy import distance as dist
from geopy.exc import GeocoderTimedOut
from sympy.geometry import *
from math import cos, sin
import pyproj, json

from datetime import datetime  # Todo: Datetime
from time import sleep
from datetime import datetime, date  # Todo: Datetime

from flask_babel import _

import requests


def createRoute(form, departurelocation, arrivallocation):
    creator = User.query.filter_by(id=current_user.get_id()).first()
    creatorname = creator.username
    # Driver id is None wanneer de creator geen driver is zodat er later een driver zich kan aanbieden voor de route
    if form.type.data == 'Driver':  # TODO: does this work with translation?
        driverid = creator.id
    else:
        driverid = None
    # departure_location_lat = uniform(49.536612, 51.464020)
    # departure_location_long = uniform(2.634966, 6.115877)
    # arrival_location_lat = uniform(49.536612, 51.464020)
    # arrival_location_long = uniform(2.634966, 6.115877)
    d = form.date.data

    route = Route(  # creator=creatorname,
        departure_location_lat=departurelocation.latitude,
        departure_location_long=departurelocation.longitude, arrival_location_lat=arrivallocation.latitude,
        arrival_location_long=arrivallocation.longitude, driver_id=driverid, departure_time=d,
        departure_location_string=form.start.data, arrival_location_string=form.destination.data,
        playlist=form.playlist.data, passenger_places=form.places.data, maximum_deviation=15)
    db.session.add(route)
    db.session.commit()


def edit_route(id, departurelocation, arrivallocation, time, passenger_places=None, playlist=None):
    trip = Route.query.get_or_404(id)

    if departurelocation:
        try:
            if isinstance(departurelocation, Location):
                trip.departure_location_lat = departurelocation.latitude
                trip.departure_location_long = departurelocation.longitude
            else:
                trip.departure_location_lat = departurelocation[0]
                trip.departure_location_long = departurelocation[1]
        except:
            trip.departure_location_lat = departurelocation.latitude
            trip.departure_location_long = departurelocation.longitude
    if arrivallocation:
        try:
            if isinstance(departurelocation, Location):
                trip.arrival_location_lat = departurelocation.latitude
                trip.arrival_location_long = departurelocation.longitude
            else:
                trip.arrival_location_lat = departurelocation[0]
                trip.arrival_location_long = departurelocation[1]
        except:
            trip.arrival_location_lat = arrivallocation.latitude
            trip.arrival_location_long = arrivallocation.longitude
    if time:
        trip.departure_time = time

    if passenger_places:
        trip.passenger_places = passenger_places

    if playlist and playlist != "":
        trip.playlist = playlist

    db.session.commit()


@bp.route('/addroute', methods=['GET', 'POST'])
@login_required
def addRoute():
    # flash("Warning: this page won't submit anything to the database yet. We're working on it.")
    form = AddRouteForm()
    if form.validate_on_submit():
        geolocator = Nominatim(user_agent="[PlaceHolder]", scheme='http')
        try:
            departure_location = geolocator.geocode(form.start.data)
            sleep(1.1)
            arrival_location = geolocator.geocode(form.destination.data)
            sleep(1.1)  # sleep for 1 sec (required by Nominatim usage policy)
        except GeocoderTimedOut:
            flash(_("The geolocator is timing out! please try again"))
            return render_template('routes/addRoute.html', title='New Route', form=form)

        if departure_location is None:
            flash(_("The Start address is invalid"))
            return render_template('routes/addRoute.html', title='New Route', form=form)

        if arrival_location is None:
            flash(_("The destination address is invalid"))
            return render_template('routes/addRoute.html', title='New Route', form=form)

        if form.type.data == 'Passenger':  # TODO: does this work with translation
            return redirect(
                url_for("routes_drive.overview", lat_from=departure_location.latitude,
                        long_from=departure_location.longitude,
                        lat_to=arrival_location.latitude, long_to=arrival_location.longitude, time=form.date.data))

        if form.date.data is None or form.date.data < datetime.now():
            flash(_("Date is invalid"))
            return render_template('routes/addRoute.html', title='New Route', form=form)
        if len(form.start.data) > 256:
            flash(_("Start data exceeds character limit"))
            return render_template('routes/addRoute.html', title='New Route', form=form)
        if len(form.destination.data) > 256:
            flash(_("Destination data exceeds character limit"))
            return render_template('routes/addRoute.html', title='New Route', form=form)
        if len(form.playlist.data) > 32:
            flash(_("Playlist data exceeds character limit"))
            return render_template('routes/addRoute.html', title='New Route', form=form)
        if not str(form.places.data).isdigit():
            flash(_("Passenger places must be a number!"))
            return render_template('routes/addRoute.html', title='New Route', form=form)
        createRoute(form, departure_location, arrival_location)
        flash(_('New route added'))
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
    driver = User.query.get(trip.driver_id)
    requests = RouteRequest.query.filter_by(route_id=drive_id).all()
    acceptedRequests = []
    for requestparse in requests:
        if requestparse.status == RequestStatus.accepted:
            acceptedRequests.append((User.query.get(requestparse.user_id), requestparse.pickup_text()))
    requested = bool(RouteRequest.query.filter_by(route_id=drive_id, user_id=current_user.id).first())
    isDriver = False
    stops = []
    if current_user.id == driver.id:
        isDriver = True
        stops = trip.stops(sorted=True, passengerNames=True)
    # From routes that where registered without a drive, should be removed in the future
    # if current_user is None:
    #    user = current_user

    if form.validate_on_submit():
        if requested:
            RouteRequest.query.filter_by(route_id=drive_id, user_id=current_user.id).delete()
            db.session.commit()
            flash(_("Request has been cancelled"))
        else:
            if not trip.places_left():
                flash(_("There aren't any places left in the car"))
                return redirect(url_for("main.index"))
            geolocator = Nominatim(user_agent="[PlaceHolder]", scheme='http')
            try:
                pickup = geolocator.geocode(form.pickupPoint.data)
                if pickup is None:
                    flash(_("Pickup address not found"))
                    return redirect(url_for("routes_drive.drive", drive_id=drive_id))
                sleep(1.1)
            except GeocoderTimedOut:
                flash(_("The geolocator is timing out! please try again"))
                return render_template('routes/addRoute.html', title='New Route', form=form)
            requested = bool(RouteRequest.query.filter_by(route_id=drive_id, user_id=current_user.id).first())
            if requested:
                flash(_("You've already sent a request for this route"))
                return redirect(url_for("routes_drive.drive", drive_id=drive_id))
            request = RouteRequest(route_id=drive_id, user_id=current_user.id)
            request.set_PickupPoint(pickup.latitude, pickup.longitude, form.pickupPoint.data)
            db.session.add(request)
            db.session.commit()
            flash(_("Request has been made"))
        return redirect(url_for("main.index"))

    return render_template('routes/request_route.html', form=form, user=driver, trip=trip, requested=requested,
                           title='Route Request', passengers=acceptedRequests, isdriver=isDriver, stops=stops)


@bp.route('/drives/<drive_id>/request/cancel', methods=['GET', 'POST'])
@login_required
def cancel_request(drive_id):
    RouteRequest.query.filter_by(route_id=drive_id, user_id=current_user.id).delete()
    db.session.commit()
    flash(_("The request has been cancelled"))
    return redirect(url_for('main.index'))


@bp.route('/drives/<drive_id>/passenger-requests/<user_id>', methods=['GET', 'POST'])
@login_required
def passenger_request(drive_id, user_id):
    form = RequestForm()
    trip = Route.query.filter_by(id=drive_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()
    request = RouteRequest.query.filter_by(route_id=drive_id, user_id=user_id).first_or_404()

    if request.status == RequestStatus.accepted:
        flash(_("This route request has already been accepted"))
        return redirect(url_for("main.index"))
    if request.status == RequestStatus.rejected:
        flash(_("This route request has already been rejected"))
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        if form.accept.data:
            if not trip.places_left():
                flash(_("You don't have any places left in your car"))
                return redirect(url_for("main.index"))
            request.status = RequestStatus.accepted
            db.session.commit()
            flash(_("The route request was successfully accepted."))
        elif form.reject.data:
            RouteRequest.query.filter_by(route_id=drive_id, user_id=user_id).delete()
            db.session.commit()
            flash(_("The route request was successfully rejected."))
        return redirect(url_for("main.index"))

    return render_template('routes/route_request.html', form=form, user=user, trip=trip, title='Route Request',
                           pickup=request)


# Returns a score based on music preference of user u and v
def compareMusicPrefs(u_id: int, v_id: int) -> int:
    # Get the users
    u = User.query.get(u_id)
    v = User.query.get(v_id)

    # Calculate score where two likes = +1, 1 like and 1 dislike = -1, and otherwise = 0
    def score(x, y) -> int: return 1 if x.likes and y.likes else -1 if x.likes != y.likes else 0

    # Get pairs of music pref where genres match
    # Then apply the score function and return the sum of the results
    return sum([score(x, y) for x in u.musicpref for y in v.musicpref if x.genre == y.genre])


@bp.route("/overview", methods=["GET", "POST"])
def overview():
    form = RouteSearchForm(request.form)

    if form.submit.data:
        geolocator = Nominatim(user_agent="[PlaceHolder]", scheme='http')
        departure_location = geolocator.geocode(form.start.data)
        sleep(1.1)
        if departure_location is None:
            flash(_("The Start address is invalid"))
            return render_template('routes/search_results.html', title=_('New Route'), form=form)
        arrival_location = geolocator.geocode(form.destination.data)
        sleep(1.1)
        if arrival_location is None:
            flash(_("The destination address is invalid"))
            return render_template('routes/search_results.html', title=_('New Route'), form=form)

        lat_from = departure_location.latitude
        long_from = departure_location.longitude
        lat_to = arrival_location.latitude
        long_to = arrival_location.longitude

        time = form.date.data
        if not time:
            time = datetime.now()
        # time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

        allowed_distance = float(form.distance.data)

        # return redirect(
        #     url_for("routes_drive.overview", lat_from=departure_location.latitude,
        #             long_from=departure_location.longitude,
        #             lat_to=arrival_location.latitude, long_to=arrival_location.longitude, time=form.date.data, distance=form.distance.data))

    else:
        lat_from = request.args.get('lat_from')
        long_from = request.args.get('long_from')

        lat_to = request.args.get('lat_to')
        long_to = request.args.get('long_to')

        time = request.args.get('time')  # Should only be the date
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S') if time else None

        allowed_distance = request.args.get('distance')
        if not allowed_distance:
            allowed_distance = 2

    departure_location = (lat_from, long_from)
    arrival_location = (lat_to, long_to)

    routes = filter_routes(allowed_distance, arrival_location, departure_location, time)

    # Sort our routes on music preference
    routes = sorted(routes, key=lambda x: compareMusicPrefs(current_user.id, x.driver_id), reverse=True)

    # Try to get some routes from team3
    try:
        data = {"from": "{lat}, {long}".format(lat=lat_from, long=long_from),
                "to": "{lat}, {long}".format(lat=lat_to, long=long_to), "arrive-by": str(time.isoformat()) + ".00",
                "limit": 3}
        response = requests.get("https://team3.ppdb.me/api/drives/search",
                                   headers={"Content-Type": "application/json"},
                                   params=data)
        routes_ = json.loads(response.content)
        other_routes = []
        for route in routes_:
            add = True
            required_elements = ["arrive-by", "from", "to", "id"]
            for element in required_elements:
                if element not in route:
                    add = False
                    break
            if add:
                other_routes.append(route)
    except:
        other_routes = []
        print('Something went wrong with GET to team 3')

    return render_template('routes/search_results.html', routes=routes, title="Search", src=addr(lat_from, long_from),
                           dest=addr(lat_to, long_to), form=form, other_routes=other_routes)


def filter_routes(allowed_distance, arrival_location, departure_location, time, limit=20):
    if not time:
        return []

    # dist.distance(Route.arrival_coordinates, arrival_location).km <= allowed_distance
    # and
    same_day_routes = Route.query.filter(func.DATE(Route.departure_time) == time.date()).limit(limit).all()  # https://gist.github.com/Tukki/3953990
    routes = []
    from geopy import distance  # No idea why this include won't work when placed outside this function
    import sys
    # allowed_distance = 2
    # * zorgt ervoor dat de elementen uit de locatie afzonderlijk woorden doorgegeven

    transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:5643")

    pickupPoint = transformer.transform(*departure_location)
    dropoffPoint = transformer.transform(*arrival_location)

    print("Sameday", same_day_routes, file=sys.stderr)

    for route in same_day_routes:
        route_dep = (route.departure_location_lat, route.departure_location_long)
        route_arr = (route.arrival_location_lat, route.arrival_location_long)

        routeLineSegment = Segment(Point(transformer.transform(*route_dep)), Point(transformer.transform(*route_arr)))

        if route.maximum_deviation is None:
            route.maximum_deviation = 15

        print("1", routes, file=sys.stderr)

        print("Distance pickup", routeLineSegment.distance(pickupPoint), routeLineSegment.distance(pickupPoint)/1000, file=sys.stderr)
        print("Arrival", distance.distance(route_arr, arrival_location).km, file=sys.stderr)

        # @trinm: ik (Arno) heb hier de * 100 op de twee regels hieronder weggedaan, anders faalde de test.
        if routeLineSegment.distance(pickupPoint)/1000 < route.maximum_deviation and \
                distance.distance(route_arr, arrival_location).km <= allowed_distance:
            routes.append(route)

        print("2", routes, file=sys.stderr)

        # if distance.distance(route_dep, departure_location).km <= allowed_distance and \
        #         distance.distance(route_arr, arrival_location).km <= allowed_distance:
        #     routes.append(route)
    return routes


def toCartesian(lat, lng):
    x = 6371 * cos(float(lat)) * cos(float(lng))
    y = 6371 * cos(float(lat)) * sin(float(lng))
    z = 6371 * sin(float(lat))

    return x, y, z


@bp.route('/history', methods=['GET'])
@login_required
def history():
    current_time = datetime.utcnow()
    routes_driver = Route.query.filter_by(driver_id=current_user.id)
    routes_passenger = Route.query.filter(
        RouteRequest.query.filter_by(user_id=current_user.id, route_id=Route.id).exists())
    routes = routes_driver.union(routes_passenger)

    past_routes_unsort = routes.filter(Route.departure_time <= current_time)

    past_routes = []
    if past_routes_unsort:
        past_routes.append(past_routes_unsort.first())
    for unsort_route in past_routes_unsort:
        temp_routes = []
        for route in past_routes:
            if route.departure_time > unsort_route.departure_time:
                temp_routes.append(unsort_route)
            temp_routes.append(route)
        past_routes = temp_routes

    return render_template('main/history.html', title=_('Notifications'), routes=past_routes)


@bp.route('/drives/<id>/delete', methods=['GET'])
@login_required
def delete(id):
    # TODO: check cascade
    if Route.query.get(id).driver().id == current_user.id:
        Route.query.filter_by(id=id).delete()
        db.session.commit()
        flash(_("The route has been deleted successfully"))
    else:
        flash(_("You have to be the driver of the route in order to remove it"))
    return redirect(url_for("main.index"))


@bp.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def editRoute(id):
    # TODO: not yet tested (not enough time)
    if Route.query.get(id).driver().id != current_user.id:
        flash(_("You have to be the driver of the route in order to edit it"))
        return redirect(url_for("main.index"))
    # flash("Warning: this page won't submit anything to the database yet. We're working on it.")
    form = EditRouteForm(request.form)
    if form.submit.data:
        departure_location = None
        arrival_location = None
        time = None
        geolocator = Nominatim(user_agent="[PlaceHolder]", scheme='http')
        if form.start.data and form.start.data != "":
            if len(form.start.data) > 256:
                flash(_("Start data exceeds character limit"))
                return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
            departure_location = geolocator.geocode(form.start.data)
            if departure_location is None:
                flash(_("The Start address is invalid"))
                return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
            trip = Route.query.get_or_404(id)
            trip.departure_location_string = form.start.data
            db.session.commit()
        if form.destination.data and form.destination.data != "":
            if len(form.destination.data) > 256:
                flash(_("Destination data exceeds character limit"))
                return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
            arrival_location = geolocator.geocode(form.destination.data)
            if arrival_location is None:
                flash(_("The destination address is invalid"))
                return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
            trip = Route.query.get_or_404(id)
            trip.arrival_location_string = form.destination.data
            db.session.commit()
        if form.date.data:
            if form.date.data < datetime.now():  # TODO datetime
                flash("Date is invalid")
                return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
            time = form.date.data
        if len(form.playlist.data) > 32:
            flash(_("Playlist data exceeds character limit"))
            return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
        if form.places.data:
            trip = Route.query.get_or_404(id)
            if form.places.data < trip.passenger_places - trip.places_left():
                flash(_("Not enough passenger places"))
                return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
        edit_route(id, departure_location, arrival_location, time, form.places.data, form.playlist.data)
        flash(_('Your changes have been updated'))
        return redirect(url_for('routes_drive.drive', drive_id=id))
    return render_template('routes/editRoute.html', title=_('Edit Route'), form=form)
