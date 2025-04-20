"""Flask application factory module."""
import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db, login_manager


def create_app(test_config=None):
    """Create and configure the Flask application."""
    # create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

    # configure the database with SQLite fallback
    database_url = os.environ.get("DATABASE_URL")
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Set SQLite database with absolute path
    sqlite_path = os.path.join(app.instance_path, 'expense_tracker.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{sqlite_path}'
    
    # Only try to use PostgreSQL if DATABASE_URL is provided
    if database_url:
        try:
            import psycopg2
            # Test connection
            psycopg2.connect(database_url)
            # If we get here, the connection was successful
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_recycle": 300,
                "pool_pre_ping": True,
            }
            print("Using PostgreSQL database")
        except Exception as e:
            print(f"Failed to connect to PostgreSQL, falling back to SQLite: {e}")
    else:
        print("DATABASE_URL not provided, using SQLite database")

    # initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login user loader function."""
        from models import User
        return User.query.get(int(user_id))

    # register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)

    # ensure database tables exist
    with app.app_context():
        db.create_all()

    return app