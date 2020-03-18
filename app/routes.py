from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.email import send_password_reset_email
from app.forms import *
from app.models import User
from werkzeug.urls import url_parse


@app.route('/forgot_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ForgotPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            send_password_reset_email(user, form.email.data)
            flash("Check your email for the instructions to reset your password. Check your junk mail too when you didn't receive anything")
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


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route('/users/<username>')
@login_required
def user_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title='Account', user=user)


@app.route('/account/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    flash("Warning: this page won't submit anything to the database yet. We're working on it.")

    form_profile = ProfileSettings()
    if form_profile.validate_on_submit():
        user = User.query.filter_by(id=current_user.get_id()).first()
        user.firstname = form_profile.firstname.data
        user.lastname = form_profile.lastname.data
        user.email = form_profile.email.data
        if len(form_profile.password.data) > 0:
            user.set_password(form_profile.password.data)
        db.session.commit()

    form_music = MusicSettings()
    if form_music.validate_on_submit():
        user = User.query.filter_by(id=current_user.get_id()).first()
        # TODO(Sam): etc...

    form_car = CarSettings()
    if form_car.validate_on_submit():
        user = User.query.filter_by(id=current_user.get_id()).first()
        user.car_color = form_car.color
        user.car_brand = form_car.brand
        user.car_plate = form_car.plate
        db.session.commit()

    return render_template('settings.html', title='Account Settings', form_profile=form_profile, form_music=form_music,
                           form_car=form_car)


@app.route('/addroute')
@login_required
def addRoute():
    form = AddRoute()
    flash("Warning: this page won't submit anything to the database yet. We're working on it.")
    return render_template('addRoute.html', title='New Route', form=form)


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


@app.route('/drives/<drive_id>/passenger-requests/<user_id>')
@login_required
def user(drive_id, user_id):
    return render_template('wip.html', title='W.I.P.')


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
