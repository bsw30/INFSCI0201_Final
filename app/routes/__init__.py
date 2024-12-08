from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Replace with your DB URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import parts of the app (blueprints, models)
        from . import models
        from .users import user_bp  # Example blueprint

        # Register blueprints
        app.register_blueprint(user_bp, url_prefix='/user')

    return app
