from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, DateTimeField, SubmitField, ValidationError, IntegerField
from wtforms.validators import DataRequired, InputRequired
from wtforms.fields.html5 import DecimalRangeField

from flask_babel import lazy_gettext as _l


class AddRouteForm(FlaskForm):
    type = RadioField(_l('type'), choices=[('Driver', _l('Driver')), ('Passenger', _l('Passenger'))], validators=[DataRequired()]) # TODO: wich one to translate?
    start = StringField(_l('start'), validators=[DataRequired()])
    places = IntegerField(_l('Passenger places'), validators=[])
    playlist = StringField(_l('Spotify playlist ID'))
    destination = StringField(_l('destination'), validators=[DataRequired()])
    date = DateTimeField(_l('date'), format='%d/%m/%Y %H:%M', validators=[InputRequired()])
    submit = SubmitField(_l('Confirm'))

    def validate_playlist(self, playlist):
        if len(playlist.data) > 32:
            raise ValidationError(_l('Be sure to only enter the ID of the playlist.\n'
                                  'The playlist ID are all chars after the last "/" and before the "?" '
                                  'in the link you use to share a playlist'))


class EditRouteForm(FlaskForm):
    start = StringField(_l('start'))
    destination = StringField(_l('destination'))
    playlist = StringField(_l('Spotify playlist ID'))
    places = IntegerField(_l('Passenger places'))
    date = DateTimeField(_l('date'), format='%d/%m/%Y %H:%M')
    submit = SubmitField(_l('Save Changes'))

    def validate_playlist(self, playlist):
        if len(playlist.data) > 32:
            raise ValidationError(_l('Be sure to only enter the ID of the playlist.\n'
                                  'The playlist ID are all chars after the last "/" and before the "?" '
                                  'in the link you use to share a playlist'))


class RouteSearchForm(FlaskForm):
    start = StringField(_l('start'))
    destination = StringField(_l('destination'))
    date = DateTimeField(_l('date'), format='%d/%m/%Y %H:%M')
    distance = DecimalRangeField(_l('Age'), default=2)
    # https://stackoverflow.com/questions/31136882/displaying-slider-value-alongside-wtforms-fields-html5-decimalrangefield
    submit = SubmitField(_l('Search'))


class RequestForm(FlaskForm):
    accept = SubmitField(_l('Accept'))
    reject = SubmitField(_l('Reject'))


class SendRequestForm(FlaskForm):
    pickupPoint = StringField(_l('pickup'), validators=[DataRequired()])
    submit = SubmitField(_l('Send Request'))
