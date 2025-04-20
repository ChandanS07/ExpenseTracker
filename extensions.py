"""Extensions module.

This module contains the SQLAlchemy and Flask-Login extension instances.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize SQLAlchemy extension without an app
db = SQLAlchemy()

# Initialize login manager without an app
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'