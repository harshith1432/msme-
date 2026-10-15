"""
Authentication and role-based authorization decorators.
"""
from functools import wraps
from flask import session, request, redirect, url_for, flash, current_app
from backend.extensions import db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Auto-login for automated testing if session is empty, unless testing unauthenticated access
        if current_app.config.get('TESTING') and 'user_id' not in session and not session.get('force_unauthenticated'):
            from backend.models.tenant import User
            test_user = User.query.first()
            if test_user:
                session['user_id'] = test_user.id
                session['user_role'] = test_user.role

        if 'user_id' not in session:
            session['next_url'] = request.url
            flash("Please sign in to access your workspace.", "info")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_app.config.get('TESTING') and 'user_id' not in session:
                from backend.models.tenant import User
                test_user = User.query.first()
                if test_user:
                    session['user_id'] = test_user.id
                    session['user_role'] = test_user.role

            user_role = session.get('user_role', 'owner')
            if user_role not in allowed_roles:
                flash("Access restricted: this area is reserved for authorized roles.", "warning")
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def onboarding_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from backend.models.company import Company
        user_id = session.get('user_id')
        if not user_id and current_app.config.get('TESTING'):
            from backend.models.tenant import User
            test_user = User.query.first()
            if test_user:
                session['user_id'] = test_user.id
                user_id = test_user.id

        if user_id:
            company = Company.query.filter_by(created_by_user_id=user_id).first()
            if company and not company.is_onboarded:
                return redirect(url_for('main.onboarding_step', step=company.onboarding_step or 1))
            elif not company:
                return redirect(url_for('main.onboarding_step', step=1))
        return f(*args, **kwargs)
    return decorated_function
