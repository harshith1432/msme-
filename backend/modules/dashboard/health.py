"""
Health and readiness probes for load balancers and orchestrators.
"""
from flask import Blueprint, jsonify
from backend.extensions import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health/live', methods=['GET'])
def liveness():
    """Liveness probe: verifies process is alive and responsive."""
    return jsonify({'status': 'alive'}), 200

@health_bp.route('/health/ready', methods=['GET'])
def readiness():
    """Readiness probe: verifies database connectivity and core subsystems."""
    checks = {'database': 'unknown', 'status': 'ok'}
    try:
        db.session.execute(db.text('SELECT 1'))
        checks['database'] = 'connected'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
        checks['status'] = 'unready'
        return jsonify(checks), 503

    return jsonify(checks), 200
