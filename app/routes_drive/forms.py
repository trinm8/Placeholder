from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, DateField, SubmitField


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
