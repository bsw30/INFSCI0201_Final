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
    subscribed_tags = db.relationship('Tag', secondary='user_tag_subscriptions', backref='subscribers')
    subscribed_organizers = db.relationship('Organizer', secondary='user_organizer_subscriptions', backref='subscribers')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_attending(self, event):
        return self.attending_events.filter_by(id=event.id).first() is not None

    def is_event_manager(self):
        return self.role == 'event_manager'

    def subscribe_to_tag(self, tag):
        if tag not in self.subscribed_tags:
            self.subscribed_tags.append(tag)
            db.session.commit()

    def unsubscribe_from_tag(self, tag):
        if tag in self.subscribed_tags:
            self.subscribed_tags.remove(tag)
            db.session.commit()

    def subscribe_to_organizer(self, organizer):
        if organizer not in self.subscribed_organizers:
            self.subscribed_organizers.append(organizer)
            db.session.commit()

    def unsubscribe_from_organizer(self, organizer):
        if organizer in self.subscribed_organizers:
            self.subscribed_organizers.remove(organizer)
            db.session.commit()

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
    tags = db.relationship('Tag', secondary='event_tags', backref='events')
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

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

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

event_tags = db.Table('event_tags',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    extend_existing=True
)

event_attendees = db.Table('event_attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('signup_date', db.DateTime, default=datetime.utcnow)
)


user_tag_subscriptions = db.Table('user_tag_subscriptions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

user_organizer_subscriptions = db.Table('user_organizer_subscriptions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('organizer_id', db.Integer, db.ForeignKey('organizer.id'), primary_key=True)
)

