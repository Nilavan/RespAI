from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default='test')
    phone = db.Column(db.String(10), default='test')
    result = db.Column(db.String)
    probability = db.Column(db.Float)
    #verify = db.Column(db.Bool)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Patient')
