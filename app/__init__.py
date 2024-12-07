# app/__init__.py

import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()

# Load environment variables from .env file
load_dotenv()

# Initialize Flask extensions
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///event_planner.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint  # Make sure you have a main blueprint
    app.register_blueprint(main_blueprint)

    from .routes.events import events_bp  # Events blueprint
    app.register_blueprint(events_bp, url_prefix='/events')  # Registering events blueprint with URL prefix

    # Create database tables (only run once, ideally in a separate script for migrations)
    with app.app_context():
        db.create_all()

    # Define the user_loader function for Flask-Login
    from .models import User  # Import here to avoid circular import
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Retrieve the user by ID from the database

    # Example route
    @app.route('/')
    def home():
        return render_template('landing.html')

    return app