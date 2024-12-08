from .models import User, Event, Organizer
from . import db
from datetime import datetime
from sqlalchemy.exc import OperationalError
from .eventbrite_sync import EventbriteSync
import os

def create_dummy_data():
    try:
        # Create organizers if they don't exist
        if Organizer.query.first() is None:
            organizers = [
                Organizer(name="Tech Events Inc.", description="We organize the best tech events in town!"),
                Organizer(name="Business Networking Group", description="Connecting professionals through events")
            ]
            for organizer in organizers:
                db.session.add(organizer)
            db.session.commit()
            print('Organizers created.')

        # Create users if they don't exist
        if User.query.first() is None:
            users = [
                User(username="john_doe", email="john@example.com", first_name="John", last_name="Doe", role="user"),
                User(username="jane_smith", email="jane@example.com", first_name="Jane", last_name="Smith", role="event_manager", organizer_id=1),
                User(username="bob_johnson", email="bob@example.com", first_name="Bob", last_name="Johnson", role="event_manager", organizer_id=2)
            ]
            for user in users:
                user.set_password("password123")
                db.session.add(user)
            db.session.commit()
            print('Users created.')

        # Initialize EventbriteSync and fetch events
        print("Initializing Eventbrite sync...")
        sync = EventbriteSync()
        stats = sync.sync_events()
        print(f'Eventbrite sync complete: {stats["new"]} new events, {stats["failed"]} failed')

        # Create some dummy events if no events exist
        if Event.query.first() is None:
            dummy_events = [
                Event(
                    title="Tech Conference 2024",
                    description="Annual tech conference showcasing the latest innovations",
                    date=datetime(2024, 6, 15, 9, 0),
                    location="San Francisco Convention Center",
                    event_type="Conference",
                    tags="tech,innovation,networking",
                    organizer_id=1,
                    image_url="https://example.com/tech-conf-2024.jpg"
                ),
                Event(
                    title="Business Networking Lunch",
                    description="Monthly networking event for professionals",
                    date=datetime(2024, 3, 10, 12, 0),
                    location="Downtown Business Center",
                    event_type="Networking",
                    tags="business,networking,lunch",
                    organizer_id=2,
                    image_url="https://example.com/business-lunch.jpg"
                )
            ]
            for event in dummy_events:
                db.session.add(event)
            db.session.commit()
            print('Dummy events created.')

    except OperationalError:
        print('Database tables not created yet. Run flask db upgrade first.')
    except Exception as e:
        print(f'An error occurred while creating dummy data: {str(e)}')
        db.session.rollback()

def schedule_event_updates(scheduler):
    scheduler.add_job(create_dummy_data, 'interval', hours=24)