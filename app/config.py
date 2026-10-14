import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'msme-navigator-in-secret-key-2026')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'csv', 'docx'}
    
    # Primary PostgreSQL Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:Harshith%401432@127.0.0.1:5432/msme'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DEBUG = False
    TESTING = False
    DEFAULT_LANGUAGE = 'en'
    SUPPORTED_LANGUAGES = ['en', 'hi', 'kn', 'te', 'ta', 'ml', 'mr', 'gu', 'bn']

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
