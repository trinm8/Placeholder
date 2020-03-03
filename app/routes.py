from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', title='Welcome')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # user = {'username': 'Arno'}
    # return render_template('flask test.html', user=user)
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for {}'.format(form.email.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)

@app.route('/users/register')
def register():
    return render_template('wip.html', title='W.I.P.')

@app.route('/users/auth')
def auth():
    return render_template('wip.html', title='W.I.P.')

@app.route('/drives')
def drives():
    return render_template('wip.html', title='W.I.P.')

# Driver id and passenger id can be variable!
@app.route('/drives/<drive_id>/passengers')
def drivePassengers(drive_id):
    return render_template('wip.html', title='W.I.P.')

@app.route('/drives/<drive_id>/passenger-requests')
def passengerRequests(drive_id):
    return render_template('wip.html', title='W.I.P.')

@app.route('/drives/<drive_id>/passenger-requests/<user_id>')
def user(drive_id, user_id):
    return render_template('wip.html', title='W.I.P.')

@app.route('/drives/search')
def search():
    return render_template('wip.html', title='W.I.P.')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='Page not found')


