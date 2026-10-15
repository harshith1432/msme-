"""
Production-Ready Environment Configuration for MSME Navigator.
Handles dev, test, and production configs with strict validation.
"""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env.local'))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    ENV = os.environ.get('FLASK_ENV', 'production')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'msme-navigator-in-secret-key-2026'
    
    # Path configuration
    BASE_DIR = BASE_DIR
    FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
    TEMPLATES_DIR = os.path.join(FRONTEND_DIR, 'templates')
    STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    STORAGE_LOCAL_ROOT = os.environ.get('STORAGE_LOCAL_ROOT', os.path.join(BASE_DIR, 'uploads'))

    # Security & limits
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'csv', 'docx', 'txt'}
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:Harshith%401432@127.0.0.1:5432/msme'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 1800)),
        'pool_pre_ping': True
    }

    # Storage Backend: 'local' or 's3'
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_BUCKET_PRIVATE = os.environ.get('S3_BUCKET_PRIVATE', 'msme-private-documents')
    S3_BUCKET_KNOWLEDGE = os.environ.get('S3_BUCKET_KNOWLEDGE', 'msme-knowledge-sources')
    S3_REGION = os.environ.get('S3_REGION', 'ap-south-1')

    # Celery & Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
    CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'true').lower() in ('true', '1')

    # i18n
    DEFAULT_LANGUAGE = 'en'
    SUPPORTED_LANGUAGES = ['en', 'hi', 'kn', 'te', 'ta', 'ml', 'mr', 'gu', 'bn']

    # Hugging Face Inference Providers (RAG LLM Layer)
    HF_TOKEN = os.environ.get('HF_TOKEN')
    HF_MODEL = os.environ.get('HF_MODEL', 'meta-llama/Llama-3.2-3B-Instruct')
    HF_PROVIDER = os.environ.get('HF_PROVIDER')
    HF_TIMEOUT_SECONDS = int(os.environ.get('HF_TIMEOUT_SECONDS', 20))
    HF_MAX_RETRIES = int(os.environ.get('HF_MAX_RETRIES', 2))
    HF_MAX_NEW_TOKENS = int(os.environ.get('HF_MAX_NEW_TOKENS', 512))

    # Mandatory RAG Knowledge-Base Boundaries & Refusals
    RAG_REFUSAL_MESSAGE = os.environ.get(
        'RAG_REFUSAL_MESSAGE',
        "I can only answer questions supported by the information available in my authorized knowledge base. Please ask a question related to the available documents."
    )
    RAG_RELEVANCE_THRESHOLD = float(os.environ.get('RAG_RELEVANCE_THRESHOLD', '0.25'))

    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    CELERY_TASK_ALWAYS_EAGER = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    CELERY_TASK_ALWAYS_EAGER = True
    STORAGE_BACKEND = 'local'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    CELERY_TASK_ALWAYS_EAGER = False

def get_config(env_name=None):
    env = env_name or os.environ.get('FLASK_ENV', 'development')
    if env == 'testing':
        return TestingConfig
    elif env == 'production':
        return ProductionConfig
    return DevelopmentConfig
