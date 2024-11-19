from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the database
db = SQLAlchemy()

# Initialize the login manager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'  # Make sure to change this
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Example database URI

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.events import events_bp
    from app.routes.users import users_bp
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(users_bp, url_prefix='/users')

    return app
