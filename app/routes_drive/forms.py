from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, DateTimeField, SubmitField, ValidationError, IntegerField
from wtforms.fields.html5 import DecimalRangeField


class AddRouteForm(FlaskForm):
    type = RadioField('type', choices=[('Driver', 'Driver'), ('Passenger', 'Passenger')])
    start = StringField('start')
    places = IntegerField('Passenger places')
    playlist = StringField('Spotify playlist ID')
    destination = StringField('destination')
    date = DateTimeField('date', format='%d/%m/%Y %H:%M')
    submit = SubmitField('Confirm')

    def validate_playlist(self, playlist):
        if len(playlist.data) > 32:
            raise ValidationError('Be sure to only enter the ID of the playlist.\n'
                                  'The playlist ID are all chars after the last "/" and before the "?" '
                                  'in the link you use to share a playlist')

class EditRouteForm(FlaskForm):
    start = StringField('start')
    destination = StringField('destination')
    playlist = StringField('Spotify playlist ID')
    places = IntegerField('Passenger places')
    date = DateTimeField('date', format='%d/%m/%Y %H:%M')
    submit = SubmitField('Save Changes')

    def validate_playlist(self, playlist):
        if len(playlist.data) > 32:
            raise ValidationError('Be sure to only enter the ID of the playlist.\n'
                                  'The playlist ID are all chars after the last "/" and before the "?" '
                                  'in the link you use to share a playlist')

class RouteSearchForm(FlaskForm):
    start = StringField('start')
    destination = StringField('destination')
    date = DateTimeField('date', format='%d/%m/%Y %H:%M')
    distance = DecimalRangeField('Age', default=2)
    # https://stackoverflow.com/questions/31136882/displaying-slider-value-alongside-wtforms-fields-html5-decimalrangefield
    submit = SubmitField('Search')

class RequestForm(FlaskForm):
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')


class SendRequestForm(FlaskForm):
    submit = SubmitField('Send Request')
