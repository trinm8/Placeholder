from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from werkzeug.urls import url_parse


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', title='Welcome')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
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
        return -1

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
    return render_template('404.html', title='Page not found')

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html', title='Method not allowed')
