from flask import render_template, redirect
from flask_login import current_user

from app import db
from app.models import Statistics, Route, RouteRequest, User, RequestStatus
from app.main import bp

from sqlalchemy import union

from datetime import datetime

from flask_babel import _


@bp.route('/lol')
def lol():
    counter = Statistics.query.first()
    if counter is None:
        counter = Statistics(rickroll_counter=0)
        db.session.add(counter)
    counter.rickroll_counter += 1
    db.session.commit()
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")




@bp.route('/index')
@bp.route('/')
def index():
    if current_user.is_authenticated:
        current_time = datetime.utcnow()
        routes_driver = Route.query.filter_by(driver_id=current_user.id)
        routes_passenger = Route.query.filter(RouteRequest.query.filter_by(user_id=current_user.id, route_id=Route.id).exists())
        routes = routes_driver.union(routes_passenger)
        future_routes = routes.filter(Route.departure_time >= current_time).all()
        future_routes.sort(key=lambda x: x.departure_time)
        passengerIds = []
        if len(future_routes) > 0 and future_routes[0]:
            passengerIds = future_routes[0].passengers()
        passengers = []
        for passengerId in passengerIds:
            # get the users of the passenger id
            user = User.query.filter_by(id=passengerId).first_or_404()
            passengers.append(user)

        return render_template('main/main_logged_in.html', title=_('Dashboard'), future_routes=future_routes, passengers=passengers)
    return render_template('main/home.html', title=_('Welcome'))


@bp.route('/about')
def about():
    counter = Statistics.query.first()
    if counter is None:
        counter = _("over 9000")
    else:
        counter = counter.rickroll_counter
    return render_template('main/about.html', title='About', counter=counter)





