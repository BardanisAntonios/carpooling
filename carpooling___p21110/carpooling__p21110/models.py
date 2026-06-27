from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), default='user') # 'admin' ή 'user'
    routes = db.relationship('Route', backref='driver', lazy=True)

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_point = db.Column(db.String(100), nullable=False)
    end_point = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    # ΣΤΗΛΗ ΠΟΥ ΓΕΜΙΖΕΙ ΑΠΟ ΤΟ API
    distance_km = db.Column(db.Float, nullable=True) 
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)