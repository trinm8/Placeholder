from flask import render_template, redirect
from flask_login import current_user

from app import db
from app.models import Statistics, Route, RouteRequest
from app.main import bp

from sqlalchemy import union

from datetime import datetime


@bp.route('/lol')
def lol():
    counter = Statistics.query.first()
    if counter is None:
        counter = Statistics(rickroll_counter=0)
        db.session.add(counter)
    counter.rickroll_counter += 1
    db.session.commit()
    return redirect("https://www.youtube.com/watch?v=cvh0nX08nRw")




@bp.route('/index')
@bp.route('/')
def index():
    if current_user.is_authenticated:
        current_time = datetime.utcnow()
        routes_driver = Route.query.filter_by(driver_id=current_user.id)
        routes_passenger = Route.query.filter(RouteRequest.query.filter_by(user_id=current_user.id, route_id=Route.id).exists())
        routes = routes_driver.union(routes_passenger)

        future_routes = Route.query.filter(Route.departure_time >= current_time) #TODO: intersection nemen

        return render_template('main/main_logged_in.html', title='Dashboard', routes=routes, future_routes=future_routes)
    return render_template('main/home.html', title='Welcome')


@bp.route('/about')
def about():
    counter = Statistics.query.first()
    if counter is None:
        counter = "over 9000"
    else:
        counter = counter.rickroll_counter
    return render_template('main/about.html', title='About', counter=counter)





