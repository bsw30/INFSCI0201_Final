from . import db
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User model to handle user information and password hashing
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    # Relationships
    participants = db.relationship('Participant', backref='user_participant', lazy=True)  # Changed backref to 'user_participant'
    notifications = db.relationship('Notification', backref='user_notifications', lazy=True)  # Changed backref to 'user_notifications'

    # Set the user's password (hash it)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check the user's password (compare the hash)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Event model to handle event details
class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), nullable=False)

    # Foreign keys
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.venue_id'))

    # Relationships
    participants = db.relationship('Participant', backref='event_participant', lazy=True)  # Changed backref to 'event_participant'
    feedback = db.relationship('Feedback', backref='event_feedback', lazy=True)

    def __repr__(self):
        return f"<Event {self.name}>"

# Participant model to link users with events
class Participant(db.Model):
    participant_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    status = db.Column(db.String(20), nullable=False)

    # Relationships
    user = db.relationship('User', backref='participants')  # This backref is now 'participants'
    event = db.relationship('Event', backref='participants')


# Notification model to handle user notifications related to events
class Notification(db.Model):
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='user_notifications')  # This backref is now 'user_notifications'
    event = db.relationship('Event', backref='notifications')


# Feedback model to handle feedback from participants for events
class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.participant_id'))
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    event = db.relationship('Event', backref='feedback')
    participant = db.relationship('Participant', backref='feedback')


# Database initialization script
def init_db():
    db.create_all()


