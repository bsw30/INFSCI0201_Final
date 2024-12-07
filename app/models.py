from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    role = db.Column(db.String(20), default='user')
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer.id'))
    organized_events = db.relationship('Event', backref='organizer', lazy=True)
    attending_events = db.relationship('Event', 
                                       secondary='event_attendees',
                                       backref=db.backref('attendees', lazy='dynamic'),
                                       lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_attending(self, event):
        return self.attending_events.filter_by(id=event.id).first() is not None

    def is_event_manager(self):
        return self.role == 'event_manager'

class Organizer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    managers = db.relationship('User', backref='organizer', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(200))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(200))

    @property
    def attendee_count(self):
        return self.attendees.count()

    def add_attendee(self, user):
        if not self.is_user_attending(user):
            self.attendees.append(user)
            db.session.commit()
            return True
        return False

    def remove_attendee(self, user):
        if self.is_user_attending(user):
            self.attendees.remove(user)
            db.session.commit()
            return True
        return False

    def is_user_attending(self, user):
        return self.attendees.filter_by(id=user.id).first() is not None

event_attendees = db.Table('event_attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('signup_date', db.DateTime, default=datetime.utcnow)
)

