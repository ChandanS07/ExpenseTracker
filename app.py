"""Flask application factory module."""
import os
import logging

from flask import Flask

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SESSION_SECRET", "dev-secret-key"),
            # Use SQLite for local development as we're having PostgreSQL connectivity issues
            SQLALCHEMY_DATABASE_URI="sqlite:///expense_tracker.db",
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Initialize extensions
    from extensions import db, login_manager
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import models for creating tables
    with app.app_context():
        from models import User  # noqa: F401
        from models import Expense  # noqa: F401
        db.create_all()
    
    # Register blueprints
    from routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Set up the user loader
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login user loader function."""
        return User.query.get(int(user_id))
    
    return app

# Create the application instance
app = create_app()

# Run the application if executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)