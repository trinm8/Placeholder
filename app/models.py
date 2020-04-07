from geopy.exc import GeocoderTimedOut

from app import db, login

from flask import current_app
from flask_login import UserMixin

import jwt
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

from time import time
from datetime import datetime, timedelta
import dateutil.parser

import enum
import base64
import os

from geopy.geocoders import Nominatim


def addr(lat, long):
    # https://stackoverflow.com/questions/11390392/return-individual-address-components-city-state-etc-from-geopy-geocoder
    geolocator = Nominatim(user_agent="[PlaceHolder]")
    try:
        location = geolocator.reverse(str(lat) + ", " + str(long))
    except GeocoderTimedOut:
        return "Geocoder timed out :/"

    addr_dict = location.raw["address"]
    try:
        location_str = addr_dict["road"] + " " + addr_dict["house_number"] + ", " + addr_dict["postcode"] + " "
        if "city" in addr_dict:
            location_str += addr_dict["city"]
        elif "town" in addr_dict:
            location_str += addr_dict["town"]
    except:
        try:
            location_str = addr_dict["cycleway"] + ", " + addr_dict["postcode"] + " " + addr_dict["city"]
        except:
            location_str = str(location.address)
    return location_str

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Statistics(db.Model):
    rickroll_counter = db.Column(db.Integer, primary_key=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True)
    lastname = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    # age = db.Column(db.Integer)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Music preferences
    musicpref = db.relationship('MusicPref')

    # Car properties
    car_color = db.Column(db.String(64), index=True)
    car_brand = db.Column(db.String(64), index=True)
    car_plate = db.Column(db.String(32), index=True, unique=True)

    # Authentication tokens
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {} {}>'.format(self.name, self.lastname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=robohash&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def get_token(self, expires=3600):
        now = datetime.now()
        if self.token is not None and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b32encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def name(self):
        return self.firstname + " " + self.lastname

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(64))
    departure_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    departure_location_lat = db.Column(db.Float(precision=53))
    departure_location_long = db.Column(db.Float(precision=53))
    arrival_location_lat = db.Column(db.Float(precision=53))
    arrival_location_long = db.Column(db.Float(precision=53))
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    passenger_places = db.Column(db.Integer)

    def __repr__(self):
        return '<Route from {}, {} to {}, {}>'.format(self.departure_location_lat, self.departure_location_long,
                                                      self.arrival_location_lat, self.arrival_location_long)

    def to_dict(self):
        data = {
            "id": self.id,
            "driver-id": self.driver_id,
            "passenger-ids": [],  # TODO
            "from": [self.departure_location_lat, self.departure_location_long],
            "to": [self.departure_location_lat, self.departure_location_long],
            "arrive-by": self.departure_time.isoformat()
        }
        return data

    def from_dict(self, data):
        if "from" in data:
            self.departure_location_lat, self.departure_location_long = data["from"]
        if "to" in data:
            self.arrival_location_lat, self.arrival_location_long = data["to"]
        if "passenger-places" in data:
            self.passenger_places = data["passenger-places"]
        if "arrive-by" in data:
            # src: https://stackoverflow.com/questions/969285/how-do-i-translate-an-iso-8601-datetime-string-into-a-python-datetime-object
            self.departure_time = dateutil.parser.parse(data["arrive-by"])
            
    def text_from(self):
        return addr(self.departure_location_lat, self.departure_location_long)
    
    def text_to(self):
        return addr(self.arrival_location_lat, self.arrival_location_long)

    def driver(self):
        return User.query.get(self.driver_id)


class RequestStatus(enum.Enum):
    pending = 1
    accepted = 2
    rejected = 3


class RouteRequest(db.Model):
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.Enum(RequestStatus))

    def __init__(self, route_id, user_id):
        self.status = RequestStatus.pending
        self.route_id = route_id
        self.user_id = user_id

    def route(self):
        return Route.query.get(self.route_id)

    def user(self):
        return User.query.get(self.user_id)

    def accepted(self):
        return self.status == RequestStatus.accepted

class MusicPref(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    genre = db.Column(db.String(64))
    likes = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {} {} genre {}'.format(self.user, 'likes' if self.likes else 'dislikes', self.genre)
