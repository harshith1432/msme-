"""
ApplicationWorkspace, GeneratedArtifact, AIDraft, and TranslationCache models.
"""
from datetime import datetime
from backend.extensions import db

class AIDraft(db.Model):
    """Paperwork Agent Drafts: Checklists, Cover Letters, Application Summaries"""
    __tablename__ = 'ai_drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    scheme_id = db.Column(db.String(20), db.ForeignKey('incentive_schemes.id'), nullable=True)
    compliance_id = db.Column(db.String(20), db.ForeignKey('compliance_requirements.id'), nullable=True)
    
    draft_type = db.Column(db.String(50), default='checklist')
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='draft')
    version = db.Column(db.Integer, default=1)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    scheme = db.relationship('IncentiveScheme', backref='drafts')
    compliance = db.relationship('ComplianceRequirement', backref='drafts')

class ApplicationWorkspace(db.Model):
    """Compliance & Incentive Application Packages / Working Folders"""
    __tablename__ = 'application_workspaces'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    workspace_type = db.Column(db.String(40), default='incentive')
    reference_id = db.Column(db.String(50), nullable=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('document_folders.id'), nullable=True)
    status = db.Column(db.String(30), default='draft')
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
    artifact_type = db.Column(db.String(50), default='checklist')
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    mime_type = db.Column(db.String(100), default='application/pdf')
    content_text = db.Column(db.Text, nullable=True)
    version = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default='draft')
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
