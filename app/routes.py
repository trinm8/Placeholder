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
