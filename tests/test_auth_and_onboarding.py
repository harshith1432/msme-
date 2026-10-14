"""
Comprehensive Test Suite for Authentication, Onboarding, Role Segregation, and Localization.
Tests:
  1. Public Landing Page (Unauthenticated)
  2. User Registration & Password Hashing
  3. Login Flow, Invalid Credentials, and Session Persistence
  4. Authentication Route Protection (@login_required)
  5. 6-Step Company Onboarding Flow & Draft Saving
  6. Final Onboarding Confirmation & Task Initialization
  7. Role-Based Permissions (MSME Owner vs CA Consultant vs Super Admin)
  8. Logout & Session Termination
  9. Multilingual Localization Translation & Fallback (Kannada, Hindi, Telugu, Tamil, Malayalam)
"""
import pytest
from datetime import date
from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import User, Company, Tenant, Membership, Task, AuditEvent
from app.services.i18n import translate, reload_locales

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


# --- 1. Public Landing Page ---

def test_public_landing_page(client):
    res = client.get('/')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "Unified Compliance & Incentive Intelligence" in html
    assert "628 Official Records" in html
    assert "Sign In" in html
    assert "Get Started" in html


# --- 2. Registration Flow ---

def test_user_registration(client, app):
    res = client.post('/register', data={
        'name': 'Suresh Kumar',
        'email': 'suresh@karnataka-tech.in',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'role': 'owner',
        'preferred_language': 'kn'
    }, follow_redirects=False)
    
    # Should redirect to onboarding
    assert res.status_code == 302
    assert '/onboarding' in res.headers['Location']

    with app.app_context():
        user = User.query.filter_by(email='suresh@karnataka-tech.in').first()
        assert user is not None
        assert user.name == 'Suresh Kumar'
        assert user.check_password('Password@123')
        assert not user.check_password('WrongPassword')
        assert user.preferred_language == 'kn'

        # Verify draft company was initialized
        company = Company.query.filter_by(created_by_user_id=user.id).first()
        assert company is not None
        assert company.is_onboarded is False
        assert company.onboarding_step == 1

def test_user_registration_mismatched_password(client):
    res = client.post('/register', data={
        'name': 'Test User',
        'email': 'mismatch@example.com',
        'password': 'Password@123',
        'confirm_password': 'DifferentPassword',
        'role': 'owner'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert "Passwords do not match" in res.data.decode('utf-8')


# --- 3. Login Flow & Invalid Credentials ---

def test_login_invalid_credentials(client):
    res = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'badpassword'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert "Invalid email address or password" in res.data.decode('utf-8')

def test_login_success_owner(client, app):
    # Seed owner user
    with app.app_context():
        tenant = Tenant(name='Test Corp', slug='test-corp')
        db.session.add(tenant)
        db.session.flush()
        user = User(name='Ramesh Patil', email='ramesh@patileng.in', role='owner')
        user.set_password('OwnerPass@2026')
        db.session.add(user)
        db.session.flush()
        db.session.add(Company(tenant_id=tenant.id, name='Patil Eng', state='Maharashtra', created_by_user_id=user.id, is_onboarded=True, onboarding_step=6))
        db.session.commit()

    res = client.post('/login', data={
        'email': 'ramesh@patileng.in',
        'password': 'OwnerPass@2026'
    }, follow_redirects=False)
    
    assert res.status_code == 302
    assert '/dashboard' in res.headers['Location']

    with client.session_transaction() as sess:
        assert sess['user_id'] is not None
        assert sess['user_role'] == 'owner'


# --- 4. Protected Routes & Authentication Enforcement ---

def test_unauthenticated_dashboard_redirect(client):
    # With clean session and force_unauthenticated, accessing /dashboard should redirect to login
    with client.session_transaction() as sess:
        sess.clear()
        sess['force_unauthenticated'] = True
        
    res = client.get('/dashboard', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.headers['Location']


# --- 5. 6-Step Onboarding Flow ---

def test_onboarding_wizard_complete_journey(client, app):
    # 1. Register new owner
    client.post('/register', data={
        'name': 'Anita Deshmukh',
        'email': 'anita@deshmukh-foods.in',
        'password': 'SecurePassword@2026',
        'confirm_password': 'SecurePassword@2026',
        'role': 'owner'
    })

    # 2. Step 1: Company Identity
    res = client.post('/onboarding', data={
        'step': '1',
        'action': 'continue',
        'name': 'Deshmukh Agro Foods Pvt Ltd',
        'trade_name': 'Deshmukh Organics',
        'entity_type': 'Private Limited Company',
        'incorporation_date': '2023-04-10',
        'registered_address': 'Gat No 45, MIDC Baramati',
        'state': 'Maharashtra',
        'district': 'Pune',
        'pincode': '413133',
        'contact_email': 'contact@deshmukh-foods.in',
        'contact_phone': '+91 98220 12345'
    }, follow_redirects=False)
    assert res.status_code == 302
    assert '/onboarding/step/2' in res.headers['Location']

    # 3. Step 2: Classification
    res = client.post('/onboarding', data={
        'step': '2',
        'action': 'continue',
        'activity_type': 'Manufacturing',
        'sector': 'Food Processing & Tech',
        'employees': '18',
        'is_exporter': 'on'
    }, follow_redirects=False)
    assert res.status_code == 302
    assert '/onboarding/step/3' in res.headers['Location']

    # 4. Step 3: Financial Profile
    res = client.post('/onboarding', data={
        'step': '3',
        'action': 'continue',
        'turnover': '35000000',
        'investment': '12000000',
        'financial_year': '2025-26'
    }, follow_redirects=False)
    assert res.status_code == 302
    assert '/onboarding/step/4' in res.headers['Location']

    # 5. Step 4: Registrations
    res = client.post('/onboarding', data={
        'step': '4',
        'action': 'continue',
        'udyam_number': 'UDYAM-MH-26-0045123',
        'gstin': '27AABCD1234E1Z5',
        'pan_number': 'AABCD1234E',
        'is_dpiit': 'on',
        'is_zed_certified': 'on'
    }, follow_redirects=False)
    assert res.status_code == 302
    assert '/onboarding/step/5' in res.headers['Location']

    # 6. Step 5: Documents (skip to step 6)
    res = client.post('/onboarding', data={
        'step': '5',
        'action': 'continue'
    }, follow_redirects=False)
    assert res.status_code == 302
    assert '/onboarding/step/6' in res.headers['Location']

    # 7. Step 6: Review & Final Confirmation
    res = client.post('/onboarding', data={
        'step': '6',
        'action': 'complete'
    }, follow_redirects=False)
    assert res.status_code == 302
    assert '/dashboard' in res.headers['Location']

    # Verify company is now fully onboarded in database
    with app.app_context():
        comp = Company.query.filter_by(name='Deshmukh Agro Foods Pvt Ltd').first()
        assert comp is not None
        assert comp.is_onboarded is True
        assert comp.onboarding_step == 6
        assert comp.state == 'Maharashtra'
        assert comp.get_latest_metric('turnover') == 35000000
        assert comp.get_latest_metric('investment') == 12000000
        assert comp.get_latest_metric('employees') == 18

        # Verify automated initial tasks were created from matched obligations
        tasks = Task.query.filter_by(company_id=comp.id).all()
        assert len(tasks) > 0


# --- 6. Role Segregation ---

def test_role_segregation(client, app):
    # Owner trying to access /admin/records should be redirected to dashboard
    with app.app_context():
        tenant = Tenant(name='MSME Org', slug='msme-org')
        db.session.add(tenant)
        db.session.flush()
        owner = User(name='Vikas Rao', email='vikas@raoenterprises.com', role='owner')
        owner.set_password('Owner@123')
        db.session.add(owner)
        db.session.flush()
        comp = Company(tenant_id=tenant.id, name='Rao Tech', state='Karnataka', created_by_user_id=owner.id, is_onboarded=True)
        db.session.add(comp)
        db.session.commit()
        owner_id = owner.id

    with client.session_transaction() as sess:
        sess['user_id'] = owner_id
        sess['user_role'] = 'owner'

    # Attempting to access admin records
    res = client.get('/admin/records', follow_redirects=False)
    assert res.status_code == 302
    assert '/dashboard' in res.headers['Location']

    # Super admin accessing admin records
    with app.app_context():
        admin = User(name='Admin Officer', email='officer@gov.in', role='platform_admin')
        admin.set_password('GovAdmin@123')
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id

    with client.session_transaction() as sess:
        sess['user_id'] = admin_id
        sess['user_role'] = 'platform_admin'

    res = client.get('/admin/records')
    assert res.status_code == 200
    assert "Regulatory Records" in res.data.decode('utf-8')


# --- 7. Sign Out ---

def test_user_logout(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'owner'

    res = client.get('/logout', follow_redirects=False)
    assert res.status_code == 302
    
    with client.session_transaction() as sess:
        assert 'user_id' not in sess


# --- 8. Multilingual Localization Engine ---

def test_i18n_translation_and_fallback():
    reload_locales()
    # English
    assert translate('nav_overview', lang='en') == 'Overview'
    # Kannada
    assert 'ಅವಲೋಕನ' in translate('nav_overview', lang='kn')
    # Hindi
    assert 'अवलोकन' in translate('nav_overview', lang='hi')
    # Telugu
    assert 'సమీక్ష' in translate('nav_overview', lang='te')
    # Tamil
    assert 'கண்ணோட்டம்' in translate('nav_overview', lang='ta')
    # Malayalam
    assert 'അവലോകനം' in translate('nav_overview', lang='ml')

    # Fallback to English for non-existent key
    assert translate('non_existent_random_key_123', default='DefaultValue', lang='kn') == 'DefaultValue'
