"""
IncentiveScheme model.
"""
from backend.extensions import db

class IncentiveScheme(db.Model):
    __tablename__ = 'incentive_schemes'
    
    id = db.Column(db.String(20), primary_key=True)  # e.g. CI-001, SI-024
    jurisdiction = db.Column(db.String(60), nullable=False, index=True)
    jurisdiction_type = db.Column(db.String(20), default='Central')
    category = db.Column(db.String(80), nullable=False, index=True)
    scheme_name = db.Column(db.String(255), nullable=False)
    ministry_agency = db.Column(db.String(150), nullable=True)
    key_benefit = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    apply_link = db.Column(db.String(255), nullable=True)
    status_notes = db.Column(db.Text, nullable=True)
    
    verification_status = db.Column(db.String(50), default='knowledge_based')
    last_verified_date = db.Column(db.String(50), default='Oct 2026')
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)
