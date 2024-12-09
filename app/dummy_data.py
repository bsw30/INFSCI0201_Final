from .models import User, Event, Organizer, Tag
from . import db
from datetime import datetime
from sqlalchemy.exc import OperationalError
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

   
        # print("Initializing Eventbrite sync...")
        # sync = EventbriteSync()
        # stats = sync.sync_events()
        # print(f'Eventbrite sync complete: {stats["new"]} new events, {stats["failed"]} failed')

    
        if Event.query.first() is None:
            dummy_events = [
                Event(
                    title="Tech Conference 2024",
                    description="Annual tech conference showcasing the latest innovations",
                    date=datetime(2024, 6, 15, 9, 0),
                    location="San Francisco Convention Center",
                    event_type="Conference",
                    organizer_id=1,
                    image_url="https://images.unsplash.com/photo-1531058020387-3be344556be6?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
                ),
                Event(
                    title="Business Networking Lunch",
                    description="Monthly networking event for professionals",
                    date=datetime(2024, 3, 10, 12, 0),
                    location="Downtown Business Center",
                    event_type="Networking",
                    organizer_id=2,
                    image_url="https://example.com/business-lunch.jpg"
                )
            ]
            for event in dummy_events:
                db.session.add(event)
            db.session.commit()

            # Add tags to events
            tech_conf = Event.query.filter_by(title="Tech Conference 2024").first()
            business_lunch = Event.query.filter_by(title="Business Networking Lunch").first()

            tech_tags = ["tech", "innovation", "networking"]
            business_tags = ["business", "networking", "lunch"]

            for tag_name in tech_tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                tech_conf.tags.append(tag)

            for tag_name in business_tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                business_lunch.tags.append(tag)

            db.session.commit()
            print('Dummy events created with tags.')

    except OperationalError:
        print('Database tables not created yet. Run flask db upgrade first.')
    except Exception as e:
        print(f'An error occurred while creating dummy data: {str(e)}')
        db.session.rollback()

