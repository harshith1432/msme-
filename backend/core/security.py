"""
Security controls: headers, CSRF utilities, input sanitization, rate limiting helpers.
"""
from functools import wraps
from flask import request, abort, current_app

def setup_security_headers(app):
    @app.after_request
    def set_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'; "
            "img-src 'self' https: data: blob:; "
            "font-src 'self' https: data:;"
        )
        return response

def validate_safe_redirect(target_url):
    """Ensure redirects remain within the application domain."""
    if not target_url:
        return False
    from urllib.parse import urlparse
    parsed = urlparse(target_url)
    return parsed.netloc == '' or parsed.netloc == request.host
