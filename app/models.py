from app import db, login, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt
from time import time
import enum
import dateutil.parser


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
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


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

class MusicPref(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    genre = db.Column(db.String(64))
    likes = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {} {} genre {}'.format(self.user, 'likes' if self.likes else 'dislikes', self.genre)
