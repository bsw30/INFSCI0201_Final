from .models import User, Event, Organizer
from . import db
from datetime import datetime, timedelta
import random
from sqlalchemy.exc import OperationalError

def create_dummy_data():
    try:
        # Check if there's any data in the database
        if User.query.first() is None:
            # Create organizers
            organizers = [
                Organizer(name="Tech Events Inc.", description="We organize the best tech events in town!"),
                Organizer(name="Business Networking Group", description="Connecting professionals through events")
            ]
            for organizer in organizers:
                db.session.add(organizer)
            db.session.commit()

            # Create users
            users = [
                User(username="john_doe", email="john@example.com", first_name="John", last_name="Doe", role="user"),
                User(username="jane_smith", email="jane@example.com", first_name="Jane", last_name="Smith", role="event_manager", organizer_id=organizers[0].id),
                User(username="bob_johnson", email="bob@example.com", first_name="Bob", last_name="Johnson", role="event_manager", organizer_id=organizers[1].id)
            ]
            for user in users:
                user.set_password("password123")
                db.session.add(user)
            db.session.commit()

            # Create events
            event_types = ["Conference", "Workshop", "Seminar", "Networking"]
            locations = ["New York", "San Francisco", "Chicago", "Los Angeles", "Boston"]
            
            for i in range(10):
                organizer = random.choice([user for user in users if user.role == "event_manager"])
                event = Event(
                    title=f"Event {i+1}",
                    description=f"This is a description for Event {i+1}",
                    date=datetime.now() + timedelta(days=random.randint(1, 30)),
                    location=random.choice(locations),
                    event_type=random.choice(event_types),
                    tags="tech, business",
                    organizer_id=organizer.id,
                    image_url=f"/placeholder.svg?height=300&width=400"
                )
                db.session.add(event)

            db.session.commit()
            print('Dummy data created.')
        else:
            print('Database already contains data. Skipping dummy data creation.')
    except OperationalError:
        print('Database tables not created yet. Run flask db upgrade first.')
    except Exception as e:
        print(f'An error occurred while creating dummy data: {str(e)}')

