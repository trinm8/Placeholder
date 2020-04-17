from geopy.exc import GeocoderTimedOut
from geopy.exc import GeocoderQueryError

from app import db, login

from flask import current_app
from flask_login import UserMixin

import jwt
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

from time import time, sleep
from datetime import datetime, timedelta
import dateutil.parser

import enum
import base64
import os

from geopy.geocoders import Nominatim


def get_from_dict(dictionary, *args):
    for word in args:
        if word in dictionary:
            return dictionary[word]
    return ""


def addr(lat, long):
    geolocator = Nominatim(user_agent="[PlaceHolder]")
    print("query")
    try:
        sleep(1.1)
        location = geolocator.reverse(str(lat) + ", " + str(long))
          # sleep for 1 sec (required by Nominatim usage policy)
    except GeocoderTimedOut:
        print("Geocoder timed out")
        return "Geocoder timed out"
    except GeocoderQueryError:
        return "Geocoder errored on query"
    print("succesfull")

    addr_dict = location.raw["address"]

    location_str = ""

    # Address line
    location_str += get_from_dict(addr_dict, "road", "avenue", "street", "cycleway", "pedestrian") + " "
    # Number
    location_str += get_from_dict(addr_dict, "house_number")
    # Only add a ", " if you've already added something so far (that's not a space)
    location_str += ", " if len(location) > 1 else ""
    # Postcode
    location_str += get_from_dict(addr_dict, "postcode") + " "
    # City
    location_str += get_from_dict(addr_dict, "city", "town")

    # When nothing could be added
    if len(location_str) <= 4:
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
    # TODO: I changed this from 32 to 64, but it didn't get updated with flask db migrate,
    #  Drop and add table again to do this probably
    token = db.Column(db.String(64), unique=True)
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
        return jwt.encode({'user_id': self.id, 'exp': expires},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def revoke_token(self):
        self.token_expiration = datetime.now() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        try:
            print(token)
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            print("failed")
            return
        return User.query.get(id)

    def name(self):
        return self.firstname + " " + self.lastname

    def getNotifications(self):
        requests = RouteRequest.query \
            .filter(Route.query
                    .filter_by(driver_id=self.id)
                    .filter_by(id=RouteRequest.route_id)
                    .exists()) \
            .filter_by(status=RequestStatus.pending)

        current_time = datetime.utcnow()
        routes_driver = Route.query.filter_by(driver_id=self.id)
        routes_passenger = Route.query.filter(RouteRequest.query.filter_by(user_id=self.id, route_id=Route.id).exists())
        routes = routes_driver.union(routes_passenger)
        # future_routes = routes.filter(Route.departure_time >= current_time).all()
        future_routes = routes.filter(Route.departure_time > current_time).all()

        notifications = []
        if (len(future_routes) > 0):
            f = "Next route: " + future_routes[0].departure_time.isoformat() + "\n" + future_routes[0].text_to()
            notifications.append(f)
        else:
            notifications.append("No routes planned in the future")

        for request in requests:
            notifications.append(request)

        return notifications


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # creator = db.Column(db.String(64))
    departure_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    departure_location_lat = db.Column(db.Float(precision=53))
    departure_location_long = db.Column(db.Float(precision=53))
    departure_location_string = db.Column(db.String(256))
    arrival_location_lat = db.Column(db.Float(precision=53))
    arrival_location_long = db.Column(db.Float(precision=53))
    arrival_location_string = db.Column(db.String(256))
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    passenger_places = db.Column(db.Integer)

    playlist = db.Column(db.String(32))  # Should be the spotify playlist id

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
        if self.departure_location_string:
            return self.departure_location_string
        else:
            return ""
        #return addr(self.departure_location_lat, self.departure_location_long)

    def text_to(self):
        if self.arrival_location_string:
            return self.arrival_location_string
        else:
            return ""
        #return addr(self.arrival_location_lat, self.arrival_location_long)

    def driver(self):
        return User.query.get(self.driver_id)


class RequestStatus(enum.Enum):
    pending = 1
    accepted = 2
    rejected = 3


class RouteRequest(db.Model):
    route_id = db.Column(db.Integer, db.ForeignKey('route.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
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

    def accept(self):
        self.status = RequestStatus.accepted

    def reject(self):
        self.status = RequestStatus.rejected

    def to_dict(self):
        return {
            'id': self.route_id,
            'username': self.user().username,
            'status': self.status.name
        }


class MusicPref(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    genre = db.Column(db.String(64))
    likes = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {} {} genre {}'.format(self.user, 'likes' if self.likes else 'dislikes', self.genre)
