#app/main.py

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app import db  # Assuming you're importing the db instance
from app.models import Event  # Assuming your Event model is in 'models.py'
from datetime import datetime

# Define the blueprint for the 'main' section of the app
main = Blueprint('main', __name__)


# Route for the dashboard page, requires login
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# Route for the venues page, requires login
@main.route('/venues')
@login_required
def venues():
    return render_template('venues.html')


# Route for the participants page, requires login
@main.route('/participants')
@login_required
def participants():
    return render_template('participants.html')


# Route for the events page, requires login
@main.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    if request.method == 'POST':
        # Handle the form submission to create a new event
        event_name = request.form['name']
        event_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        event_start_time = request.form['start_time']
        event_end_time = request.form['end_time']
        event_location = request.form['location']
        event_description = request.form['description']

        # Create a new Event instance and add it to the database
        new_event = Event(name=event_name, date=event_date, start_time=event_start_time,
                          end_time=event_end_time, location=event_location, description=event_description)

        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('main.events'))

    # If the request method is GET, display existing events
    events = Event.query.all()  # Fetch all events from the database
    return render_template('events.html', events=events)


# Route for the reports page, requires login
@main.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

