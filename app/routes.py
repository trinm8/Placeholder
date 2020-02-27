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
    return "W.I.P."

@app.route('/users/auth')
def register():
    return "W.I.P."

@app.route('/drives')
def register():
    return "W.I.P."

# Driver id and passenger id can be variable!
@app.route('/drives/drive_id/passengers')
def register():
    return "W.I.P."

@app.route('/drives/drive_id/passenger-requests')
def register():
    return "W.I.P."

@app.route('/drives/drive_id/passenger-requests/user-id')
def register():
    return "W.I.P."

@app.route('/drives/search')
def register():
    return "W.I.P."