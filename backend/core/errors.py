"""
Centralized error handling and standardized JSON/HTML error responses.
"""
from flask import jsonify, render_template, request

class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv

class NotFoundError(APIError):
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)

class UnauthorizedError(APIError):
    def __init__(self, message="Authentication required", payload=None):
        super().__init__(message, status_code=401, payload=payload)

class ForbiddenError(APIError):
    def __init__(self, message="Access forbidden", payload=None):
        super().__init__(message, status_code=403, payload=payload)

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad Request', 'status_code': 400}), 400
        return "Bad Request", 400

    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not Found', 'status_code': 404}), 404
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(500)
    def server_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal Server Error', 'status_code': 500}), 500
        return "An internal server error occurred.", 500
