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

PREFIX = "/web"

@app.route(PREFIX + '/lol')
def lol():
    counter = Statistics.query.first()
    if counter is None:
        counter = Statistics(rickroll_counter=0)
        db.session.add(counter)
    counter.rickroll_counter += 1
    db.session.commit()
    return redirect("https://www.youtube.com/watch?v=cvh0nX08nRw")

@app.route(PREFIX + '/forgot_password', methods=['GET', 'POST'])
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


@app.route(PREFIX + '/reset_password/<token>', methods=['GET', 'POST'])
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


@app.route(PREFIX + '/index')
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


@app.route(PREFIX + '/about')
def about():
    counter = Statistics.query.first()
    if counter is None:
        counter = "over 9000"
    else:
        counter = counter.rickroll_counter
    return render_template('about.html', title='About', counter=counter)


# @app.route('/account')
# @login_required
# def account():
#     return render_template('account.html', title='Account')


@app.route(PREFIX + '/users/<username>')
@login_required
def user_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title='Account', user=user)


@app.route(PREFIX + '/account/settings', methods=['GET', 'POST'])
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


@app.route(PREFIX + '/addroute', methods=['GET', 'POST'])
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


@app.route(PREFIX + '/requests', methods=['GET'])
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


@app.route(PREFIX + '/login', methods=['GET', 'POST'])
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


@app.route(PREFIX + '/logout')
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


@app.route(PREFIX + '/users/register', methods=['POST'])
def register_api():
    username = request.json.get('username')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    password = request.json.get('password')

    id = register_user(username, firstname, lastname, password)

    return {'id': str(id)}


@app.route(PREFIX + '/register', methods=['GET', 'POST'])
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

@app.route(PREFIX + '/drives/<drive_id>', methods=['GET', 'POST'])
@login_required
def drive(drive_id):
    form = SendRequestForm()
    trip = Route.query.get_or_404(drive_id)
    user = User.query.get_or_404(trip.driver_id)

    if form.validate_on_submit():
        request = RouteRequest(route_id=drive_id, user_id=current_user.id)
        db.session.add(request)
        db.session.commit()
        flash("Request has been made")
        return redirect(url_for("index"))

    if RouteRequest.query.filter_by(route_id=drive_id, user_id=current_user.id).first():
        flash("You have already requested acces for this route")
        return redirect(url_for("index"))

    return render_template('request_route.html', form=form, user=user, trip=trip, title='Route Request')


@app.route(PREFIX + '/drives/<drive_id>/passenger-requests/<user_id>', methods=['GET', 'POST'])
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

    return render_template('route_request.html', form=form, user=user, trip=trip, title='Route Request')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='Page not found'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html', title='Method not allowed'), 405


# Function for deliberatly creating an error (for testing the error mailing system)
@app.route(PREFIX + '/internal_server_error')
def internal_server_error():
    user = User(username="johndoe", firstname="John", lastname="Doe")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    return render_template("500.html", title="Internal error")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title='Internal error'), 500
