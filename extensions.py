"""Extensions module.

This module contains the SQLAlchemy and Flask-Login extension instances.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize SQLAlchemy with no session options
db = SQLAlchemy()

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'