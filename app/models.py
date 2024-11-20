from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    participants = db.relationship('Participant', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.venue_id'))
    participants = db.relationship('Participant', backref='event', lazy=True)
    feedback = db.relationship('Feedback', backref='event', lazy=True)

class Participant(db.Model):
    participant_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    status = db.Column(db.String(20), nullable=False)

class Venue(db.Model):
    venue_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    availability_status = db.Column(db.String(20), nullable=False)

class Notification(db.Model):
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.participant_id'))
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Database initialization script
def init_db():
    db.create_all()