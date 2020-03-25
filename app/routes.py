from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.email import send_password_reset_email
from app.forms import *
from app.models import *
from werkzeug.urls import url_parse
from random import uniform
from datetime import *
from geopy import Nominatim

@app.route('/forgot_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ForgotPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            send_password_reset_email(user, form.email.data)
            flash(
                "Check your email for the instructions to reset your password. Check your junk mail too when you didn't receive anything")
            return redirect(url_for('login'))
        else:
            flash('No user found with the given name.')
            return redirect(url_for('reset_password_request'))
    return render_template('forgot_password.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/index')
@app.route('/')
def index():
    if current_user.is_authenticated:
        class trip:
            description = "From Middelheimlaan to Edegemsesteenweg"
            time = "07:00 - 5 March 2020"
            driver = "arnodece"
            passengers = ["Sien Nuyens", "Sam Peeters", "Tim Sanders"]
            departure = "Middelheimlaan 1, 2020 Antwerpen"
            destination = "Edegemsesteenweg 100, 2020 Antwerpen"
            stops = ["Randomstraat 69, 2020 Antwerpen", "Timisgaystraat 420, 2020 Antwerpen"]

        trips = [trip(), trip(), trip(), trip(), trip(), trip()]

        return render_template('main_logged_in.html', title='Dashboard', trips=trips, trip=trips[0])
    return render_template('home.html', title='Welcome')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


# @app.route('/account')
# @login_required
# def account():
#     return render_template('account.html', title='Account')


@app.route('/users/<username>')
@login_required
def user_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title='Account', user=user)


@app.route('/account/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    # flash("Warning: this page won't submit anything to the database yet. We're working on it.")

    form = Settings()

    if form.validate_on_submit():

        usr = User.query.filter_by(id=current_user.get_id()).first()

        # Profile settings
        if form.submit_profile.data:
            usr.firstname = form.firstname.data
            usr.lastname = form.lastname.data
            usr.email = form.email.data
            if len(form.password.data) > 0:
                usr.set_password(form.password.data)
            db.session.commit()

            flash("Profile settings updated!")

        # Add liked genre
        if form.submit_liked.data:
            if len(form.liked_genre.data) > 0:
                pref = MusicPref(user=usr.id, genre=form.liked_genre.data, likes=True)
                db.session.add(pref)
                db.session.commit()

                flash("Liked genre added!")

        # Add disliked genre
        if form.submit_disliked.data:
            if len(form.disliked_genre.data) > 0:
                pref = MusicPref(user=usr.id, genre=form.disliked_genre.data, likes=False)
                db.session.add(pref)
                db.session.commit()

                flash("Disliked genre added!")

        # Car settings
        if form.submit_car.data:
            usr.car_color = form.color.data
            usr.car_brand = form.brand.data
            usr.car_plate = form.plate.data
            db.session.commit()

            flash("Car settings updated!")

    return render_template('settings.html', title='Account Settings', form=form)


def createRoute(form):
    creator = User.query.filter_by(id=current_user.get_id()).first()
    creatorname = creator.username
    # Driver id is None wanneer de creator geen driver is zodat er later een driver zich kan aanbieden voor de route
    if form.type.data == 'Driver':
        driverid = creator.id
    else:
        driverid = None
    geolocator = Nominatim(user_agent="[PlaceHolder]")
    departurelocation = geolocator.geocode(form.start.data)
    arrivallocation = geolocator.geocode(form.destination.data)
    #departure_location_lat = uniform(49.536612, 51.464020)
    #departure_location_long = uniform(2.634966, 6.115877)
    #arrival_location_lat = uniform(49.536612, 51.464020)
    #arrival_location_long = uniform(2.634966, 6.115877)
    d = form.date.data
    route = Route(creator=creatorname, departure_location_lat=departurelocation.latitude,
                             departure_location_long=departurelocation.longitude, arrival_location_lat=arrivallocation.latitude,
                             arrival_location_long=arrivallocation.longitude, driver_id=driverid, departure_time=d)
    db.session.add(route)
    db.session.commit()


@app.route('/addroute', methods=['GET', 'POST'])
@login_required
def addRoute():
    # flash("Warning: this page won't submit anything to the database yet. We're working on it.")
    form = AddRouteForm()
    if form.validate_on_submit():
        if (form.date.data < date.today()):
            flash("Date is invalid")
            return render_template('addRoute.html', title='New Route', form=form)
        createRoute(form)
        flash('New route added')
        return redirect(url_for('index'))
    return render_template('addRoute.html', title='New Route', form=form)


@app.route('/requests', methods=['GET'])
@login_required
def getRequests():

    request_query = RouteRequest.query.filter_by(user_id=current_user.get_id())
    requests = []
    for r in request_query:
        route = Route.query.filter_by(id=r.route_id)
        request = {
            'status': r.status,
            'user': 'John',
            'from': 'Somewhere',
            'to': 'Elsewhere',
            'time': route.departure_time
        }
        requests.append(request)

    return render_template('requests.html', title='Requests', requests=requests)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)  # TODO:, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


def register_user(username: str, firstname: str, lastname: str, password: str) -> int:
    # TODO: prevent duplicate code
    user = User.query.filter_by(username=username).first()
    if user is not None:
        # flash("There is already an user with this username. Please choose another one.")
        return 0

    user = User(username=username, firstname=firstname, lastname=lastname)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user.id


@app.route('/users/register', methods=['POST'])
def register_api():
    username = request.json.get('username')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    password = request.json.get('password')

    id = register_user(username, firstname, lastname, password)

    return {'id': str(id)}


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        register_user(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data,
                      password=form.password.data)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/users/auth')
def auth():
    return render_template('wip.html', title='W.I.P.')


@app.route('/drives')
@login_required
def drives():
    return render_template('wip.html', title='W.I.P.')


# Driver id and passenger id can be variable!
@app.route('/drives/<drive_id>/passengers')
@login_required
def drivePassengers(drive_id):
    return render_template('wip.html', title='W.I.P.')


@app.route('/drives/<drive_id>/passenger-requests')
@login_required
def passengerRequests(drive_id):
    return render_template('wip.html', title='W.I.P.')

@app.route('/drives/<drive_id>/request')
@login_required
def request_drive(drive_id):
    request = RouteRequest(route_id=drive_id, user_id=current_user.id)
    db.session.add(request)
    db.session.commit()
    flash("Request has been made")
    return redirect(url_for("index"))


@app.route('/drives/<drive_id>/passenger-requests/<user_id>', methods=['GET', 'POST'])
@login_required
def passenger_request(drive_id, user_id):
    form = RequestForm()
    trip = Route.query.filter_by(id=drive_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()
    request = RouteRequest.query.filter_by(route_id=drive_id, user_id=user_id).first_or_404()

    if request.status == RequestStatus.accepted:
        flash("This route request has already been accepted")
        return redirect(url_for("index"))
    if request.status == RequestStatus.rejected:
        flash("This route request has already been rejected")
        return redirect(url_for("index"))

    if form.validate_on_submit():
        if form.accept.data:
            request.status = RequestStatus.accepted
            db.session.commit()
            flash("The route request was successfully accepted.")
        elif form.reject.data:
            request.status = RequestStatus.rejected
            db.session.commit()
            flash("The route request was successfully rejected.")
        return redirect(url_for("index"))

    return render_template('route_request.html', form=form, user=user, trip=trip, title='W.I.P.')


@app.route('/drives/search')
@login_required
def search():
    return render_template('wip.html', title='W.I.P.')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='Page not found'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html', title='Method not allowed'), 405


# Function for deliberatly creating an error (for testing the error mailing system)
@app.route('/internal_server_error')
def internal_server_error():
    user = User(username="johndoe", firstname="John", lastname="Doe")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    return render_template("500.html", title="Internal error")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title='Internal error'), 500
