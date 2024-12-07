# app/routes/events.py

import os
import requests
from flask import Blueprint, render_template
from app import db
from app.models import Event
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get the Eventbrite API key from the environment
EVENTBRITE_API_KEY = os.getenv('EVENTBRITE_API_KEY')

# Create the blueprint for the events route
events_bp = Blueprint('events_bp', __name__)

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

def fetch_events_from_api():
    """Fetch events from the Eventbrite API."""
    if not EVENTBRITE_API_KEY:
        return [{"error": "API key is missing"}]  # Return error message if the API key is missing

    url = "https://www.eventbriteapi.com/v3/events/search/"
    params = {
        "location.address": "Pittsburgh, PA",  # Specify location for the API query
        "token": EVENTBRITE_API_KEY  # Include the API key for authentication
    }

    try:
        response = requests.get(url, params=params)
        if response and response.status_code == 200:
            return response.json().get('events', [])
        else:
            return [{
                "error": f"Failed to fetch events. Status Code: {response.status_code if response else 'No response'}"}]
    except requests.exceptions.RequestException as e:
        # Catch network errors or API issues
        return [{"error": f"Request failed: {str(e)}"}]

def fetch_event_details_by_id(event_id):
    """Fetch the details of a single event by its event_id."""
    if not EVENTBRITE_API_KEY:
        return {"error": "API key is missing"}  # Return error message if the API key is missing

    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/"
    params = {
        "token": EVENTBRITE_API_KEY  # Include the API key for authentication
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()  # Return the event details
        elif response.status_code == 429:
            return [{"error": "API rate limit exceeded, please try again later."}]
        else:
            return [{"error": f"Failed to fetch events. Status Code: {response.status_code}"}]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Request failed: {str(e)}"}]
