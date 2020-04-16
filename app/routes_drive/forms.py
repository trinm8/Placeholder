from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, DateTimeField, SubmitField
from wtforms.fields.html5 import DecimalRangeField


class AddRouteForm(FlaskForm):
    type = RadioField('type', choices=[('Driver', 'Driver'), ('Passenger', 'Passenger')])
    start = StringField('start')
    destination = StringField('destination')
    date = DateTimeField('date', format='%d/%m/%Y %H:%M')
    submit = SubmitField('Confirm')

class EditRouteForm(FlaskForm):
    start = StringField('start')
    destination = StringField('destination')
    date = DateTimeField('date', format='%d/%m/%Y %H:%M')
    submit = SubmitField('Save Changes')

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
