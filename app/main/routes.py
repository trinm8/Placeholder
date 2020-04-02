from flask import render_template, redirect
from flask_login import current_user

from app import db
from app.models import Statistics, Route
from app.main import bp


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
        routes = Route.query.filter_by(driver_id=current_user.id) #TODO: Check date is not past yet

        return render_template('main/main_logged_in.html', title='Dashboard', routes=routes)
    return render_template('main/home.html', title='Welcome')


@bp.route('/about')
def about():
    counter = Statistics.query.first()
    if counter is None:
        counter = "over 9000"
    else:
        counter = counter.rickroll_counter
    return render_template('main/about.html', title='About', counter=counter)





