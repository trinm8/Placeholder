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

class ProfileSettings(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password')


# TODO(Sam): Figure out how to do this with text areas for music settings
class MusicSettings(FlaskForm):
    liked_genres = StringField('Liked Genres')
    disliked_genres = StringField('disliked Genres')


class CarSettings(FlaskForm):
    color = StringField('Color', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    plate = StringField('License plate', validators=[DataRequired()])


class AddRoute(FlaskForm):
    type = RadioField('type', choices=[('value', 'Driver'), ('value_2', 'Passenger')], validators=[DataRequired()])
    start = StringField('start', validators=[DataRequired()])
    destination = StringField('destination', validators=[DataRequired()])
    date = DateField('date', format='%d-%m-%Y', validators=[DataRequired()])
    submit = SubmitField('Confirm')
