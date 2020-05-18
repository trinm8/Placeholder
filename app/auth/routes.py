from app.auth import bp
from flask_login import current_user, logout_user, login_user, login_required
from flask import url_for, redirect, flash, request, render_template
from werkzeug.urls import url_parse
from app.auth.forms import LoginForm, RegistrationForm, ForgotPassword, ResetPasswordForm
from app.models import User, UserAuthentication
from app import db
from app.auth.emails import send_password_reset_email
from flask_babel import _

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # Current user must be from authentication since the new update
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAuthentication.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(User.query.get_or_404(user.id))  # TODO:, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def register_user_func(username: str, firstname: str, lastname: str, password: str) -> int:
    # TODO: prevent duplicate code
    user = UserAuthentication.query.filter_by(username=username).first()
    if user is not None:
        # flash("There is already an user with this username. Please choose another one.")
        return 0

    user = User(firstname=firstname, lastname=lastname)
    db.session.add(user)
    db.session.commit() # Seperate commit to keep the constraints happy
    authentication = UserAuthentication(username=username, id=user.id)
    authentication.set_password(password)
    db.session.add(authentication)
    db.session.commit()
    return user.id


@bp.route('/users/register', methods=['POST'])
def register_api():
    username = request.json.get('username')
    firstname = request.json.get('firstname')
    lastname = request.json.get('lastname')
    password = request.json.get('password')

    id = register_user_func(username, firstname, lastname, password)

    return {'id': str(id)}


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        id = register_user_func(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data,
                           password=form.password.data)
        flash(_('Congratulations, you are now a registered user!'))
        login_user(User.query.get_or_404(id))
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/forgot_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ForgotPassword()
    if form.validate_on_submit():
        user = UserAuthentication.query.filter_by(username=form.username.data).first()
        if user:
            email = form.email.data
            message = _("Check your email for the instructions to reset your password. Check your junk mail too when you didn't receive anything")
            if user.user().email:
                email = user.user().email
                message = _("There was already an email attached to this user, using that one instead. ") + message
            send_password_reset_email(user, email)
            flash(message)
            return redirect(url_for('auth.login'))
        else:
            flash(_('No user found with the given name.'))
            return redirect(url_for('auth.reset_password_request'))
    return render_template('auth/forgot_password.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash("Password reset link not valid")
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.authentication().set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
