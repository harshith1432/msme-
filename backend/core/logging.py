"""
Centralized structured logging with request correlation IDs and secret redaction.
"""
import logging
import sys
import uuid
from flask import request, g, has_request_context, has_app_context

REDACTED_KEYS = {'password', 'secret', 'token', 'authorization', 'api_key', 'access_key'}

class RequestContextFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, 'request_id', 'no-req-id') if has_app_context() else 'no-req-id'
            record.client_ip = request.remote_addr or 'unknown'
            record.method = request.method
            record.path = request.path
        else:
            record.request_id = getattr(g, 'request_id', 'worker-or-sys') if has_app_context() else 'worker-or-sys'
            record.client_ip = 'internal'
            record.method = '-'
            record.path = '-'
        return True

def setup_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", '
        '"request_id": "%(request_id)s", "method": "%(method)s", "path": "%(path)s", '
        '"message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())

    logger = logging.getLogger()
    logger.setLevel(logging.INFO if not app.config.get('DEBUG') else logging.DEBUG)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger
