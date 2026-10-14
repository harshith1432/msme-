"""
Comprehensive Test Suite for MSME Compliance & Incentives Navigator.
Tests:
  - 2025 Revised MSME Threshold Rules
  - Feb 2026 DPIIT Startup Definitions (G.S.R. 108(E))
  - Statutory Employer & Turnover Ladder Triggers
  - 8 Languages Multilingual AI Action Cards
  - Regulatory Records Database Integrity (628 records)
  - Multi-tenant Isolation & Consultant Workspace
  - Web Routes, CSV Export, and Document Vault
"""
import os
import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import Company, ComplianceRequirement, IncentiveScheme, Task, Document, User
from app.services.rules_engine import RulesEngine
from app.services.ai_advisor import AIAdvisor, ACTION_HEADERS

@pytest.fixture
def app():
    test_app = create_app(TestingConfig)
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# 1. MSME Classification Tests (1 April 2025 Limits)
def test_msme_classification_micro():
    engine = RulesEngine()
    # Micro: <= 2.5 Cr investment & <= 10 Cr turnover
    assert engine.classify_msme(15000000, 45000000) == "Micro Enterprise"
    assert engine.classify_msme(25000000, 100000000) == "Micro Enterprise"

def test_msme_classification_small():
    engine = RulesEngine()
    # Small: <= 25 Cr investment & <= 100 Cr turnover
    assert engine.classify_msme(50000000, 200000000) == "Small Enterprise"
    assert engine.classify_msme(250000000, 1000000000) == "Small Enterprise"

def test_msme_classification_medium():
    engine = RulesEngine()
    # Medium: <= 125 Cr investment & <= 500 Cr turnover
    assert engine.classify_msme(500000000, 2500000000) == "Medium Enterprise"
    assert engine.classify_msme(1250000000, 5000000000) == "Medium Enterprise"

def test_msme_classification_beyond():
    engine = RulesEngine()
    # Exceeding limits
    assert "Beyond MSME" in engine.classify_msme(1500000000, 6000000000)

# 2. Startup India 2026 Definitions (G.S.R. 108(E))
def test_startup_india_standard_cap():
    engine = RulesEngine()
    # Standard: age <= 10, turnover <= 200 Cr
    eligible, reason = engine.check_startup_eligibility(5, 500000000, is_deep_tech=False)
    assert eligible is True
    
    # Exceeds 200 Cr
    not_eligible, _ = engine.check_startup_eligibility(5, 2500000000, is_deep_tech=False)
    assert not_eligible is False

def test_startup_india_deep_tech_cap():
    engine = RulesEngine()
    # Deep Tech: age <= 20, turnover <= 300 Cr
    eligible, reason = engine.check_startup_eligibility(15, 2500000000, is_deep_tech=True)
    assert eligible is True
    assert "Deep Tech" in reason

# 3. Statutory Employer & Turnover Ladder Triggers
def test_employer_threshold_triggers():
    engine = RulesEngine()
    ladder_5 = engine.evaluate_employer_ladder(employees=5, turnover_inr=500000)
    assert len(ladder_5) == 1  # 1+ employees only

    ladder_22 = engine.evaluate_employer_ladder(employees=22, turnover_inr=50000000)
    # Triggers: 1+, 10+ (ESI/POSH), 20+ (EPF/Bonus), FSSAI (>12L), GST (>20L/40L), Tax audit (>1Cr)
    bases = [item['basis'] for item in ladder_22]
    assert any("1+ Employees" in b for b in bases)
    assert any("10+ Employees" in b for b in bases)
    assert any("20+ Employees" in b for b in bases)
    assert any("Turnover > ₹12 Lakh" in b for b in bases)

# 4. 8 Languages Multilingual AI Action Cards
def test_ai_advisor_multilingual():
    advisor = AIAdvisor()
    profile = {
        "name": "Test Ventures Ltd",
        "state": "Maharashtra",
        "sector": "Manufacturing",
        "turnover": 30000000,
        "investment": 10000000,
        "employees": 15
    }
    
    for lang in ['en', 'hi', 'mr', 'gu', 'ta', 'te', 'kn', 'bn']:
        plan = advisor.generate_action_plan(profile, lang=lang)
        assert plan['language'] == lang
        assert 'headers' in plan
        assert len(plan['immediate_priorities']) >= 2
        assert len(plan['periodic_deadlines']) >= 4
        assert len(plan['top_incentives']) >= 1
        assert len(plan['action_portals']) >= 4

# 5. Regulatory Database Records Integrity
def test_database_records_count(app):
    with app.app_context():
        cc_count = ComplianceRequirement.query.filter_by(jurisdiction_type='Central').count()
        sc_count = ComplianceRequirement.query.filter(ComplianceRequirement.jurisdiction_type != 'Central').count()
        ci_count = IncentiveScheme.query.filter_by(jurisdiction_type='Central').count()
        si_count = IncentiveScheme.query.filter(IncentiveScheme.jurisdiction_type != 'Central').count()

        assert cc_count == 94
        assert sc_count == 330
        assert ci_count == 78
        assert si_count == 126
        assert (cc_count + sc_count + ci_count + si_count) == 628

# 6. Web Routes & Features
def test_web_routes_accessibility(client):
    routes = [
        '/dashboard',
        '/compliance',
        '/compliance/CC-001',
        '/incentives',
        '/advisor',
        '/tasks',
        '/documents',
        '/consultant',
        '/admin/records',
        '/admin/changes',
        '/admin/dashboard',
        '/admin/companies',
        '/admin/users',
        '/admin/audit',
        '/reports',
        '/reports/export-csv'
    ]
    for r in routes:
        res = client.get(r)
        assert res.status_code in [200, 302], f"Route {r} failed with status {res.status_code}"

def test_language_switch_endpoint(client):
    res = client.get('/set-language/hi', follow_redirects=True)
    assert res.status_code == 200
    with client.session_transaction() as sess:
        assert sess['lang'] == 'hi'

def test_api_chat(client):
    res = client.post('/api/chat', json={"message": "What are my immediate obligations?", "lang": "en"})
    assert res.status_code == 200
    data = res.get_json()
    assert 'action_plan' in data
    assert len(data['action_plan']['immediate_priorities']) > 0

def test_task_toggle_api(client, app):
    with app.app_context():
        company = Company.query.first()
        task = Task(company_id=company.id, title="Test task", status="todo")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    res = client.post(f'/tasks/toggle/{task_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'completed'


def test_admin_dashboard_isolated_controls(client, app):
    # 1. Super Admin access to Admin Dashboard
    with app.app_context():
        admin = User.query.filter_by(role='platform_admin').first()
        if not admin:
            admin = User(name='Platform Admin', email='admin_test@gov.in', role='platform_admin')
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
        admin_id = admin.id

    with client.session_transaction() as sess:
        sess['user_id'] = admin_id
        sess['user_role'] = 'platform_admin'

    # Admin visits /admin/dashboard
    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Must contain ONLY admin controls
    assert "Platform Administration & Governance Dashboard" in html
    assert "Regulatory Records (628)" in html
    assert "Change Intelligence" in html
    assert "Knowledge Ingestion" in html
    assert "Retrieval Playground" in html
    assert "Enterprises Directory" in html
    assert "User Accounts" in html
    assert "System Audit Logs" in html

    # Must NOT contain company controls
    assert "Statutory Thresholds Triggered for Your Scale" not in html
    assert "Immediate Action Priorities" not in html
    assert "Top Government Subsidies to Claim" not in html
    assert "Manage Calendar" not in html
    assert "Edit Profile" not in html

    # Admin accessing /dashboard must be redirected to /admin/dashboard
    res_dash = client.get('/dashboard', follow_redirects=False)
    assert res_dash.status_code == 302
    assert '/admin/dashboard' in res_dash.headers['Location']

    # Admin access to directory, users, audit
    res_comp = client.get('/admin/companies')
    assert res_comp.status_code == 200
    assert "Registered Enterprises Directory" in res_comp.data.decode('utf-8')

    res_users = client.get('/admin/users')
    assert res_users.status_code == 200
    assert "User & Role Governance" in res_users.data.decode('utf-8')

    res_audit = client.get('/admin/audit')
    assert res_audit.status_code == 200
    assert "System Audit & Security Trail" in res_audit.data.decode('utf-8')


def test_company_user_cannot_see_admin_controls(client, app):
    with app.app_context():
        owner = User.query.filter_by(role='owner').first()
        assert owner is not None
        owner_id = owner.id

    with client.session_transaction() as sess:
        sess['user_id'] = owner_id
        sess['user_role'] = 'owner'

    # Non-admin viewing company dashboard
    res = client.get('/dashboard')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Company dashboard contains company controls
    assert "MSME Status" in html or "Core Platform" in html
    assert "Applicable Obligations" in html

    # Company user must NOT see admin controls in sidebar
    assert "/admin/dashboard" not in html
    assert "/admin/knowledge" not in html
    assert "/admin/changes" not in html
    assert "/admin/companies" not in html
    assert "/admin/users" not in html
    assert "/admin/audit" not in html

    # Non-admin attempting to access /admin/dashboard directly must be redirected
    res_forbidden = client.get('/admin/dashboard', follow_redirects=False)
    assert res_forbidden.status_code == 302
    assert '/dashboard' in res_forbidden.headers['Location']

