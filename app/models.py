from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True)
    lastname = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    # age = db.Column(db.Integer)
    # email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

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


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(64))
    departure_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    departure_location_lat = db.Column(db.Float(precision=53))
    departure_location_long = db.Column(db.Float(precision=53))
    arrival_location_lat = db.Column(db.Float(precision=53))
    arrival_location_long = db.Column(db.Float(precision=53))
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Route from {}, {} to {}, {}>'.format(self.departure_location_lat, self.departure_location_long,
                                                      self.arrival_location_lat, self.arrival_location_long)
