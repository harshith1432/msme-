"""
Flask Application Factory for MSME Compliance & Incentives Navigator.
"""
from flask import Flask, session, request
import os
from .config import Config
from .extensions import db
from .services.seeder import seed_database

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Ensure uploads and data directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)

    # Context processor to inject active language, user, and supported languages into all templates
    from .services.i18n import translate, translate_dynamic, MASTER_TRANSLATIONS, load_locale
    app.jinja_env.globals['t'] = translate
    app.jinja_env.filters['t'] = translate
    app.jinja_env.globals['td'] = translate_dynamic
    app.jinja_env.filters['td'] = translate_dynamic
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
            from .models import User
            user = User.query.get(user_id)

        client_translations = {}
        if current_lang != 'en':
            if current_lang in MASTER_TRANSLATIONS:
                client_translations.update(MASTER_TRANSLATIONS[current_lang])
            loc = load_locale(current_lang)
            if loc:
                client_translations.update(loc)
            
        return {
            'current_lang': current_lang,
            'supported_languages': supported,
            'current_user': user,
            't': translate,
            'client_translations': client_translations
        }

    # Register routes
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Automatically run schema migrations and seed database on initial boot
    try:
        from .services.migration import run_migrations
        run_migrations(app)
        seed_database(app)
    except Exception as e:
        print(f"Database seeder/migration note: {e}")

    return app
