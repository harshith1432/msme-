"""
Request lifecycle middleware: correlation IDs, request timing, and performance logging.
"""
import time
import uuid
from flask import request, g

def setup_middleware(app):
    @app.before_request
    def start_timer_and_correlation_id():
        g.start_time = time.time()
        # Accept incoming X-Request-ID or generate a new UUID
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())

    @app.after_request
    def log_and_tag_response(response):
        duration = time.time() - getattr(g, 'start_time', time.time())
        response.headers['X-Request-ID'] = getattr(g, 'request_id', '')
        response.headers['X-Response-Time-Ms'] = f"{duration * 1000:.2f}"
        return response
