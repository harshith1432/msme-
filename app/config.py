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
    
    # Primary Database Configuration
    _raw_db_url = os.environ.get('DATABASE_URL')
    if _raw_db_url:
        if _raw_db_url.startswith('postgres://'):
            _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = _raw_db_url
    else:
        if os.environ.get('VERCEL'):
            SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/msme_navigator.db'
        else:
            _default_sqlite = os.path.join(BASE_DIR, 'data', 'msme_navigator.db')
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{_default_sqlite}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DEBUG = False
    TESTING = False
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

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
