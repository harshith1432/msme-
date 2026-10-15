"""
AuditEvent model.
"""
from datetime import datetime
from backend.extensions import db

class AuditEvent(db.Model):
    """Immutable Audit Log"""
    __tablename__ = 'audit_events'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, nullable=True, index=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(60), nullable=True)
    entity_id = db.Column(db.String(60), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
