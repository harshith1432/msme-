"""
Tenant, User, Membership, ClientAccess, and Subscription models.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db

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
