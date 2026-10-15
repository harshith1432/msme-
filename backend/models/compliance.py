"""
ComplianceRequirement, RegulatoryChange, and ReviewRequest models.
"""
from datetime import datetime
from backend.extensions import db

class ComplianceRequirement(db.Model):
    __tablename__ = 'compliance_requirements'
    
    id = db.Column(db.String(20), primary_key=True)  # e.g. CC-001, SC-010
    jurisdiction = db.Column(db.String(60), nullable=False, index=True)
    jurisdiction_type = db.Column(db.String(20), default='Central')
    domain = db.Column(db.String(60), nullable=False, index=True)
    requirement = db.Column(db.String(255), nullable=False)
    law_basis = db.Column(db.Text, nullable=True)
    applies_to_trigger = db.Column(db.Text, nullable=True)
    what_to_do = db.Column(db.Text, nullable=True)
    frequency_due_date = db.Column(db.String(120), nullable=True)
    authority = db.Column(db.String(150), nullable=True)
    official_link = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    verification_status = db.Column(db.String(50), default='knowledge_based')
    last_verified_date = db.Column(db.String(50), default='Oct 2026')
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)

class RegulatoryChange(db.Model):
    """Regulatory Change Intelligence Queue with Full Lifecycle"""
    __tablename__ = 'regulatory_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(255), nullable=False)
    issuing_authority = db.Column(db.String(150), nullable=False)
    summary_of_change = db.Column(db.Text, nullable=False)
    effective_date = db.Column(db.Date, nullable=True)
    affected_jurisdiction = db.Column(db.String(80), default='Central')
    affected_domain = db.Column(db.String(80), nullable=True)
    
    review_status = db.Column(db.String(30), default='detected')
    content_hash = db.Column(db.String(64), nullable=True)
    prior_version = db.Column(db.String(20), default='1.0')
    new_version = db.Column(db.String(20), default='1.1')
    source_snapshot = db.Column(db.Text, nullable=True)
    proposed_diff = db.Column(db.Text, nullable=True)
    affected_rule_id = db.Column(db.String(30), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

class ReviewRequest(db.Model):
    """Human Expert Review Escalation for uncertain compliance interpretations"""
    __tablename__ = 'review_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_type = db.Column(db.String(50), default='compliance')
    reference_id = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
