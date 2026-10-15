"""
Compatibility wrapper delegating to backend package.
Maintains 100% backwards compatibility for existing imports and test runners.
"""
from backend import create_app
from backend.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig
from backend.extensions import db

__all__ = ['create_app', 'Config', 'DevelopmentConfig', 'TestingConfig', 'ProductionConfig', 'db']
