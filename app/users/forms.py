from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


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
