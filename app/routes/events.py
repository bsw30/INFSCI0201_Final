from flask import Blueprint, render_template
from datetime import datetime
from app import db
from app.models import Event
from sqlalchemy.exc import OperationalError

# Create a Blueprint for event routes
events_bp = Blueprint('events', __name__)

# Route for landing page (viewing upcoming events)
@events_bp.route('/')
def landing_page():
    today = datetime.today().date()
    try:
        # Query the database for events
        events = Event.query.filter(Event.date >= today).order_by(Event.date).all()
    except OperationalError:
        # Return an empty list if the database query fails
        events = []
        db.session.rollback()  # Rollback to prevent any open transactions

    return render_template('landing_page.html', events=events)

# In your events.py (routes file)
@events_bp.route('/upcoming_events')
def upcoming_events():
    today = datetime.today().date()
    try:
        events = Event.query.filter(Event.date >= today).order_by(Event.date).all()
    except OperationalError:
        events = []
        db.session.rollback()  # Rollback to prevent any open transactions

    return render_template('upcoming_events.html', events=events)
