from geopy.exc import GeocoderTimedOut
from geopy.exc import GeocoderQueryError

from app import db, login

from flask import current_app, url_for
from flask_login import UserMixin

from flask_babel import _

import jwt
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

from time import time, sleep
from datetime import datetime, timedelta
import dateutil.parser

from urllib.parse import quote

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
        return _("Geocoder timed out")
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

    return _(location_str)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Statistics(db.Model):
    rickroll_counter = db.Column(db.Integer, primary_key=True)

class UserAuthentication(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def get_token(self, expires=3600):
        return jwt.encode({'user_id': self.id, 'exp': time() + expires},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def user(self):
        return User.query.get(self.id)

class Car(db.Model):
    # Car properties
    color = db.Column(db.String(64), index=True)
    brand = db.Column(db.String(64), index=True)
    plate = db.Column(db.String(32), index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True) # Each user can have max 1 car

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True)
    lastname = db.Column(db.String(64), index=True)
    # age = db.Column(db.Integer)
    email = db.Column(db.String(120), index=True, unique=True)

    # Music preferences
    musicpref = db.relationship('MusicPref')

    def authentication(self):
        return UserAuthentication.query.get(self.id)

    def username(self):
        return UserAuthentication.query.with_entities(UserAuthentication.username).filter_by(id=self.id).first().username

    def car(self):
        return Car.query.get(self.id)

    def to_dict(self):
        car_color = car_plate = car_brand = None
        car_entity = self.car()
        if car_entity:
            car_color = car_entity.color
            car_brand = car_entity.brand
            car_plate = car_entity.plate
        data = {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "username": self.username(),
            "email": self.email,
            "car_color": _(car_color),
            "car_plate": car_plate,
            "car_brand": car_brand
        }
        return data

    def from_dict(self, data):
        if "username" in data:
            self.username = data["username"]
        if "firstname" in data:
            self.firstname = data["firstname"]
        if "lastname" in data:
            self.lastname = data["lastname"]
        if "email" in data:
            self.email = data["email"]
        if "car_color" in data:
            self.car().color = data["car_color"]
        if "car_plate" in data:
            self.car().plate = data["car_plate"]
        if "car_brand" in data:
            self.car().brand = data["car_brand"]

    def __repr__(self):
        return '<User {} {}>'.format(self.firstname, self.lastname)

    def avatar(self, size):
        digest = md5(self.username().lower().encode('utf-8')).hexdigest()
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

    @staticmethod
    def check_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['user_id']
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
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
        future_routes_unsort = routes.filter(Route.departure_time > current_time).all()
        # ORDER BY
        future_routes = []
        if future_routes_unsort:
            future_routes.append(future_routes_unsort[0])
        for unsort_route in future_routes_unsort:
            temp_routes = []
            for route in future_routes:
                if route.departure_time > unsort_route.departure_time:
                    temp_routes.append(unsort_route)

                temp_routes.append(route)
            future_routes = temp_routes

        notifications = []
        if (len(future_routes) > 0):
            # f = "Next route: " + future_routes[0].departure_time.isoformat() + "\n" + future_routes[0].text_to()
            notifications.append(future_routes[0])
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
    maximum_deviation = db.Column(db.FLOAT(precision=3))

    playlist = db.Column(db.String(32))  # Should be the spotify playlist id

    def __repr__(self):
        return '<Route from {}, {} to {}, {}>'.format(self.departure_location_lat, self.departure_location_long,
                                                      self.arrival_location_lat, self.arrival_location_long)

    def to_dict(self):
        data = {
            "id": self.id,
            "driver-id": self.driver_id,
            "passenger-ids": self.passengers(),  # TODO: test whether this works
            "passenger-places": self.passenger_places,
            "from": [self.departure_location_lat, self.departure_location_long],
            "to": [self.arrival_location_lat, self.arrival_location_long],
            "arrive-by": self.departure_time.isoformat() + ".00"  # include milliseconds
        }
        return data

    def from_dict(self, data):
        if "from" in data:
            self.departure_location_lat, self.departure_location_long = data["from"]
            self.departure_location_string = addr(self.departure_location_lat, self.departure_location_long)
        if "to" in data:
            self.arrival_location_lat, self.arrival_location_long = data["to"]
            self.arrival_location_string = addr(self.arrival_location_lat, self.arrival_location_long)
        if "passenger-places" in data:
            self.passenger_places = data["passenger-places"]
        if "arrive-by" in data:
            # src: https://stackoverflow.com/questions/969285/how-do-i-translate-an-iso-8601-datetime-string-into-a-python-datetime-object
            self.departure_time = dateutil.parser.parse(data["arrive-by"])
        self.maximum_deviation = 15

    def text_from(self):
        if self.departure_location_string:
            return self.departure_location_string
        else:
            self.departure_location_string = addr(self.departure_location_lat, self.departure_location_long)
            return self.departure_location_string
        # return addr(self.departure_location_lat, self.departure_location_long)

    def text_to(self):
        if self.arrival_location_string:
            return self.arrival_location_string
        else:
            self.arrival_location_string = addr(self.arrival_location_lat, self.arrival_location_long)
            return self.arrival_location_string
        # return addr(self.arrival_location_lat, self.arrival_location_long)

    def driver(self):
        return User.query.get(self.driver_id)

    def places_left(self):
        try:
            current_passengers = self.passengers()
            return self.passenger_places - len(current_passengers)
        except:
            return 0

    # Returns a list of the passenger id's
    def passengers(self):
        # return RouteRequest.query(RouteRequest.user_id).filter_by(route_id=self.id, status=RequestStatus.accepted).all()
        passengers = RouteRequest.query.filter_by(route_id=self.id, status=RequestStatus.accepted).all()
        passenger_ids = []
        for passenger in passengers:
            passenger_ids.append(passenger.user_id)
        return passenger_ids

    def google_calendar_link(self):
        start_time = self.departure_time.isoformat() # "20180512T230000Z"
        end_time = (self.departure_time + timedelta(hours=1)).isoformat()

        # Remove the '-' and ':' from the time
        translation_table = dict.fromkeys(map(ord, '-:'), None) # We want to replace the '-' and ':' with Nothing)
        start_time = start_time.translate(translation_table)
        end_time = end_time.translate(translation_table)

        base_url = "https://calendar.google.com/calendar/r/eventedit"

        description = "Your trip from {from_} to {to_}. For details, link here: {route_url}" \
            .format(from_=self.text_from(),
                    to_=self.text_to(),
                    route_url=url_for('routes_drive.drive', drive_id=self.id, _external=True))

        parameters = "?text={event_name}&dates={start_time}/{end_time}&details={description}&location={location}"

        parameters = parameters.format(event_name="[PlaceHolder] Trip",
                                       start_time=start_time,
                                       end_time=end_time,
                                       description=quote(description),
                                       location=quote(self.text_from()))
        # quote encodes the special characters in a string to e.g. %20

        return base_url + parameters


class RequestStatus(enum.Enum):
    pending = 1
    accepted = 2
    rejected = 3


class RouteRequest(db.Model):
    route_id = db.Column(db.Integer, db.ForeignKey('route.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    status = db.Column(db.Enum(RequestStatus))
    time_created = db.Column(db.DateTime)
    time_updated = db.Column(db.DateTime)

    def __init__(self, route_id, user_id):
        self.status = RequestStatus.pending
        self.route_id = route_id
        self.user_id = user_id
        self.time_created = datetime.utcnow()

    def route(self):
        return Route.query.get(self.route_id)

    def user(self):
        return User.query.get(self.user_id)

    def accepted(self):
        return self.status == RequestStatus.accepted

    def accept(self):
        self.time_updated = datetime.utcnow()
        self.status = RequestStatus.accepted

    def reject(self):
        self.time_updated = datetime.utcnow()
        self.status = RequestStatus.rejected

    def to_dict(self):
        data = {
            'id': self.user_id,
            'username': self.user().username(),
            'status': self.status.name,
            'time-created': self.time_created.isoformat() + '.00'
        }
        if self.time_updated is not None:
            data['time-updated'] = self.time_updated.isoformat() + '.00'
        return data


class MusicPref(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    genre = db.Column(db.String(64))
    likes = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {} {} genre {}'.format(self.user, 'likes' if self.likes else 'dislikes', self.genre)
