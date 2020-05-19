from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from ..models import UserAuthentication
from wtforms.validators import DataRequired, EqualTo, Email, Length

from flask_babel import lazy_gettext as _l


class ForgotPassword(FlaskForm):
    username = StringField(_l('username'), validators=[DataRequired(), Length(max=64)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField(_l('Send Reset Link'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Update Password'))


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(max=64)])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    login = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(max=64)])
    firstname = StringField(_l('First name'), validators=[DataRequired(), Length(max=64)])
    lastname = StringField(_l('Last name'), validators=[DataRequired(), Length(max=64)])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')]) # TODO: wat doet die EqualTo('password')? Schrijf comments
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = UserAuthentication.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username. The given one is already used.'))
