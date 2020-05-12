from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import DataRequired

from flask_babel import lazy_gettext as _l


class Settings(FlaskForm):
    # Profile settings
    firstname = StringField(_l('First name'), validators=[DataRequired()])
    lastname = StringField(_l('Last name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'))
    submit_profile = SubmitField(_l("Update Profile"))

    # Music settings
    liked_genre = StringField(_l('Liked Genre'))
    disliked_genre = StringField(_l('Disliked Genre'))
    submit_liked = SubmitField(_l("Add"))
    submit_disliked = SubmitField(_l("Add"))

    # Car settings
    color = StringField(_l('Color'), validators=[DataRequired()])
    brand = StringField(_l('Brand'), validators=[DataRequired()])
    plate = StringField(_l('License plate'), validators=[DataRequired()])
    submit_car = SubmitField(_l("Update Car"))


class ReviewForm(FlaskForm):
    score = FloatField(_l('Score'))
    review_text = StringField(_l('Review text'))
    submit_review = SubmitField(_l("Submit"))
