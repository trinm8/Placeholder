from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, DateTimeField, SubmitField


class AddRouteForm(FlaskForm):
    type = RadioField('type', choices=[('Driver', 'Driver'), ('Passenger', 'Passenger')])
    start = StringField('start')
    destination = StringField('destination')
    date = DateTimeField('date', format='%d/%m/%Y %H:%M')
    submit = SubmitField('Confirm')


class RequestForm(FlaskForm):
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')


class SendRequestForm(FlaskForm):
    submit = SubmitField('Send Request')
