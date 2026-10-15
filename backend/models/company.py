"""
Company, CompanyMetric, CompanyObligation, and Task models.
"""
from datetime import datetime
from backend.extensions import db

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    trade_name = db.Column(db.String(150), nullable=True)
    entity_type = db.Column(db.String(60), default='Private Limited Company')
    
    state = db.Column(db.String(60), nullable=False, index=True)
    district = db.Column(db.String(80), nullable=True)
    registered_address = db.Column(db.Text, nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    
    industry = db.Column(db.String(100), default='Manufacturing')
    sector = db.Column(db.String(100), default='General Manufacturing')
    activity_type = db.Column(db.String(50), default='Manufacturing')
    
    incorporation_date = db.Column(db.Date, nullable=True)
    udyam_number = db.Column(db.String(50), nullable=True)
    pan_number = db.Column(db.String(20), nullable=True)
    gstin = db.Column(db.String(20), nullable=True)
    
    is_dpiit_recognized = db.Column(db.Boolean, default=False)
    is_deep_tech = db.Column(db.Boolean, default=False)
    is_zed_certified = db.Column(db.Boolean, default=False)
    is_exporter = db.Column(db.Boolean, default=False)
    
    onboarding_step = db.Column(db.Integer, default=1)
    is_onboarded = db.Column(db.Boolean, default=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    metrics = db.relationship('CompanyMetric', backref='company', lazy=True, cascade='all, delete-orphan')
    obligations = db.relationship('CompanyObligation', backref='company', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='company', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='company', lazy=True, cascade='all, delete-orphan')
    drafts = db.relationship('AIDraft', backref='company', lazy=True, cascade='all, delete-orphan')
    review_requests = db.relationship('ReviewRequest', backref='company', lazy=True, cascade='all, delete-orphan')

    @property
    def udyam_registration_number(self):
        return self.udyam_number

    @udyam_registration_number.setter
    def udyam_registration_number(self, val):
        self.udyam_number = val

    def get_latest_metric(self, metric_type):
        m = CompanyMetric.query.filter_by(company_id=self.id, metric_type=metric_type)\
                               .order_by(CompanyMetric.created_at.desc()).first()
        return m.value if m else 0

class CompanyMetric(db.Model):
    __tablename__ = 'company_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    metric_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    financial_year = db.Column(db.String(20), default='2025-26')
    provenance = db.Column(db.String(50), default='user_entered')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CompanyObligation(db.Model):
    __tablename__ = 'company_obligations'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    compliance_id = db.Column(db.String(20), db.ForeignKey('compliance_requirements.id'), nullable=False)
    
    status = db.Column(db.String(50), default='new')
    match_reason = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    evidence_text = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    compliance = db.relationship('ComplianceRequirement', backref='company_obligations')

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    obligation_id = db.Column(db.Integer, db.ForeignKey('company_obligations.id'), nullable=True)
    source_type = db.Column(db.String(50), default='manual')
    source_id = db.Column(db.String(50), nullable=True)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='medium')
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='todo')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    drafts = db.relationship('AIDraft', backref='task', lazy=True)
