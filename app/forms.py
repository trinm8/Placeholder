from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    login = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username. The given one is already used.')


class ForgotPassword(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')


class Settings(FlaskForm):
    # Profile settings
    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password')
    submit_profile = SubmitField("Update Profile")

    # Music settings
    liked_genre = StringField('Liked Genre')
    disliked_genre = StringField('Disliked Genre')
    submit_liked = SubmitField("Add")
    submit_disliked = SubmitField("Add")

    # Car settings
    color = StringField('Color', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    plate = StringField('License plate', validators=[DataRequired()])
    submit_car = SubmitField("Update Car")


class AddRouteForm(FlaskForm):
    type = RadioField('type', choices=[('Driver', 'Driver'), ('Passenger', 'Passenger')])
    start = StringField('start')
    destination = StringField('destination')
    date = DateField('date', format='%m/%d/%Y')
    submit = SubmitField('Confirm')


class RequestForm(FlaskForm):
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')


class SendRequestForm(FlaskForm):
    submit = SubmitField('Send Request')
