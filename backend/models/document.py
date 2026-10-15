"""
Document, DocumentExtraction, ExtractedField, DocumentFolder, and FolderLink models.
"""
from datetime import datetime
from backend.extensions import db

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    doc_type = db.Column(db.String(60), default='other')
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    verification_status = db.Column(db.String(30), default='unverified')
    status = db.Column(db.String(30), default='ready')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    extractions = db.relationship('DocumentExtraction', backref='document', lazy=True, cascade='all, delete-orphan')

class DocumentExtraction(db.Model):
    """Paperwork Agent Document Text & OCR Extraction"""
    __tablename__ = 'document_extractions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, index=True)
    status = db.Column(db.String(30), default='pending')
    raw_text = db.Column(db.Text, nullable=True)
    extraction_method = db.Column(db.String(80), default='ocr_heuristic_v1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fields = db.relationship('ExtractedField', backref='extraction', lazy=True, cascade='all, delete-orphan')

class ExtractedField(db.Model):
    """Staged candidate fields awaiting human confirmation before updating authoritative profile"""
    __tablename__ = 'extracted_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    extraction_id = db.Column(db.Integer, db.ForeignKey('document_extractions.id'), nullable=False, index=True)
    field_name = db.Column(db.String(60), nullable=False)
    proposed_value = db.Column(db.String(255), nullable=True)
    confidence = db.Column(db.String(30), default='needs_review')
    source_location = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), default='needs_review')
    corrected_value = db.Column(db.String(255), nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)

class DocumentFolder(db.Model):
    """Smart Document Vault Virtual Folder Hierarchy"""
    __tablename__ = 'document_folders'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('document_folders.id'), nullable=True)
    folder_type = db.Column(db.String(40), default='vault')
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
