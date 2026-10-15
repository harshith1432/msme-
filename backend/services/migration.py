"""
Database Schema Migration Helper for MSME Platform.
Ensures new tables and columns are added smoothly to PostgreSQL / SQLite
without dropping data or breaking existing records.
"""
from sqlalchemy import inspect, text
from backend.extensions import db

def run_migrations(app):
    """
    Applies any schema updates required for the AI features:
    1. Runs db.create_all() to create missing tables.
    2. Runs ALTER TABLE on existing tables if columns are missing.
    """
    with app.app_context():
        # First ensure all tables defined in models are created
        db.create_all()

        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            if 'documents' in existing_tables:
                doc_cols = [c['name'] for c in inspector.get_columns('documents')]
                with db.engine.connect() as conn:
                    if 'verification_status' not in doc_cols:
                        conn.execute(text("ALTER TABLE documents ADD COLUMN verification_status VARCHAR(30) DEFAULT 'unverified';"))
                        conn.commit()
                    if 'status' not in doc_cols:
                        conn.execute(text("ALTER TABLE documents ADD COLUMN status VARCHAR(30) DEFAULT 'ready';"))
                        conn.commit()

            if 'tasks' in existing_tables:
                task_cols = [c['name'] for c in inspector.get_columns('tasks')]
                with db.engine.connect() as conn:
                    if 'source_type' not in task_cols:
                        conn.execute(text("ALTER TABLE tasks ADD COLUMN source_type VARCHAR(50) DEFAULT 'manual';"))
                        conn.commit()
                    if 'source_id' not in task_cols:
                        conn.execute(text("ALTER TABLE tasks ADD COLUMN source_id VARCHAR(50);"))
                        conn.commit()

            if 'regulatory_changes' in existing_tables:
                reg_cols = [c['name'] for c in inspector.get_columns('regulatory_changes')]
                with db.engine.connect() as conn:
                    if 'content_hash' not in reg_cols:
                        conn.execute(text("ALTER TABLE regulatory_changes ADD COLUMN content_hash VARCHAR(64);"))
                        conn.commit()
                    if 'prior_version' not in reg_cols:
                        conn.execute(text("ALTER TABLE regulatory_changes ADD COLUMN prior_version VARCHAR(20) DEFAULT '1.0';"))
                        conn.commit()
                    if 'new_version' not in reg_cols:
                        conn.execute(text("ALTER TABLE regulatory_changes ADD COLUMN new_version VARCHAR(20) DEFAULT '1.1';"))
                        conn.commit()
                    if 'source_snapshot' not in reg_cols:
                        conn.execute(text("ALTER TABLE regulatory_changes ADD COLUMN source_snapshot TEXT;"))
                        conn.commit()
                    if 'proposed_diff' not in reg_cols:
                        conn.execute(text("ALTER TABLE regulatory_changes ADD COLUMN proposed_diff TEXT;"))
                        conn.commit()
                    if 'affected_rule_id' not in reg_cols:
                        conn.execute(text("ALTER TABLE regulatory_changes ADD COLUMN affected_rule_id VARCHAR(30);"))
                        conn.commit()

            if 'users' in existing_tables:
                user_cols = [c['name'] for c in inspector.get_columns('users')]
                with db.engine.connect() as conn:
                    if 'preferred_language' not in user_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en';"))
                        conn.commit()
                    if 'reset_token' not in user_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(100);"))
                        conn.commit()
                    if 'reset_token_expiry' not in user_cols:
                        conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP;"))
                        conn.commit()

            if 'companies' in existing_tables:
                comp_cols = [c['name'] for c in inspector.get_columns('companies')]
                with db.engine.connect() as conn:
                    if 'onboarding_step' not in comp_cols:
                        conn.execute(text("ALTER TABLE companies ADD COLUMN onboarding_step INTEGER DEFAULT 1;"))
                        conn.commit()
                    if 'is_onboarded' not in comp_cols:
                        conn.execute(text("ALTER TABLE companies ADD COLUMN is_onboarded BOOLEAN DEFAULT FALSE;"))
                        conn.commit()
                        # Default existing seeded companies to onboarded
                        conn.execute(text("UPDATE companies SET is_onboarded = TRUE, onboarding_step = 6 WHERE is_onboarded IS NULL OR is_onboarded = FALSE;"))
                        conn.commit()
                    if 'created_by_user_id' not in comp_cols:
                        conn.execute(text("ALTER TABLE companies ADD COLUMN created_by_user_id INTEGER;"))
                        conn.commit()
                    if 'contact_email' not in comp_cols:
                        conn.execute(text("ALTER TABLE companies ADD COLUMN contact_email VARCHAR(120);"))
                        conn.commit()
                    if 'contact_phone' not in comp_cols:
                        conn.execute(text("ALTER TABLE companies ADD COLUMN contact_phone VARCHAR(20);"))
                        conn.commit()
        except Exception as e:
            print(f"Migration note: {e}")
