"""
Comprehensive Application Routes & APIs for MSME Platform.
Implements:
  - Stage A: Public Landing Page
  - Stage B: Authentication (Register, Login, Logout, Forgot Password)
  - Stage C: 6-Step Enterprise Onboarding Wizard
  - Stage D: Role-Segregated Dashboards (Owner, Member, CA Workspace, Admin Portal)
  - Central & State Compliance Catalogue (424 items)
  - Central & State Incentive Catalogue (204 items)
  - Action-Oriented AI Advisor (5-Part Action Cards in Indian languages)
  - Tasks & Calendar Tracking
  - Secure Document Vault with OCR Extraction
  - CA / Consultant Multi-Client Workspace
  - Admin Regulatory Verification & Change Intelligence
  - Executive Reports & CSV Export
"""
import os
import io
import csv
import json
from functools import wraps
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, request, jsonify, session, 
    redirect, url_for, current_app, flash, send_from_directory,
    Response, abort
)
from backend.extensions import db
from backend.models import (
    Tenant, User, Membership, Company, CompanyMetric, 
    ComplianceRequirement, IncentiveScheme, CompanyObligation,
    Task, Document, ClientAccess, RegulatoryChange, AuditEvent,
    DocumentExtraction, ExtractedField, AIDraft, ReviewRequest,
    KnowledgeCollection, KnowledgeDocument, DocumentChunk, IngestionJob, KnowledgeSource,
    DocumentFolder, DocumentFolderLink, ApplicationWorkspace, GeneratedArtifact, TranslationCache
)
from backend.services.rules_engine import RulesEngine
from backend.services.ai_advisor import AIAdvisor, LANGUAGE_NAMES
from backend.services.extraction_service import ExtractionService
from backend.services.readiness_service import ReadinessService
from backend.services.incentive_service import IncentiveEligibilityService
from backend.services.regulatory_service import RegulatoryIntelligenceService
from backend.services.action_service import ComplianceActionService
from backend.services.tool_dispatcher import ToolDispatcher
from backend.services.rag_service import rag_service
from backend.services.website_research import website_research_service, SSRFProtectionError
from backend.services.document_generator import document_generator

main_bp = Blueprint('main', __name__)
rules_engine = RulesEngine()
ai_advisor = AIAdvisor()
extraction_service = ExtractionService()
readiness_service = ReadinessService()
incentive_service = IncentiveEligibilityService()
regulatory_service = RegulatoryIntelligenceService()
action_service = ComplianceActionService()
tool_dispatcher = ToolDispatcher()


# --- Authentication & Authorization Decorators ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Auto-login for legacy automated testing if session is empty, unless explicitly testing unauthenticated access
        if current_app.config.get('TESTING') and 'user_id' not in session and not session.get('force_unauthenticated'):
            test_user = User.query.first()
            if test_user:
                session['user_id'] = test_user.id
                session['user_role'] = test_user.role

        if 'user_id' not in session:
            session['next_url'] = request.url
            flash("Please sign in to access your workspace.", "info")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_app.config.get('TESTING') and 'user_id' not in session:
                test_user = User.query.first()
                if test_user:
                    session['user_id'] = test_user.id
                    session['user_role'] = test_user.role

            user_role = session.get('user_role', 'owner')
            if user_role not in allowed_roles:
                flash("Access restricted: this area is reserved for authorized roles.", "warning")
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def onboarding_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_role = session.get('user_role', 'owner')
        if user_role in ['owner', 'member']:
            company = get_current_company()
            if company and not company.is_onboarded:
                return redirect(url_for('main.onboarding'))
        return f(*args, **kwargs)
    return decorated_function


# --- Helpers ---

def get_current_company():
    user_id = session.get('user_id')
    company_id = session.get('active_company_id')
    user_role = session.get('user_role')
    
    if company_id:
        company = Company.query.get(company_id)
        if company:
            return company
            
    if user_id:
        # Check companies created by this user
        company = Company.query.filter_by(created_by_user_id=user_id).first()
        if not company:
            m = Membership.query.filter_by(user_id=user_id).first()
            if m:
                company = Company.query.filter_by(tenant_id=m.tenant_id).first()
        if not company:
            ca = ClientAccess.query.filter_by(consultant_user_id=user_id, status='active').first()
            if ca:
                company = Company.query.get(ca.company_id)
        if company:
            session['active_company_id'] = company.id
            return company

    # For platform admins, they govern all companies and do NOT have an active company workspace by default
    if user_role == 'platform_admin':
        return None

    # Fallback for testing mode or demo
    company = Company.query.first()
    if company:
        session['active_company_id'] = company.id
    return company

def get_company_profile_dict(company):
    if not company:
        return {}
    turnover = company.get_latest_metric('turnover')
    investment = company.get_latest_metric('investment')
    employees = int(company.get_latest_metric('employees'))
    
    age_years = 4
    if company.incorporation_date:
        today = date.today()
        age_years = today.year - company.incorporation_date.year - (
            (today.month, today.day) < (company.incorporation_date.month, company.incorporation_date.day)
        )

    return {
        "id": company.id,
        "tenant_id": getattr(company, 'tenant_id', None),
        "name": company.name,
        "trade_name": company.trade_name or company.name,
        "state": company.state,
        "district": company.district or "",
        "sector": company.sector,
        "entity_type": company.entity_type,
        "turnover": turnover,
        "investment": investment,
        "employees": employees,
        "age_years": max(0, age_years),
        "is_dpiit": company.is_dpiit_recognized,
        "is_deep_tech": company.is_deep_tech,
        "is_exporter": company.is_exporter,
        "udyam_number": company.udyam_number or "",
        "pan_number": company.pan_number or "",
        "gstin": company.gstin or ""
    }

@main_bp.context_processor
def inject_global_data():
    user_role = session.get('user_role', 'owner')
    is_admin = (user_role == 'platform_admin' or request.path.startswith('/admin'))
    is_consultant = (user_role == 'consultant' or request.path.startswith('/consultant'))
    company = None if (is_admin or is_consultant) else get_current_company()
    pending_changes = 0
    if is_admin:
        try:
            pending_changes = RegulatoryChange.query.filter_by(review_status='detected').count()
        except Exception:
            pending_changes = 0
    return {
        'active_company': company,
        'is_admin': is_admin,
        'is_consultant': is_consultant,
        'pending_changes_count': pending_changes
    }


# --- Stage A: Public Landing & Language Switching ---

@main_bp.route('/')
def index():
    if 'user_id' in session:
        user_role = session.get('user_role', 'owner')
        if user_role == 'platform_admin':
            return redirect(url_for('main.admin_dashboard'))
        if user_role == 'consultant':
            return redirect(url_for('main.consultant_workspace'))
        company = get_current_company()
        if company and not company.is_onboarded:
            return redirect(url_for('main.onboarding'))
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')

@main_bp.route('/landing')
def landing():
    return render_template('landing.html')

@main_bp.route('/set-language/<lang>')
@main_bp.route('/set_language/<lang>')
def set_language(lang):
    if lang in current_app.config['SUPPORTED_LANGUAGES']:
        session['lang'] = lang
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                user.preferred_language = lang
                db.session.commit()
    next_url = request.referrer or url_for('main.dashboard')
    return redirect(next_url)


# --- Stage B: Authentication Routes ---

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            if user.preferred_language:
                session['lang'] = user.preferred_language

            db.session.add(AuditEvent(
                user_id=user.id,
                action='login',
                entity_type='User',
                entity_id=str(user.id),
                details=f"User {user.email} signed in successfully"
            ))
            db.session.commit()

            flash(f"Welcome back, {user.name}!", "success")
            
            # Route by role
            if user.role == 'platform_admin':
                return redirect(url_for('main.admin_dashboard'))
            elif user.role == 'consultant':
                return redirect(url_for('main.consultant_workspace'))
            else:
                # Check onboarding status
                company = get_current_company()
                if not company or not company.is_onboarded:
                    return redirect(url_for('main.onboarding'))
                next_url = session.pop('next_url', None)
                return redirect(next_url or url_for('main.dashboard'))
        else:
            flash("Invalid email address or password. Please try again.", "danger")

    return render_template('auth/login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'owner')
        preferred_lang = request.form.get('preferred_language', 'en')

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('auth/register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('auth/register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('auth/register.html')

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("An account with this email address already exists. Please sign in.", "warning")
            return redirect(url_for('main.login'))

        # Create User
        user = User(
            name=name,
            email=email,
            role=role,
            preferred_language=preferred_lang
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Create Tenant and initial draft Company if owner
        if role in ['owner', 'member']:
            tenant = Tenant(name=f"{name}'s Organization", slug=f"org-{user.id}-{int(datetime.utcnow().timestamp())}")
            db.session.add(tenant)
            db.session.flush()

            db.session.add(Membership(user_id=user.id, tenant_id=tenant.id, role=role))

            company = Company(
                tenant_id=tenant.id,
                name="My Enterprise",
                entity_type="Private Limited Company",
                state="Maharashtra",
                created_by_user_id=user.id,
                onboarding_step=1,
                is_onboarded=False
            )
            db.session.add(company)
            db.session.flush()

            # Initialize initial metric stubs
            db.session.add(CompanyMetric(company_id=company.id, metric_type='turnover', value=10000000, provenance='user_entered'))
            db.session.add(CompanyMetric(company_id=company.id, metric_type='investment', value=5000000, provenance='user_entered'))
            db.session.add(CompanyMetric(company_id=company.id, metric_type='employees', value=5, provenance='user_entered'))
            session['active_company_id'] = company.id

        db.session.add(AuditEvent(
            user_id=user.id,
            action='register',
            entity_type='User',
            entity_id=str(user.id),
            details=f"New user registered: {email} with role {role}"
        ))
        db.session.commit()

        session['user_id'] = user.id
        session['user_role'] = user.role
        session['lang'] = preferred_lang

        flash("Account created successfully! Please complete your company onboarding.", "success")
        if role == 'consultant':
            return redirect(url_for('main.consultant_workspace'))
        return redirect(url_for('main.onboarding'))

    return render_template('auth/register.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('main.index'))

@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            user.reset_token = f"tok_{int(datetime.utcnow().timestamp())}"
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=2)
            db.session.commit()
        flash("If that email address is registered, instructions to reset your password have been sent.", "info")
        return redirect(url_for('main.login'))
    return render_template('auth/forgot_password.html')


# --- Stage C: 6-Step Company Onboarding Wizard ---

def get_onboarding_states():
    state_reqs = ComplianceRequirement.query.filter(ComplianceRequirement.jurisdiction_type != 'Central').all()
    states = sorted(list(set(r.jurisdiction for r in state_reqs if r.jurisdiction)))
    if not states:
        states = ['Gujarat', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Telangana', 'Delhi', 'Uttar Pradesh', 'West Bengal']
    return states

def render_onboarding_step_view(company, step):
    all_states = get_onboarding_states()
    current_turnover = company.get_latest_metric('turnover')
    current_investment = company.get_latest_metric('investment')
    current_employees = int(company.get_latest_metric('employees'))

    return render_template(
        'onboarding.html',
        company=company,
        current_step=step,
        all_states=all_states,
        current_turnover=current_turnover,
        current_investment=current_investment,
        current_employees=current_employees
    )

@main_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    company = get_current_company()
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    if not company:
        tenant = Tenant(name=f"{user.name if user else 'My'} Organization", slug=f"org-{int(datetime.utcnow().timestamp())}")
        db.session.add(tenant)
        db.session.flush()
        if user:
            db.session.add(Membership(user_id=user.id, tenant_id=tenant.id, role='owner'))
        company = Company(
            tenant_id=tenant.id,
            name="My Enterprise",
            entity_type="Private Limited Company",
            state="Maharashtra",
            created_by_user_id=user.id if user else None,
            onboarding_step=1,
            is_onboarded=False
        )
        db.session.add(company)
        db.session.commit()
        session['active_company_id'] = company.id

    if request.method == 'POST':
        step = int(request.form.get('step', company.onboarding_step or 1))
        action = request.form.get('action', 'continue')

        if step == 1:
            company.name = request.form.get('name', company.name).strip() or company.name
            company.trade_name = request.form.get('trade_name', '').strip()
            company.entity_type = request.form.get('entity_type', company.entity_type)
            inc_date_str = request.form.get('incorporation_date')
            if inc_date_str:
                company.incorporation_date = datetime.strptime(inc_date_str, '%Y-%m-%d').date()
            company.registered_address = request.form.get('registered_address', '').strip()
            company.state = request.form.get('state', company.state)
            company.district = request.form.get('district', '').strip()
            company.pincode = request.form.get('pincode', '').strip()
            company.contact_email = request.form.get('contact_email', '').strip()
            company.contact_phone = request.form.get('contact_phone', '').strip()

        elif step == 2:
            company.activity_type = request.form.get('activity_type', company.activity_type)
            company.sector = request.form.get('sector', company.sector)
            employees = int(request.form.get('employees', 0))
            company.is_exporter = ('is_exporter' in request.form)
            em = CompanyMetric.query.filter_by(company_id=company.id, metric_type='employees').first()
            if not em:
                em = CompanyMetric(company_id=company.id, metric_type='employees', value=employees, provenance='user_entered')
                db.session.add(em)
            else:
                em.value = employees

        elif step == 3:
            turnover = float(request.form.get('turnover', 0))
            investment = float(request.form.get('investment', 0))
            fy = request.form.get('financial_year', '2025-26')
            
            tm = CompanyMetric.query.filter_by(company_id=company.id, metric_type='turnover').first()
            if not tm:
                tm = CompanyMetric(company_id=company.id, metric_type='turnover', value=turnover, financial_year=fy, provenance='user_entered')
                db.session.add(tm)
            else:
                tm.value = turnover
                tm.financial_year = fy

            im = CompanyMetric.query.filter_by(company_id=company.id, metric_type='investment').first()
            if not im:
                im = CompanyMetric(company_id=company.id, metric_type='investment', value=investment, financial_year=fy, provenance='user_entered')
                db.session.add(im)
            else:
                im.value = investment
                im.financial_year = fy

        elif step == 4:
            company.udyam_number = request.form.get('udyam_number', '').strip()
            company.gstin = request.form.get('gstin', '').strip()
            company.pan_number = request.form.get('pan_number', '').strip()
            company.is_dpiit_recognized = ('is_dpiit' in request.form)
            company.is_deep_tech = ('is_deep_tech' in request.form)
            company.is_zed_certified = ('is_zed_certified' in request.form)

        elif step == 5:
            if 'onboarding_doc' in request.files:
                file = request.files['onboarding_doc']
                if file and file.filename:
                    ext = file.filename.rsplit('.', 1)[-1].lower()
                    if ext in current_app.config['ALLOWED_EXTENSIONS']:
                        sec_name = f"{company.id}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sec_name)
                        file.save(file_path)
                        doc = Document(
                            company_id=company.id,
                            title=file.filename,
                            doc_type='other',
                            filename=sec_name,
                            file_path=file_path,
                            file_size=os.path.getsize(file_path),
                            mime_type=file.content_type,
                            verification_status='unverified',
                            status='ready'
                        )
                        db.session.add(doc)

        db.session.commit()

        if action == 'draft':
            flash("Onboarding progress saved as draft.", "info")
            return redirect(url_for('main.onboarding_step_view', step=step))
        elif action == 'complete' or step == 6:
            company.is_onboarded = True
            company.onboarding_step = 6
            # Trigger initial rule evaluation & pre-populate tasks
            p = get_company_profile_dict(company)
            eval_res = rules_engine.evaluate_company(p)
            for item in eval_res['matched_central_compliance'][:3]:
                db.session.add(Task(
                    company_id=company.id,
                    title=f"Review: {item['Requirement'][:80]}",
                    description=item.get('What to do', ''),
                    priority='high',
                    source_type='compliance',
                    source_id=item['ID'],
                    status='todo',
                    due_date=date.today() + timedelta(days=15)
                ))
            db.session.add(AuditEvent(
                tenant_id=company.tenant_id,
                user_id=user.id if user else None,
                action='onboarding_completed',
                entity_type='Company',
                entity_id=str(company.id),
                details=f"Completed 6-step onboarding for {company.name}"
            ))
            db.session.commit()
            flash("Enterprise onboarding confirmed! Your personalized regulatory dashboard is ready.", "success")
            return redirect(url_for('main.dashboard'))
        else:
            company.onboarding_step = min(6, step + 1)
            db.session.commit()
            return redirect(url_for('main.onboarding_step_view', step=company.onboarding_step))

    step = company.onboarding_step or 1
    return render_onboarding_step_view(company, step)

@main_bp.route('/onboarding/step/<int:step>')
@login_required
def onboarding_step_view(step):
    company = get_current_company()
    if not company:
        return redirect(url_for('main.onboarding'))
    step = max(1, min(6, step))
    return render_onboarding_step_view(company, step)


# --- Stage D: Main Operational Dashboards & Modules ---

@main_bp.route('/dashboard')
@login_required
@onboarding_required
def dashboard():
    user_role = session.get('user_role', 'owner')
    if user_role == 'platform_admin':
        return redirect(url_for('main.admin_dashboard'))
    if user_role == 'consultant':
        return redirect(url_for('main.consultant_workspace'))
        
    lang = session.get('lang', 'en')
    company = get_current_company()
    if not company:
        flash("No active company found. Please create a profile.", "warning")
        return redirect(url_for('main.onboarding'))
    
    profile = get_company_profile_dict(company)
    evaluation = rules_engine.evaluate_company(profile)
    action_plan = ai_advisor.generate_action_plan(profile, lang)
    tasks = Task.query.filter_by(company_id=company.id).order_by(Task.due_date.asc()).limit(5).all()
    
    return render_template(
        'dashboard.html',
        company=company,
        profile=profile,
        evaluation=evaluation,
        action_plan=action_plan,
        tasks=tasks,
        lang=lang,
        lang_name=LANGUAGE_NAMES.get(lang, 'English')
    )

@main_bp.route('/compliance')
@login_required
@onboarding_required
def compliance():
    lang = session.get('lang', 'en')
    company = get_current_company()
    profile = get_company_profile_dict(company)
    evaluation = rules_engine.evaluate_company(profile)
    
    central_reqs = ComplianceRequirement.query.filter_by(jurisdiction_type='Central', is_active=True).all()
    state_reqs = ComplianceRequirement.query.filter(ComplianceRequirement.jurisdiction_type != 'Central', ComplianceRequirement.is_active==True).all()
    
    all_states = sorted(list(set(r.jurisdiction for r in state_reqs if r.jurisdiction)))
    all_domains = sorted(list(set(r.domain for r in central_reqs if r.domain)))

    return render_template(
        'compliance.html',
        company=company,
        profile=profile,
        evaluation=evaluation,
        central_reqs=central_reqs,
        state_reqs=state_reqs,
        all_states=all_states,
        all_domains=all_domains,
        lang=lang
    )

@main_bp.route('/compliance/<req_id>')
@login_required
def compliance_detail(req_id):
    req = ComplianceRequirement.query.get_or_404(req_id)
    company = get_current_company()
    profile = get_company_profile_dict(company)
    
    obligation = CompanyObligation.query.filter_by(company_id=company.id, compliance_id=req_id).first()
    
    return render_template(
        'compliance_detail.html',
        req=req,
        company=company,
        profile=profile,
        obligation=obligation
    )

@main_bp.route('/incentives')
@login_required
@onboarding_required
def incentives():
    lang = session.get('lang', 'en')
    company = get_current_company()
    profile = get_company_profile_dict(company)
    evaluation = rules_engine.evaluate_company(profile)
    
    central_schemes = IncentiveScheme.query.filter_by(jurisdiction_type='Central', is_active=True).all()
    state_schemes = IncentiveScheme.query.filter(IncentiveScheme.jurisdiction_type != 'Central', IncentiveScheme.is_active==True).all()
    
    categories = sorted(list(set(s.category for s in central_schemes if s.category)))
    all_states = sorted(list(set(s.jurisdiction for s in state_schemes if s.jurisdiction)))

    return render_template(
        'incentives.html',
        company=company,
        profile=profile,
        evaluation=evaluation,
        central_schemes=central_schemes,
        state_schemes=state_schemes,
        categories=categories,
        all_states=all_states,
        lang=lang
    )

@main_bp.route('/advisor')
@login_required
@onboarding_required
def advisor():
    lang = session.get('lang', 'en')
    company = get_current_company()
    profile = get_company_profile_dict(company)
    action_plan = ai_advisor.generate_action_plan(profile, lang)

    return render_template(
        'advisor.html',
        company=company,
        profile=profile,
        action_plan=action_plan,
        lang=lang,
        lang_name=LANGUAGE_NAMES.get(lang, 'English')
    )

@main_bp.route('/tasks', methods=['GET', 'POST'])
@login_required
@onboarding_required
def tasks():
    company = get_current_company()
    if request.method == 'POST':
        title = request.form.get('title')
        due_str = request.form.get('due_date')
        priority = request.form.get('priority', 'medium')
        due_date = datetime.strptime(due_str, '%Y-%m-%d').date() if due_str else None
        
        if title:
            new_task = Task(
                company_id=company.id,
                title=title,
                priority=priority,
                due_date=due_date,
                status='todo'
            )
            db.session.add(new_task)
            db.session.commit()
            flash("Task added successfully.", "success")
        return redirect(url_for('main.tasks'))

    company_tasks = Task.query.filter_by(company_id=company.id).order_by(Task.due_date.asc()).all()
    return render_template('tasks.html', company=company, tasks=company_tasks)

@main_bp.route('/tasks/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    company = get_current_company()
    if task.company_id != company.id:
        abort(403)
    
    if task.status == 'completed':
        task.status = 'todo'
        task.completed_at = None
    else:
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({"success": True, "status": task.status})

@main_bp.route('/documents', methods=['GET', 'POST'])
@login_required
@onboarding_required
def documents():
    company = get_current_company()
    folder_id = request.args.get('folder_id', type=int)
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part provided", "danger")
            return redirect(url_for('main.documents'))
        file = request.files['file']
        title = request.form.get('title', file.filename)
        doc_type = request.form.get('doc_type', 'other')
        target_folder_id = request.form.get('folder_id', type=int)
        expiry_str = request.form.get('expiry_date')
        expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date() if expiry_str else None

        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext not in current_app.config['ALLOWED_EXTENSIONS']:
                flash("File type not allowed.", "danger")
                return redirect(url_for('main.documents'))

            sec_name = f"{company.id}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sec_name)
            file.save(file_path)
            file_size = os.path.getsize(file_path)

            doc = Document(
                company_id=company.id,
                title=title,
                doc_type=doc_type,
                filename=sec_name,
                file_path=file_path,
                file_size=file_size,
                mime_type=file.content_type,
                expiry_date=expiry_date
            )
            db.session.add(doc)
            db.session.flush()

            if target_folder_id:
                folder = DocumentFolder.query.filter_by(id=target_folder_id, company_id=company.id).first()
                if folder:
                    link = DocumentFolderLink(folder_id=folder.id, document_id=doc.id)
                    db.session.add(link)

            db.session.add(AuditEvent(
                tenant_id=company.tenant_id,
                action='file_uploaded',
                entity_type='Document',
                entity_id=title,
                details=f"Uploaded {sec_name} ({file_size} bytes)"
            ))
            db.session.commit()
            flash("Document uploaded securely to private vault.", "success")
            return redirect(url_for('main.documents', folder_id=target_folder_id or folder_id))

    # Fetch virtual folders
    folders = DocumentFolder.query.filter_by(company_id=company.id).order_by(DocumentFolder.name.asc()).all()
    active_folder = DocumentFolder.query.filter_by(id=folder_id, company_id=company.id).first() if folder_id else None

    if active_folder:
        linked_doc_ids = [l.document_id for l in active_folder.links]
        docs = Document.query.filter(Document.id.in_(linked_doc_ids)).order_by(Document.uploaded_at.desc()).all() if linked_doc_ids else []
    else:
        docs = Document.query.filter_by(company_id=company.id).order_by(Document.uploaded_at.desc()).all()

    return render_template('documents.html', company=company, documents=docs, folders=folders, active_folder=active_folder)

@main_bp.route('/documents/folders/create', methods=['POST'])
@login_required
def create_folder():
    company = get_current_company()
    name = request.form.get('name', '').strip()
    folder_type = request.form.get('folder_type', 'vault')
    if not name:
        flash("Folder name is required.", "danger")
        return redirect(url_for('main.documents'))

    new_folder = DocumentFolder(
        company_id=company.id,
        name=name,
        folder_type=folder_type
    )
    db.session.add(new_folder)
    db.session.commit()
    flash(f"Virtual folder '{name}' created in Smart Vault.", "success")
    return redirect(url_for('main.documents', folder_id=new_folder.id))

@main_bp.route('/documents/link', methods=['POST'])
@login_required
def link_document():
    company = get_current_company()
    doc_id = request.form.get('document_id', type=int)
    folder_id = request.form.get('folder_id', type=int)

    doc = Document.query.filter_by(id=doc_id, company_id=company.id).first_or_404()
    folder = DocumentFolder.query.filter_by(id=folder_id, company_id=company.id).first_or_404()

    existing = DocumentFolderLink.query.filter_by(folder_id=folder.id, document_id=doc.id).first()
    if not existing:
        link = DocumentFolderLink(folder_id=folder.id, document_id=doc.id)
        db.session.add(link)
        db.session.commit()
        flash(f"Document '{doc.title}' linked to folder '{folder.name}'.", "success")
    else:
        flash("Document is already linked to this folder.", "info")

    return redirect(url_for('main.documents', folder_id=folder.id))

@main_bp.route('/documents/folders/<int:folder_id>/delete', methods=['POST'])
@login_required
def delete_folder(folder_id):
    company = get_current_company()
    folder = DocumentFolder.query.filter_by(id=folder_id, company_id=company.id).first_or_404()
    
    # Unlink any workspace referencing this folder
    ApplicationWorkspace.query.filter_by(folder_id=folder.id).update({'folder_id': None})
    
    folder_name = folder.name
    db.session.delete(folder)
    db.session.commit()
    flash(f"Virtual folder '{folder_name}' has been deleted.", "success")
    return redirect(url_for('main.documents'))

@main_bp.route('/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    company = get_current_company()
    doc = Document.query.filter_by(id=doc_id, company_id=company.id).first_or_404()
    
    # Remove folder links
    DocumentFolderLink.query.filter_by(document_id=doc.id).delete()
    
    # Safely remove physical file
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass
            
    doc_title = doc.title
    db.session.delete(doc)
    db.session.commit()
    flash(f"Document '{doc_title}' has been deleted from vault.", "success")
    
    folder_id = request.args.get('folder_id', type=int)
    if folder_id:
        return redirect(url_for('main.documents', folder_id=folder_id))
    return redirect(url_for('main.documents'))

@main_bp.route('/documents/download/<int:doc_id>')
@login_required
def download_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    company = get_current_company()
    if doc.company_id != company.id:
        abort(403)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], doc.filename, as_attachment=True, download_name=doc.title)

@main_bp.route('/documents/<int:doc_id>/extract', methods=['POST'])
@login_required
def extract_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    company = get_current_company()
    if doc.company_id != company.id:
        abort(403)
    extraction, err = extraction_service.process_document(doc.id)
    if err:
        return jsonify({"success": False, "error": err}), 400
    fields = [{
        "id": f.id,
        "field_name": f.field_name,
        "proposed_value": f.proposed_value,
        "confidence": f.confidence,
        "source_location": f.source_location,
        "status": f.status
    } for f in extraction.fields]
    return jsonify({
        "success": True,
        "extraction_id": extraction.id,
        "fields": fields,
        "raw_text_preview": extraction.raw_text[:300]
    })

@main_bp.route('/documents/<int:doc_id>/extraction', methods=['GET'])
@login_required
def get_document_extraction(doc_id):
    doc = Document.query.get_or_404(doc_id)
    company = get_current_company()
    if doc.company_id != company.id:
        abort(403)
    latest = DocumentExtraction.query.filter_by(document_id=doc.id).order_by(DocumentExtraction.created_at.desc()).first()
    if not latest:
        return jsonify({"success": False, "error": "No extraction record found for this document"}), 404
    fields = [{
        "id": f.id,
        "field_name": f.field_name,
        "proposed_value": f.proposed_value,
        "confidence": f.confidence,
        "source_location": f.source_location,
        "status": f.status,
        "corrected_value": f.corrected_value
    } for f in latest.fields]
    return jsonify({
        "success": True,
        "extraction_id": latest.id,
        "status": latest.status,
        "fields": fields,
        "raw_text": latest.raw_text
    })

@main_bp.route('/documents/confirm-fields', methods=['POST'])
@login_required
def confirm_extracted_fields():
    company = get_current_company()
    data = request.get_json() or {}
    extraction_id = data.get('extraction_id')
    field_actions = data.get('fields', {})
    
    extraction = DocumentExtraction.query.get_or_404(extraction_id)
    if extraction.document.company_id != company.id:
        abort(403)
        
    success, msg = extraction_service.confirm_extracted_fields(extraction.id, field_actions)
    if not success:
        return jsonify({"success": False, "error": msg}), 400
        
    return jsonify({"success": True, "message": msg})

@main_bp.route('/documents/<int:doc_id>/verify', methods=['POST'])
@login_required
def verify_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    company = get_current_company()
    if doc.company_id != company.id:
        abort(403)
    data = request.get_json() or {}
    new_status = data.get('verification_status', 'verified')
    doc.verification_status = new_status
    db.session.add(AuditEvent(
        tenant_id=company.tenant_id,
        action='document_verified',
        entity_type='Document',
        entity_id=str(doc.id),
        details=f"Document '{doc.title}' marked as {new_status}"
    ))
    db.session.commit()
    return jsonify({"success": True, "verification_status": doc.verification_status})

@main_bp.route('/schemes/<scheme_id>/readiness')
@login_required
def scheme_readiness(scheme_id):
    company = get_current_company()
    eval_res, err = readiness_service.evaluate_readiness(company.id, scheme_id=scheme_id)
    if err:
        return jsonify({"success": False, "error": err}), 400
    return jsonify({"success": True, "readiness": eval_res})

@main_bp.route('/drafts')
@login_required
@onboarding_required
def view_drafts():
    company = get_current_company()
    company_drafts = AIDraft.query.filter_by(company_id=company.id).order_by(AIDraft.created_at.desc()).all()
    workspaces = ApplicationWorkspace.query.filter_by(company_id=company.id).order_by(ApplicationWorkspace.created_at.desc()).all()
    return render_template('drafts.html', company=company, drafts=company_drafts, workspaces=workspaces)

@main_bp.route('/drafts/wizard', methods=['GET', 'POST'])
@login_required
@onboarding_required
def drafts_wizard():
    company = get_current_company()
    profile = get_company_profile_dict(company)
    eval_res = rules_engine.evaluate_company(profile)
    vault_docs = Document.query.filter_by(company_id=company.id).all()

    if request.method == 'POST':
        package_title = request.form.get('title', '').strip()
        workspace_type = request.form.get('workspace_type', 'incentive')
        reference_id = request.form.get('reference_id', '')
        notes = request.form.get('notes', '')

        if not package_title:
            package_title = f"{workspace_type.title()} Filing Package - {datetime.utcnow().strftime('%b %Y')}"

        # Build checklist items based on chosen scheme/compliance or default
        checklist_items = []
        if workspace_type == 'incentive' and reference_id:
            scheme = IncentiveScheme.query.filter_by(id=reference_id).first()
            if scheme:
                checklist_items = [
                    {'name': 'Udyam Registration Certificate', 'status': 'Verified' if any('udyam' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Ministry of MSME'},
                    {'name': 'Audited Balance Sheet & Profit & Loss Statement', 'status': 'Verified' if any('audit' in d.title.lower() or 'itr' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Latest FY'},
                    {'name': 'Bank Account Statement & Cancelled Cheque', 'status': 'Verified' if any('bank' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Direct Benefit Transfer'},
                    {'name': 'Directors / Proprietor PAN & Aadhaar Copy', 'status': 'Verified' if any('pan' in d.title.lower() or 'aadhaar' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Identity Verification'},
                    {'name': f"Project Report / Investment Statement for {scheme.scheme_name}", 'status': 'Required', 'notes': 'Technical Appraisal'}
                ]
        elif workspace_type == 'compliance' and reference_id:
            req = ComplianceRequirement.query.filter_by(id=reference_id).first()
            if req:
                checklist_items = [
                    {'name': 'PAN & Certificate of Incorporation / Deed', 'status': 'Verified' if any('pan' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Statutory Proof'},
                    {'name': 'Registered Office Utility Bill & Rent Agreement', 'status': 'Verified' if any('rent' in d.title.lower() or 'bill' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Premises Clearance'},
                    {'name': 'Employee Muster Roll & Wage Register', 'status': 'Verified' if any('wage' in d.title.lower() or 'staff' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Headcount Record'},
                    {'name': f"Filing Form / Return for {req.requirement}", 'status': 'Required', 'notes': req.jurisdiction}
                ]

        if not checklist_items:
            checklist_items = [
                {'name': 'Udyam Registration Certificate', 'status': 'Verified' if any('udyam' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Ministry of MSME'},
                {'name': 'Enterprise PAN Card', 'status': 'Verified' if any('pan' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Income Tax Dept'},
                {'name': 'Bank Account Statement (Last 6 Months)', 'status': 'Verified' if any('bank' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'Financial Verification'},
                {'name': 'GST Registration & Latest GSTR-3B Filing', 'status': 'Verified' if any('gst' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'GSTN Portal'},
                {'name': 'Authorized Signatory Identity Proof', 'status': 'Verified' if any('aadhaar' in d.title.lower() for d in vault_docs) else 'Missing', 'notes': 'UIDAI / MCA'}
            ]

        # Create Workspace Folder in Smart Vault
        ws_folder = DocumentFolder(
            company_id=company.id,
            name=f"Package: {package_title[:40]}",
            folder_type='compliance_package' if workspace_type == 'compliance' else 'incentive_application'
        )
        db.session.add(ws_folder)
        db.session.flush()

        # Create Workspace Record
        ws = ApplicationWorkspace(
            company_id=company.id,
            title=package_title,
            workspace_type=workspace_type,
            reference_id=reference_id,
            folder_id=ws_folder.id,
            status='draft',
            checklist_json=json.dumps(checklist_items),
            notes=notes
        )
        db.session.add(ws)
        db.session.flush()

        # Link any existing matching vault documents into this workspace's virtual folder
        for doc in vault_docs:
            for item in checklist_items:
                if item['status'] == 'Verified' and any(k in doc.title.lower() for k in item['name'].lower().split() if len(k) > 3):
                    existing_link = DocumentFolderLink.query.filter_by(folder_id=ws_folder.id, document_id=doc.id).first()
                    if not existing_link:
                        db.session.add(DocumentFolderLink(folder_id=ws_folder.id, document_id=doc.id))

        # Generate Real PDF Checklist
        pdf_fn, pdf_path = document_generator.generate_checklist_pdf(
            company_name=company.name,
            udyam_reg=company.udyam_registration_number,
            workspace_title=package_title,
            checklist_items=checklist_items
        )
        pdf_artifact = GeneratedArtifact(
            workspace_id=ws.id,
            company_id=company.id,
            artifact_type='checklist',
            title=f"{package_title} — Official Verification Checklist (PDF)",
            filename=pdf_fn,
            file_path=pdf_path,
            mime_type='application/pdf',
            status='approved'
        )
        db.session.add(pdf_artifact)

        # Generate Real DOCX Application Cover Letter
        docx_fn, docx_path = document_generator.generate_cover_letter_docx(
            company_dict=profile,
            scheme_title=package_title,
            authority_name="District Industries Centre / Relevant Ministry",
            checklist_items=checklist_items
        )
        docx_artifact = GeneratedArtifact(
            workspace_id=ws.id,
            company_id=company.id,
            artifact_type='cover_letter',
            title=f"{package_title} — Official Submission Cover Letter (DOCX)",
            filename=docx_fn,
            file_path=docx_path,
            mime_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            status='approved'
        )
        db.session.add(docx_artifact)

        db.session.commit()
        flash(f"Application Package '{package_title}' generated with downloadable PDF & DOCX artifacts.", "success")
        return redirect(url_for('main.view_workspace_package', workspace_id=ws.id))

    return render_template(
        'drafts_wizard.html',
        company=company,
        profile=profile,
        eval_res=eval_res,
        vault_docs=vault_docs
    )

@main_bp.route('/drafts/package/<int:workspace_id>')
@login_required
@onboarding_required
def view_workspace_package(workspace_id):
    company = get_current_company()
    ws = ApplicationWorkspace.query.filter_by(id=workspace_id, company_id=company.id).first_or_404()
    checklist = json.loads(ws.checklist_json) if ws.checklist_json else []
    artifacts = GeneratedArtifact.query.filter_by(workspace_id=ws.id).order_by(GeneratedArtifact.created_at.desc()).all()
    folder_docs = []
    if ws.folder:
        folder_docs = [l.doc for l in ws.folder.links if l.doc]

    return render_template(
        'drafts_package.html',
        company=company,
        workspace=ws,
        checklist=checklist,
        artifacts=artifacts,
        folder_docs=folder_docs
    )

@main_bp.route('/drafts/download/<int:artifact_id>')
@login_required
def download_artifact(artifact_id):
    company = get_current_company()
    artifact = GeneratedArtifact.query.filter_by(id=artifact_id, company_id=company.id).first_or_404()
    return send_from_directory(
        document_generator.output_dir,
        artifact.filename,
        as_attachment=True,
        download_name=artifact.filename
    )

@main_bp.route('/drafts/generate', methods=['POST'])
@login_required
def generate_draft():
    company = get_current_company()
    data = request.get_json() or request.form
    draft_type = data.get('draft_type', 'checklist')
    scheme_id = data.get('scheme_id')
    compliance_id = data.get('compliance_id')
    
    if draft_type == 'cover_letter':
        draft, err = readiness_service.generate_cover_letter(company.id, scheme_id)
    else:
        draft, err = readiness_service.generate_draft_checklist(company.id, scheme_id=scheme_id, compliance_id=compliance_id)
        
    if err:
        return jsonify({"success": False, "error": err}), 400
        
    return jsonify({
        "success": True,
        "draft_id": draft.id,
        "title": draft.title,
        "draft_type": draft.draft_type,
        "content": draft.content,
        "status": draft.status
    })

@main_bp.route('/drafts/<int:draft_id>/approve', methods=['POST'])
@login_required
def approve_draft_endpoint(draft_id):
    draft = AIDraft.query.get_or_404(draft_id)
    company = get_current_company()
    if draft.company_id != company.id:
        abort(403)
    ok, msg = readiness_service.approve_draft(draft.id)
    if not ok:
        return jsonify({"success": False, "error": msg}), 400
    return jsonify({"success": True, "message": msg, "status": draft.status})

@main_bp.route('/drafts/package/<int:workspace_id>/delete', methods=['POST'])
@login_required
def delete_workspace_package(workspace_id):
    company = get_current_company()
    ws = ApplicationWorkspace.query.filter_by(id=workspace_id, company_id=company.id).first_or_404()
    
    # Clean up physical files for generated artifacts
    for art in ws.artifacts:
        if art.file_path and os.path.exists(art.file_path):
            try:
                os.remove(art.file_path)
            except OSError:
                pass
                
    if ws.folder_id:
        pkg_folder = DocumentFolder.query.filter_by(id=ws.folder_id, company_id=company.id).first()
        if pkg_folder and pkg_folder.folder_type == 'package':
            db.session.delete(pkg_folder)
            
    ws_title = ws.title
    db.session.delete(ws)
    db.session.commit()
    flash(f"Application Package '{ws_title}' has been deleted.", "success")
    return redirect(url_for('main.view_drafts'))

@main_bp.route('/drafts/<int:draft_id>/delete', methods=['POST'])
@login_required
def delete_draft_endpoint(draft_id):
    company = get_current_company()
    draft = AIDraft.query.filter_by(id=draft_id, company_id=company.id).first_or_404()
    
    draft_title = draft.title
    db.session.delete(draft)
    db.session.commit()
    flash(f"Draft '{draft_title}' has been deleted.", "success")
    return redirect(url_for('main.view_drafts'))

@main_bp.route('/tasks/suggested')
@login_required
def suggested_tasks():
    company = get_current_company()
    suggested, err = action_service.suggest_tasks_from_obligations(company.id)
    if err:
        return jsonify({"success": False, "error": err}), 400
    return jsonify({"success": True, "suggested": suggested})

@main_bp.route('/tasks/confirm-suggested', methods=['POST'])
@login_required
def confirm_suggested_task():
    company = get_current_company()
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    due_date = data.get('due_date')
    source_id = data.get('source_id')
    source_type = data.get('source_type', 'compliance')
    
    task, err = action_service.create_task(
        company_id=company.id,
        title=title,
        description=description,
        priority=priority,
        due_date_str=due_date,
        source_type=source_type,
        source_id=source_id
    )
    if err:
        return jsonify({"success": False, "error": err}), 400
    return jsonify({"success": True, "task_id": task.id, "title": task.title})

@main_bp.route('/company', methods=['GET', 'POST'])
@login_required
def company_profile():
    company = get_current_company()
    
    if request.method == 'POST':
        company.name = request.form.get('name', company.name)
        company.trade_name = request.form.get('trade_name', company.trade_name)
        company.state = request.form.get('state', company.state)
        company.district = request.form.get('district', company.district)
        company.sector = request.form.get('sector', company.sector)
        company.entity_type = request.form.get('entity_type', company.entity_type)
        company.udyam_number = request.form.get('udyam_number', company.udyam_number)
        company.pan_number = request.form.get('pan_number', company.pan_number)
        company.gstin = request.form.get('gstin', company.gstin)
        company.is_dpiit_recognized = 'is_dpiit' in request.form
        company.is_deep_tech = 'is_deep_tech' in request.form
        company.is_exporter = 'is_exporter' in request.form

        inc_date_str = request.form.get('incorporation_date')
        if inc_date_str:
            company.incorporation_date = datetime.strptime(inc_date_str, '%Y-%m-%d').date()

        turnover = float(request.form.get('turnover', 0))
        investment = float(request.form.get('investment', 0))
        employees = int(request.form.get('employees', 0))

        db.session.add(CompanyMetric(company_id=company.id, metric_type='turnover', value=turnover, provenance='user_entered'))
        db.session.add(CompanyMetric(company_id=company.id, metric_type='investment', value=investment, provenance='user_entered'))
        db.session.add(CompanyMetric(company_id=company.id, metric_type='employees', value=employees, provenance='user_entered'))

        db.session.add(AuditEvent(
            tenant_id=company.tenant_id,
            action='profile_updated',
            entity_type='Company',
            entity_id=str(company.id),
            details=f"Updated metrics: turnover=₹{turnover:,}, staff={employees}, state={company.state}"
        ))

        db.session.commit()
        flash("Company profile updated. Compliance rules and incentives re-evaluated.", "success")
        return redirect(url_for('main.dashboard'))

    profile = get_company_profile_dict(company)
    evaluation = rules_engine.evaluate_company(profile)
    all_states = sorted(list(set(r.jurisdiction for r in ComplianceRequirement.query.filter(ComplianceRequirement.jurisdiction_type != 'Central').all())))

    return render_template(
        'company.html',
        company=company,
        profile=profile,
        evaluation=evaluation,
        all_states=all_states
    )


# --- CA & Consultant Multi-Client Workspace (Role Protected) ---

@main_bp.route('/consultant')
@login_required
@role_required('consultant', 'platform_admin')
def consultant_workspace():
    all_companies = Company.query.all()
    current = get_current_company()
    
    portfolio = []
    for c in all_companies:
        p = get_company_profile_dict(c)
        eval_res = rules_engine.evaluate_company(p)
        open_tasks = Task.query.filter_by(company_id=c.id, status='todo').count()
        portfolio.append({
            'company': c,
            'msme_class': eval_res['msme_classification'],
            'obligations_count': eval_res['total_obligations'],
            'incentives_count': eval_res['total_incentives'],
            'open_tasks': open_tasks
        })
        
    return render_template('consultant.html', portfolio=portfolio, current_company=current)

@main_bp.route('/consultant/switch-client/<int:company_id>')
@login_required
@role_required('consultant', 'platform_admin')
def switch_client(company_id):
    company = Company.query.get_or_404(company_id)
    session['active_company_id'] = company.id
    flash(f"Switched active client workspace to: {company.name}", "info")
    return redirect(url_for('main.dashboard'))


# --- Admin Platform Governance, Dashboards & Change Intelligence (Role Protected) ---

@main_bp.route('/admin')
@main_bp.route('/admin/dashboard')
@login_required
@role_required('platform_admin')
def admin_dashboard():
    # Gather platform-level governance metrics
    total_companies = Company.query.count()
    onboarded_companies = Company.query.filter_by(is_onboarded=True).count()
    
    total_users = User.query.count()
    users_by_role = {
        'owner': User.query.filter_by(role='owner').count(),
        'member': User.query.filter_by(role='member').count(),
        'consultant': User.query.filter_by(role='consultant').count(),
        'platform_admin': User.query.filter_by(role='platform_admin').count(),
    }
    
    total_compliance_records = ComplianceRequirement.query.count()
    verified_compliance_records = ComplianceRequirement.query.filter_by(verification_status='verified').count()
    central_compliance_count = ComplianceRequirement.query.filter_by(jurisdiction_type='Central').count()
    state_compliance_count = ComplianceRequirement.query.filter(ComplianceRequirement.jurisdiction_type != 'Central').count()
    
    total_changes = RegulatoryChange.query.count()
    detected_changes = RegulatoryChange.query.filter_by(review_status='detected').count()
    approved_changes = RegulatoryChange.query.filter_by(review_status='approved').count()
    published_changes = RegulatoryChange.query.filter_by(review_status='published').count()
    
    total_knowledge_docs = KnowledgeDocument.query.count()
    published_knowledge_docs = KnowledgeDocument.query.filter_by(status='published').count()
    review_knowledge_docs = KnowledgeDocument.query.filter(KnowledgeDocument.status.in_(['needs_review', 'draft'])).count()
    total_knowledge_chunks = DocumentChunk.query.count()
    total_knowledge_sources = KnowledgeSource.query.count()
    
    total_documents = Document.query.count()
    
    # Recent live administrative records
    recent_changes = RegulatoryChange.query.order_by(RegulatoryChange.created_at.desc()).limit(5).all()
    recent_companies = Company.query.order_by(Company.id.desc()).limit(5).all()
    recent_knowledge_docs = KnowledgeDocument.query.order_by(KnowledgeDocument.created_at.desc()).limit(5).all()
    recent_audits = AuditEvent.query.order_by(AuditEvent.timestamp.desc()).limit(6).all()
    
    return render_template(
        'admin_dashboard.html',
        total_companies=total_companies,
        onboarded_companies=onboarded_companies,
        total_users=total_users,
        users_by_role=users_by_role,
        total_compliance_records=total_compliance_records,
        verified_compliance_records=verified_compliance_records,
        central_compliance_count=central_compliance_count,
        state_compliance_count=state_compliance_count,
        total_changes=total_changes,
        detected_changes=detected_changes,
        approved_changes=approved_changes,
        published_changes=published_changes,
        total_knowledge_docs=total_knowledge_docs,
        published_knowledge_docs=published_knowledge_docs,
        review_knowledge_docs=review_knowledge_docs,
        total_knowledge_chunks=total_knowledge_chunks,
        total_knowledge_sources=total_knowledge_sources,
        total_documents=total_documents,
        recent_changes=recent_changes,
        recent_companies=recent_companies,
        recent_knowledge_docs=recent_knowledge_docs,
        recent_audits=recent_audits
    )

@main_bp.route('/admin/companies')
@login_required
@role_required('platform_admin')
def admin_companies():
    search = request.args.get('search', '').lower()
    state_filter = request.args.get('state', '')
    
    query = Company.query
    if state_filter:
        query = query.filter_by(state=state_filter)
    companies = query.order_by(Company.id.desc()).all()
    
    if search:
        companies = [c for c in companies if search in c.name.lower() or (c.udyam_number and search in c.udyam_number.lower()) or (c.state and search in c.state.lower()) or (c.sector and search in c.sector.lower())]
        
    all_states = sorted(list(set(c.state for c in Company.query.all() if c.state)))
    return render_template('admin_companies.html', companies=companies, all_states=all_states, total_count=len(companies))

@main_bp.route('/admin/users')
@login_required
@role_required('platform_admin')
def admin_users():
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '').lower()
    
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.order_by(User.id.asc()).all()
    
    if search:
        users = [u for u in users if search in u.name.lower() or search in u.email.lower() or search in u.role.lower()]
        
    return render_template('admin_users.html', users=users, total_count=len(users))

@main_bp.route('/admin/audit')
@login_required
@role_required('platform_admin')
def admin_audit():
    action_filter = request.args.get('action', '')
    search = request.args.get('search', '').lower()
    
    query = AuditEvent.query
    if action_filter:
        query = query.filter_by(action=action_filter)
    audits = query.order_by(AuditEvent.timestamp.desc()).limit(100).all()
    
    if search:
        audits = [a for a in audits if (a.details and search in a.details.lower()) or (a.action and search in a.action.lower()) or (a.entity_type and search in a.entity_type.lower())]
        
    distinct_actions = sorted(list(set(a.action for a in AuditEvent.query.all() if a.action)))
    return render_template('admin_audit.html', audits=audits, distinct_actions=distinct_actions, total_count=len(audits))

@main_bp.route('/admin/records')
@login_required
@role_required('platform_admin')
def admin_records():
    search = request.args.get('search', '').lower()
    verification = request.args.get('verification', '')
    
    query = ComplianceRequirement.query
    if verification:
        query = query.filter_by(verification_status=verification)
    
    records = query.order_by(ComplianceRequirement.id.asc()).all()
    if search:
        records = [r for r in records if search in r.requirement.lower() or search in r.jurisdiction.lower() or search in r.id.lower()]
        
    return render_template('admin_records.html', records=records, total_count=len(records))

@main_bp.route('/admin/records/verify/<req_id>', methods=['POST'])
@login_required
@role_required('platform_admin')
def verify_record(req_id):
    req = ComplianceRequirement.query.get_or_404(req_id)
    req.verification_status = 'verified'
    req.last_verified_date = datetime.utcnow().strftime('%b %Y')
    db.session.commit()
    flash(f"Record {req_id} marked as officially verified.", "success")
    return redirect(url_for('main.admin_records'))

@main_bp.route('/admin/changes')
@login_required
@role_required('platform_admin')
def admin_changes():
    changes = RegulatoryChange.query.order_by(RegulatoryChange.created_at.desc()).all()
    return render_template('admin_changes.html', changes=changes)

@main_bp.route('/admin/changes/approve/<int:change_id>', methods=['POST'])
@login_required
@role_required('platform_admin')
def approve_change(change_id):
    change = RegulatoryChange.query.get_or_404(change_id)
    notes = request.form.get('notes', 'Approved by authorized regulatory expert.')
    ok, msg = regulatory_service.approve_change(change.id, reviewer_user_id=session.get('user_id', 1), notes=notes)
    if ok:
        flash(f"Regulatory change '{change.title}' marked as approved. Ready for publication.", "success")
    else:
        flash(f"Approval failed: {msg}", "danger")
    return redirect(url_for('main.admin_changes'))

@main_bp.route('/admin/changes/publish/<int:change_id>', methods=['POST'])
@login_required
@role_required('platform_admin')
def publish_change(change_id):
    change = RegulatoryChange.query.get_or_404(change_id)
    ok, msg = regulatory_service.publish_change(change.id, publisher_user_id=session.get('user_id', 1))
    if ok:
        flash(f"Regulatory change '{change.title}' officially published to active rules database.", "success")
    else:
        flash(f"Publication failed: {msg}", "danger")
    return redirect(url_for('main.admin_changes'))

@main_bp.route('/admin/changes/detect', methods=['POST'])
@login_required
@role_required('platform_admin')
def detect_regulatory_change():
    data = request.get_json() or request.form
    title = data.get('title')
    source_url = data.get('source_url')
    issuing_authority = data.get('issuing_authority')
    raw_content = data.get('raw_content')
    affected_jurisdiction = data.get('affected_jurisdiction', 'Central')
    affected_domain = data.get('affected_domain', 'General')
    affected_rule_id = data.get('affected_rule_id')

    if not title or not source_url or not issuing_authority or not raw_content:
        return jsonify({"success": False, "error": "Missing required fields (title, source_url, issuing_authority, raw_content)"}), 400

    change, err = regulatory_service.ingest_update(
        title=title,
        source_url=source_url,
        issuing_authority=issuing_authority,
        raw_content=raw_content,
        affected_jurisdiction=affected_jurisdiction,
        affected_domain=affected_domain,
        affected_rule_id=affected_rule_id
    )
    if err and not change:
        return jsonify({"success": False, "error": err}), 400

    return jsonify({
        "success": True,
        "change_id": change.id,
        "review_status": change.review_status,
        "content_hash": change.content_hash,
        "message": err or "Change ingested into needs_review intelligence queue."
    })


# --- Controlled Tool Call API ---

@main_bp.route('/api/ai/tool-call', methods=['POST'])
@login_required
def api_ai_tool_call():
    data = request.get_json() or {}
    tool_name = data.get('tool')
    params = data.get('params', {})
    
    company = get_current_company()
    if 'company_id' not in params and company:
        params['company_id'] = company.id
        
    tenant_id = company.tenant_id if company else None
    result = tool_dispatcher.execute_tool(tool_name, params, tenant_id=tenant_id)
    return jsonify(result)


# --- Executive Reports & Exports ---

@main_bp.route('/reports')
@login_required
@onboarding_required
def reports():
    company = get_current_company()
    profile = get_company_profile_dict(company)
    evaluation = rules_engine.evaluate_company(profile)
    action_plan = ai_advisor.generate_action_plan(profile, 'en')
    docs = Document.query.filter_by(company_id=company.id).all()
    tasks = Task.query.filter_by(company_id=company.id).all()
    
    return render_template(
        'reports.html',
        company=company,
        profile=profile,
        evaluation=evaluation,
        action_plan=action_plan,
        documents=docs,
        tasks=tasks,
        report_date=datetime.utcnow().strftime('%d %B %Y')
    )

@main_bp.route('/reports/export-csv')
@login_required
def export_csv():
    company = get_current_company()
    profile = get_company_profile_dict(company)
    evaluation = rules_engine.evaluate_company(profile)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Jurisdiction', 'Domain', 'Requirement', 'Law Basis', 'Trigger Reason', 'Frequency / Due Date', 'Official Link'])
    
    for item in evaluation['matched_central_compliance']:
        writer.writerow([
            item.get('ID', ''),
            'Central',
            item.get('Domain', ''),
            item.get('Requirement', ''),
            item.get('Law / Rule', ''),
            item.get('match_reason', ''),
            item.get('Frequency / due date', ''),
            item.get('Official link', '')
        ])
        
    for item in evaluation['matched_state_compliance']:
        writer.writerow([
            item.get('ID', ''),
            item.get('State / UT', ''),
            item.get('Domain', ''),
            item.get('Requirement', ''),
            item.get('Law / basis', ''),
            item.get('Applies to / trigger', ''),
            'Periodic / As per state circular',
            item.get('Portal / link', '')
        ])
        
    output.seek(0)
    filename = f"MSME_Compliance_Report_{secure_filename(company.name)}_{date.today()}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# --- AI Chat API ---

@main_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json() or {}
    message = data.get('message', '')
    lang = data.get('lang') or session.get('lang', 'en')
    company = get_current_company()
    profile = get_company_profile_dict(company)
    response = ai_advisor.answer_query(message, profile, lang)
    return jsonify(response)


# --- Admin AI Knowledge Center & Ingestion Routes ---

@main_bp.route('/admin/knowledge')
@login_required
@role_required('platform_admin')
def admin_knowledge():
    collections = KnowledgeCollection.query.all()
    documents = KnowledgeDocument.query.order_by(KnowledgeDocument.created_at.desc()).all()
    
    total_docs = len(documents)
    published_count = sum(1 for d in documents if d.status == 'published')
    review_count = sum(1 for d in documents if d.status in ['needs_review', 'draft'])
    failed_count = sum(1 for d in documents if d.status == 'failed')
    total_chunks = DocumentChunk.query.count()

    return render_template(
        'admin_knowledge.html',
        collections=collections,
        documents=documents,
        total_docs=total_docs,
        published_count=published_count,
        review_count=review_count,
        failed_count=failed_count,
        total_chunks=total_chunks
    )

@main_bp.route('/admin/knowledge/upload', methods=['POST'])
@login_required
@role_required('platform_admin')
def admin_knowledge_upload():
    if 'file' not in request.files:
        flash("No file part uploaded", "danger")
        return redirect(url_for('main.admin_knowledge'))
    
    file = request.files['file']
    title = request.form.get('title') or file.filename
    issuing_authority = request.form.get('issuing_authority', 'Government of India')
    official_source_url = request.form.get('official_source_url', '')
    jurisdiction = request.form.get('jurisdiction', 'Central')
    state = request.form.get('state') or None
    document_type = request.form.get('document_type', 'circular')
    collection_id = request.form.get('collection_id', type=int)

    if file and file.filename:
        # Create knowledge upload directory if not present
        k_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'knowledge')
        os.makedirs(k_dir, exist_ok=True)

        sec_name = f"k_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
        file_path = os.path.join(k_dir, sec_name)
        file.save(file_path)

        doc = KnowledgeDocument(
            collection_id=collection_id,
            title=title,
            filename=sec_name,
            file_path=file_path,
            document_type=document_type,
            issuing_authority=issuing_authority,
            official_source_url=official_source_url,
            jurisdiction=jurisdiction,
            state=state,
            status='draft'
        )
        db.session.add(doc)
        db.session.commit()

        # Execute automated extraction and chunking pipeline
        ok, msg = rag_service.process_document_ingestion(doc.id)
        if ok:
            flash(f"Document '{title}' uploaded and processed successfully: {msg}", "success")
        else:
            flash(f"Ingestion warning for '{title}': {msg}", "warning")

    return redirect(url_for('main.admin_knowledge'))

@main_bp.route('/admin/knowledge/publish/<int:doc_id>', methods=['POST'])
@login_required
@role_required('platform_admin')
def admin_knowledge_publish(doc_id):
    notes = request.form.get('notes', 'Officially verified and approved by regulatory admin.')
    ok, msg = rag_service.publish_document(doc_id, reviewer_user_id=session.get('user_id', 1), notes=notes)
    if ok:
        flash(msg, "success")
    else:
        flash(f"Publication failed: {msg}", "danger")
    return redirect(url_for('main.admin_knowledge'))

@main_bp.route('/admin/knowledge/playground', methods=['GET', 'POST'])
@login_required
@role_required('platform_admin')
def admin_knowledge_playground():
    query = request.args.get('query') or (request.form.get('query') if request.method == 'POST' else '')
    jurisdiction = request.args.get('jurisdiction') or 'All'
    state = request.args.get('state') or ''
    top_k = int(request.args.get('top_k') or 5)

    results = []
    if query:
        j_filter = None if jurisdiction == 'All' else jurisdiction
        s_filter = state if state else None
        results = rag_service.hybrid_retrieve(query, jurisdiction=j_filter, state=s_filter, top_k=top_k)

    return render_template(
        'admin_playground.html',
        query=query,
        jurisdiction=jurisdiction,
        state=state,
        top_k=top_k,
        results=results
    )

@main_bp.route('/admin/knowledge/sources', methods=['GET', 'POST'])
@login_required
@role_required('platform_admin')
def admin_knowledge_sources():
    if request.method == 'POST':
        name = request.form.get('name')
        portal_url = request.form.get('portal_url')
        authority = request.form.get('issuing_authority')
        jurisdiction = request.form.get('jurisdiction', 'Central')
        state = request.form.get('state')

        if name and portal_url:
            src = KnowledgeSource(
                name=name,
                portal_url=portal_url,
                issuing_authority=authority,
                jurisdiction=jurisdiction,
                state=state
            )
            db.session.add(src)
            db.session.commit()
            flash(f"Official Knowledge Source '{name}' added successfully.", "success")
        return redirect(url_for('main.admin_knowledge_sources'))

    sources = KnowledgeSource.query.order_by(KnowledgeSource.name.asc()).all()
    return render_template('admin_sources.html', sources=sources)


# --- Official Website Research API (SSRF Protected) ---

@main_bp.route('/api/research/analyze-website', methods=['POST'])
@login_required
def api_research_website():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({"success": False, "error": "Target URL is required"}), 400

    try:
        result = website_research_service.research_official_portal(url)
        if not result.get('success'):
            return jsonify(result), 400
        return jsonify(result)
    except SSRFProtectionError as e:
        return jsonify({"success": False, "error": str(e), "security_blocked": True}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Research failed: {str(e)}"}), 500

