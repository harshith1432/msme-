"""
Application-wide extensions initialization.
Re-exports the canonical SQLAlchemy db instance so tests importing
from either app.extensions or backend.extensions share the exact same object.
"""
from app.extensions import db
from flask_migrate import Migrate

migrate = Migrate()

__all__ = ['db', 'migrate']
