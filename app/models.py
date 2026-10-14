"""
Data models for MSME Compliance & Incentives Intelligence Platform.
Enforces multi-tenancy, provenance, audit trails, and versioning.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    plan = db.Column(db.String(50), default='starter')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    companies = db.relationship('Company', backref='tenant', lazy=True, cascade='all, delete-orphan')
    memberships = db.relationship('Membership', backref='tenant', lazy=True, cascade='all, delete-orphan')

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='owner')  # owner, compliance_manager, consultant, viewer, knowledge_reviewer, platform_admin
    preferred_language = db.Column(db.String(10), default='en')
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    memberships = db.relationship('Membership', backref='user', lazy=True, cascade='all, delete-orphan')
    client_accesses = db.relationship('ClientAccess', foreign_keys='ClientAccess.consultant_user_id', backref='consultant', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

class Membership(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    role = db.Column(db.String(50), default='owner')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    trade_name = db.Column(db.String(150), nullable=True)
    entity_type = db.Column(db.String(60), default='Private Limited Company')  # Pvt Ltd, LLP, Partnership, Sole Proprietorship, Public Ltd
    
    state = db.Column(db.String(60), nullable=False, index=True)
    district = db.Column(db.String(80), nullable=True)
    registered_address = db.Column(db.Text, nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    
    industry = db.Column(db.String(100), default='Manufacturing')
    sector = db.Column(db.String(100), default='General Manufacturing')
    activity_type = db.Column(db.String(50), default='Manufacturing')  # Manufacturing, Services, Trading, Hybrid
    
    incorporation_date = db.Column(db.Date, nullable=True)
    udyam_number = db.Column(db.String(50), nullable=True)
    pan_number = db.Column(db.String(20), nullable=True)
    gstin = db.Column(db.String(20), nullable=True)
    
    is_dpiit_recognized = db.Column(db.Boolean, default=False)
    is_deep_tech = db.Column(db.Boolean, default=False)
    is_zed_certified = db.Column(db.Boolean, default=False)
    is_exporter = db.Column(db.Boolean, default=False)
    
    # Onboarding & Ownership Fields
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
    metric_type = db.Column(db.String(50), nullable=False)  # turnover, investment, employees
    value = db.Column(db.Float, nullable=False)
    financial_year = db.Column(db.String(20), default='2025-26')
    provenance = db.Column(db.String(50), default='user_entered')  # user_entered, imported, verified
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComplianceRequirement(db.Model):
    __tablename__ = 'compliance_requirements'
    
    id = db.Column(db.String(20), primary_key=True)  # e.g. CC-001, SC-010
    jurisdiction = db.Column(db.String(60), nullable=False, index=True)  # 'Central' or State Name
    jurisdiction_type = db.Column(db.String(20), default='Central')  # Central, State, UT
    domain = db.Column(db.String(60), nullable=False, index=True)  # Registration, GST, Labour, Tax, etc.
    requirement = db.Column(db.String(255), nullable=False)
    law_basis = db.Column(db.Text, nullable=True)
    applies_to_trigger = db.Column(db.Text, nullable=True)
    what_to_do = db.Column(db.Text, nullable=True)
    frequency_due_date = db.Column(db.String(120), nullable=True)
    authority = db.Column(db.String(150), nullable=True)
    official_link = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    verification_status = db.Column(db.String(50), default='knowledge_based')  # verified, knowledge_based, pending_review
    last_verified_date = db.Column(db.String(50), default='Oct 2026')
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)

class IncentiveScheme(db.Model):
    __tablename__ = 'incentive_schemes'
    
    id = db.Column(db.String(20), primary_key=True)  # e.g. CI-001, SI-024
    jurisdiction = db.Column(db.String(60), nullable=False, index=True)  # 'Central' or State Name
    jurisdiction_type = db.Column(db.String(20), default='Central')
    category = db.Column(db.String(80), nullable=False, index=True)  # Credit & Guarantee, Startup, Export, etc.
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

class CompanyObligation(db.Model):
    __tablename__ = 'company_obligations'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    compliance_id = db.Column(db.String(20), db.ForeignKey('compliance_requirements.id'), nullable=False)
    
    status = db.Column(db.String(50), default='new')  # new, todo, in_progress, completed_by_user, needs_review, not_applicable
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
    source_type = db.Column(db.String(50), default='manual')  # manual, compliance, scheme, ai_suggested
    source_id = db.Column(db.String(50), nullable=True)  # e.g., CC-001, CI-002
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='todo')  # todo, in_progress, completed, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    drafts = db.relationship('AIDraft', backref='task', lazy=True)

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    doc_type = db.Column(db.String(60), default='other')  # udyam_cert, pan, gstin, incorporation, audit_report, fssai, other
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    verification_status = db.Column(db.String(30), default='unverified')  # unverified, verified, expired, rejected
    status = db.Column(db.String(30), default='ready')  # ready, processing, failed
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    extractions = db.relationship('DocumentExtraction', backref='document', lazy=True, cascade='all, delete-orphan')

class ClientAccess(db.Model):
    """CA & Consultant Client Delegation"""
    __tablename__ = 'client_access'
    
    id = db.Column(db.Integer, primary_key=True)
    consultant_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    access_level = db.Column(db.String(30), default='full')  # full, reviewer, readonly
    status = db.Column(db.String(20), default='active')  # active, revoked
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', backref='consultant_delegations')

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
    
    review_status = db.Column(db.String(30), default='detected')  # detected, parsed, needs_review, approved, rejected, published
    content_hash = db.Column(db.String(64), nullable=True)
    prior_version = db.Column(db.String(20), default='1.0')
    new_version = db.Column(db.String(20), default='1.1')
    source_snapshot = db.Column(db.Text, nullable=True)
    proposed_diff = db.Column(db.Text, nullable=True)
    affected_rule_id = db.Column(db.String(30), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

class AuditEvent(db.Model):
    """Immutable Audit Log"""
    __tablename__ = 'audit_events'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, nullable=True, index=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(80), nullable=False)  # profile_updated, obligation_completed, rule_approved, file_uploaded, login, draft_created, fields_confirmed
    entity_type = db.Column(db.String(60), nullable=True)
    entity_id = db.Column(db.String(60), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Subscription(db.Model):
    """Tenant Subscription & Entitlements"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, unique=True)
    plan_tier = db.Column(db.String(40), default='starter')  # starter, growth, consultant_pro
    status = db.Column(db.String(30), default='active')  # active, trial, past_due, cancelled
    max_companies = db.Column(db.Integer, default=1)
    has_ai_access = db.Column(db.Boolean, default=True)
    valid_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DocumentExtraction(db.Model):
    """Paperwork Agent Document Text & OCR Extraction"""
    __tablename__ = 'document_extractions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, index=True)
    status = db.Column(db.String(30), default='pending')  # pending, processed, confirmed, failed
    raw_text = db.Column(db.Text, nullable=True)
    extraction_method = db.Column(db.String(80), default='ocr_heuristic_v1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fields = db.relationship('ExtractedField', backref='extraction', lazy=True, cascade='all, delete-orphan')

class ExtractedField(db.Model):
    """Staged candidate fields awaiting human confirmation before updating authoritative company profile"""
    __tablename__ = 'extracted_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    extraction_id = db.Column(db.Integer, db.ForeignKey('document_extractions.id'), nullable=False, index=True)
    field_name = db.Column(db.String(60), nullable=False)  # udyam_number, pan_number, gstin, turnover, investment, employees, etc.
    proposed_value = db.Column(db.String(255), nullable=True)
    confidence = db.Column(db.String(30), default='needs_review')  # high, medium, needs_review
    source_location = db.Column(db.String(100), nullable=True)  # Page 1, Section A, etc.
    status = db.Column(db.String(30), default='needs_review')  # needs_review, confirmed, rejected
    corrected_value = db.Column(db.String(255), nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)

class AIDraft(db.Model):
    """Paperwork Agent Drafts: Checklists, Cover Letters, Application Summaries"""
    __tablename__ = 'ai_drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    scheme_id = db.Column(db.String(20), db.ForeignKey('incentive_schemes.id'), nullable=True)
    compliance_id = db.Column(db.String(20), db.ForeignKey('compliance_requirements.id'), nullable=True)
    
    draft_type = db.Column(db.String(50), default='checklist')  # checklist, cover_letter, form_response
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='draft')  # draft, approved, rejected
    version = db.Column(db.Integer, default=1)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    scheme = db.relationship('IncentiveScheme', backref='drafts')
    compliance = db.relationship('ComplianceRequirement', backref='drafts')

class ReviewRequest(db.Model):
    """Human Expert Review Escalation for uncertain compliance/incentive interpretations"""
    __tablename__ = 'review_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_type = db.Column(db.String(50), default='compliance')  # compliance, incentive, document
    reference_id = db.Column(db.String(50), nullable=True)  # e.g. CC-001 or CI-002
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='pending')  # pending, assigned, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KnowledgeCollection(db.Model):
    """Admin RAG Document Collections (e.g. Labour Codes, Tax Acts, Schemes)"""
    __tablename__ = 'knowledge_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    documents = db.relationship('KnowledgeDocument', backref='collection', lazy=True)

class KnowledgeDocument(db.Model):
    """Admin-Managed Verified Regulatory Knowledge Document"""
    __tablename__ = 'knowledge_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('knowledge_collections.id'), nullable=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(60), default='gazette_notification')  # act, rules, circular, scheme_guidelines, gazette_notification, checklist
    issuing_authority = db.Column(db.String(150), nullable=True)
    official_source_url = db.Column(db.String(500), nullable=True)
    jurisdiction = db.Column(db.String(60), default='Central')  # Central or State name
    state = db.Column(db.String(80), nullable=True)
    industry_sector = db.Column(db.String(100), nullable=True)
    compliance_category = db.Column(db.String(100), nullable=True)
    incentive_scheme_id = db.Column(db.String(30), nullable=True)
    publication_date = db.Column(db.Date, nullable=True)
    effective_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    language = db.Column(db.String(10), default='en')
    version = db.Column(db.String(20), default='1.0')
    
    file_path = db.Column(db.String(300), nullable=True)
    filename = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    content_hash = db.Column(db.String(64), nullable=True)
    raw_text = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(30), default='draft')  # draft, processing, needs_review, approved, published, superseded, archived, failed
    error_message = db.Column(db.Text, nullable=True)
    reviewer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade='all, delete-orphan')
    jobs = db.relationship('IngestionJob', backref='document', lazy=True, cascade='all, delete-orphan')

class DocumentChunk(db.Model):
    """Text Chunks with Metadata & Vector Embeddings for Hybrid Retrieval"""
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('knowledge_documents.id'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=True)
    section_heading = db.Column(db.String(255), nullable=True)
    token_count = db.Column(db.Integer, default=0)
    embedding_json = db.Column(db.Text, nullable=True)  # JSON-serialized embedding vector
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class IngestionJob(db.Model):
    """Background Ingestion Pipeline Tracker"""
    __tablename__ = 'ingestion_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('knowledge_documents.id'), nullable=False, index=True)
    status = db.Column(db.String(30), default='queued')  # queued, processing, completed, failed
    step_progress = db.Column(db.String(100), default='Initialized')
    error_log = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KnowledgeSource(db.Model):
    """Whitelisted Official Government Sources & Portals"""
    __tablename__ = 'knowledge_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(150), unique=True, nullable=False)
    authority_name = db.Column(db.String(150), nullable=False)
    base_url = db.Column(db.String(300), nullable=False)
    is_whitelisted = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DocumentFolder(db.Model):
    """Smart Document Vault Virtual Folder Hierarchy"""
    __tablename__ = 'document_folders'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('document_folders.id'), nullable=True)
    folder_type = db.Column(db.String(40), default='vault')  # vault, compliance_package, incentive_application
    is_system = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subfolders = db.relationship('DocumentFolder', backref=db.backref('parent', remote_side=[id]), lazy=True)
    links = db.relationship('DocumentFolderLink', backref='folder', lazy=True, cascade='all, delete-orphan')

class DocumentFolderLink(db.Model):
    """Logical Links from Virtual Folders to Central Physical Document Records"""
    __tablename__ = 'document_folder_links'
    
    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('document_folders.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    doc = db.relationship('Document', backref='folder_links')

class ApplicationWorkspace(db.Model):
    """Compliance & Incentive Application Packages / Working Folders"""
    __tablename__ = 'application_workspaces'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    workspace_type = db.Column(db.String(40), default='incentive')  # compliance, incentive, custom
    reference_id = db.Column(db.String(50), nullable=True)  # e.g., CC-001, CI-002
    folder_id = db.Column(db.Integer, db.ForeignKey('document_folders.id'), nullable=True)
    status = db.Column(db.String(30), default='draft')  # draft, in_review, ready_to_submit, submitted
    checklist_json = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    folder = db.relationship('DocumentFolder', backref='workspaces')
    artifacts = db.relationship('GeneratedArtifact', backref='workspace', lazy=True, cascade='all, delete-orphan')

class GeneratedArtifact(db.Model):
    """Generated Real Downloadable Artifacts (Checklist, Cover Letter, PDF, DOCX)"""
    __tablename__ = 'generated_artifacts'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('application_workspaces.id'), nullable=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    artifact_type = db.Column(db.String(50), default='checklist')  # checklist, cover_letter, worksheet, statement
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    mime_type = db.Column(db.String(100), default='application/pdf')
    content_text = db.Column(db.Text, nullable=True)
    version = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default='draft')  # draft, approved, finalized
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TranslationCache(db.Model):
    """Database Translation Cache for Google Cloud Translation & Runtime Caching"""
    __tablename__ = 'translation_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    source_hash = db.Column(db.String(64), index=True, nullable=False)
    source_text = db.Column(db.Text, nullable=False)
    target_lang = db.Column(db.String(10), index=True, nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(50), default='google_cloud')
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

