"""
Flask Application Factory for MSME Compliance & Incentives Navigator.
Supports modular blueprints, background task integration, structured logging, and i18n.
"""
import os
from flask import Flask, session, request
from backend.config import Config, get_config
from backend.extensions import db, migrate
from backend.core.logging import setup_logging
from backend.core.errors import register_error_handlers
from backend.core.security import setup_security_headers
from backend.core.middleware import setup_middleware
from backend.services.seeder import seed_database

def create_app(config_class=None):
    if config_class is None:
        config_class = get_config()

    # Determine templates and static paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(base_dir, 'frontend', 'templates')
    static_folder = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup core infrastructure
    setup_logging(app)
    register_error_handlers(app)
    setup_security_headers(app)
    setup_middleware(app)

    # Ensure required directories exist
    upload_dir = '/tmp/uploads' if os.environ.get('VERCEL') else app.config.get('UPLOAD_FOLDER', os.path.join(base_dir, 'uploads'))
    data_dir = '/tmp/data' if os.environ.get('VERCEL') else app.config.get('DATA_DIR', os.path.join(base_dir, 'data'))
    try:
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
    except OSError:
        pass

    # Context processor to inject active language, user, and supported languages into templates
    from backend.services.i18n import translate, translate_dynamic
    app.jinja_env.globals['t'] = translate
    app.jinja_env.filters['t'] = translate
    app.jinja_env.globals['td'] = translate_dynamic
    app.jinja_env.filters['td'] = translate_dynamic
    app.jinja_env.globals['translate_dynamic'] = translate_dynamic
    app.jinja_env.filters['translate_dynamic'] = translate_dynamic

    @app.context_processor
    def inject_i18n_context():
        current_lang = session.get('lang', 'en')
        supported = [
            {'code': 'en', 'name': 'English', 'native': 'English'},
            {'code': 'kn', 'name': 'Kannada', 'native': 'ಕನ್ನಡ'},
            {'code': 'hi', 'name': 'Hindi', 'native': 'हिन्दी'},
            {'code': 'te', 'name': 'Telugu', 'native': 'తెలుగు'},
            {'code': 'ta', 'name': 'Tamil', 'native': 'தமிழ்'},
            {'code': 'ml', 'name': 'Malayalam', 'native': 'മലയാളം'},
            {'code': 'mr', 'name': 'Marathi', 'native': 'मराठी'},
            {'code': 'gu', 'name': 'Gujarati', 'native': 'ગુજરાતી'},
            {'code': 'bn', 'name': 'Bengali', 'native': 'বাংলা'}
        ]
        
        user = None
        user_id = session.get('user_id')
        if user_id:
            from backend.models.tenant import User
            user = User.query.get(user_id)
            
        return {
            'current_lang': current_lang,
            'supported_languages': supported,
            'current_user': user,
            't': translate
        }

    # Register Health and Core Blueprints
    from backend.modules.dashboard.health import health_bp
    app.register_blueprint(health_bp)

    from backend.modules.routes_legacy import main_bp
    app.register_blueprint(main_bp)

    # Automatically run schema migrations and seed database on initial boot
    try:
        from backend.services.migration import run_migrations
        run_migrations(app)
        seed_database(app)
    except Exception as e:
        print(f"Database seeder/migration note: {e}")

    return app
