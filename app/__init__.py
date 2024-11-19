from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the db object here
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the db with the app
    db.init_app(app)

    # Import models here to avoid circular import issues
    with app.app_context():
        from . import models

    # Register blueprints
    from .routes.events import events_bp
    app.register_blueprint(events_bp)

    return app