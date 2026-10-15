"""
KnowledgeCollection, KnowledgeDocument, DocumentChunk, IngestionJob, and KnowledgeSource models.
"""
from datetime import datetime
from backend.extensions import db

class KnowledgeCollection(db.Model):
    """Admin RAG Document Collections"""
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
    document_type = db.Column(db.String(60), default='gazette_notification')
    issuing_authority = db.Column(db.String(150), nullable=True)
    official_source_url = db.Column(db.String(500), nullable=True)
    jurisdiction = db.Column(db.String(60), default='Central')
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
    
    status = db.Column(db.String(30), default='draft')
    error_message = db.Column(db.Text, nullable=True)
    reviewer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade='all, delete-orphan')
    jobs = db.relationship('IngestionJob', backref='document', lazy=True, cascade='all, delete-orphan')

class DocumentChunk(db.Model):
    """Text Chunks with Metadata & Vector Embeddings"""
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('knowledge_documents.id'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=True)
    section_heading = db.Column(db.String(255), nullable=True)
    token_count = db.Column(db.Integer, default=0)
    embedding_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class IngestionJob(db.Model):
    """Background Ingestion Pipeline Tracker"""
    __tablename__ = 'ingestion_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('knowledge_documents.id'), nullable=False, index=True)
    status = db.Column(db.String(30), default='queued')
    step_progress = db.Column(db.String(100), default='Initialized')
    error_log = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KnowledgeSource(db.Model):
    """Whitelisted Official Government Sources & Portals"""
    __tablename__ = 'knowledge_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    portal_url = db.Column(db.String(300), nullable=False)
    issuing_authority = db.Column(db.String(150), nullable=True)
    jurisdiction = db.Column(db.String(50), default='Central')
    state = db.Column(db.String(100), nullable=True)
    domain_name = db.Column(db.String(150), unique=True, nullable=True)
    authority_name = db.Column(db.String(150), nullable=True)
    base_url = db.Column(db.String(300), nullable=True)
    is_whitelisted = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.portal_url and self.base_url:
            self.portal_url = self.base_url
        if not self.base_url and self.portal_url:
            self.base_url = self.portal_url
        if not self.name and self.domain_name:
            self.name = self.domain_name
        if not self.issuing_authority and self.authority_name:
            self.issuing_authority = self.authority_name
        if not self.authority_name and self.issuing_authority:
            self.authority_name = self.issuing_authority
