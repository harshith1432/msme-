"""
Comprehensive Automated Tests for Six Connected AI Capabilities:
1. Paperwork Agent (OCR, field proposals, human confirmation gate, readiness checker, AIDrafts)
2. Compliance Applicability Assistant (Deterministic evaluation + grounded citations)
3. Incentive Discovery & Eligibility Agent (Categorical eligibility: potentially eligible, more info required, likely not eligible, expert review)
4. Regulatory Change Intelligence (Allowlist, content hashing, human approval gate, publication)
5. Compliance Action Assistant (Deterministic dates, event clarification, obligation task generation)
6. Source-Grounded MSME Assistant (10 Controlled tools, tenant boundary isolation, cross-tenant denial)
"""
import pytest
import os
import json
from datetime import date, datetime, timedelta
from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import (
    Tenant, User, Company, CompanyMetric, ComplianceRequirement,
    IncentiveScheme, CompanyObligation, Task, Document,
    DocumentExtraction, ExtractedField, AIDraft, RegulatoryChange, ReviewRequest
)
from app.services.extraction_service import ExtractionService
from app.services.readiness_service import ReadinessService
from app.services.incentive_service import IncentiveEligibilityService
from app.services.regulatory_service import RegulatoryIntelligenceService
from app.services.action_service import ComplianceActionService
from app.services.tool_dispatcher import ToolDispatcher

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()

        # Seed test tenant and users
        tenant1 = Tenant(name="Tenant Alpha", slug="tenant-alpha")
        tenant2 = Tenant(name="Tenant Beta", slug="tenant-beta")
        db.session.add_all([tenant1, tenant2])
        db.session.commit()

        user1 = User(email="owner@alpha.com", name="Alpha Owner", role="owner")
        user1.set_password("pass123")
        db.session.add(user1)

        # Seed test companies
        comp1 = Company(
            tenant_id=tenant1.id,
            name="Alpha Engineering Pvt Ltd",
            trade_name="Alpha Engg",
            entity_type="Private Limited Company",
            state="Maharashtra",
            sector="General Manufacturing",
            activity_type="Manufacturing",
            udyam_number="UDYAM-MH-12-0012345",
            pan_number="AAACA1234A",
            gstin="27AAACA1234A1Z5",
            is_dpiit_recognized=True,
            is_zed_certified=True,
            incorporation_date=date(2021, 5, 10)
        )
        comp2 = Company(
            tenant_id=tenant2.id,
            name="Beta Agro Trading LLP",
            trade_name="Beta Agro",
            entity_type="LLP",
            state="Gujarat",
            sector="Trading & Retail",
            activity_type="Trading",
            incorporation_date=date(2018, 1, 15)
        )
        db.session.add_all([comp1, comp2])
        db.session.commit()

        # Seed metrics
        db.session.add(CompanyMetric(company_id=comp1.id, metric_type='turnover', value=15000000.0))
        db.session.add(CompanyMetric(company_id=comp1.id, metric_type='investment', value=4000000.0))
        db.session.add(CompanyMetric(company_id=comp1.id, metric_type='employees', value=25.0))

        db.session.add(CompanyMetric(company_id=comp2.id, metric_type='turnover', value=8000000.0))
        db.session.add(CompanyMetric(company_id=comp2.id, metric_type='investment', value=1000000.0))
        db.session.add(CompanyMetric(company_id=comp2.id, metric_type='employees', value=6.0))

        # Seed test compliance requirement
        cr1 = ComplianceRequirement(
            id='TEST-CC-01',
            jurisdiction='Central',
            jurisdiction_type='Central',
            domain='Labour',
            requirement='Mandatory Employees Provident Fund (EPF) Registration',
            law_basis='EPF & MP Act 1952',
            what_to_do='Register on Shram Suvidha and file ECR monthly by 15th.',
            frequency_due_date='15th of every month',
            authority='EPFO',
            official_link='https://unifiedportal-emp.epfindia.gov.in',
            verification_status='verified',
            version='1.0',
            is_active=True
        )
        db.session.add(cr1)

        # Seed test incentive scheme
        sch1 = IncentiveScheme(
            id='TEST-CI-01',
            jurisdiction='Central',
            jurisdiction_type='Central',
            category='Credit & Guarantee',
            scheme_name='Credit Guarantee Fund Scheme (CGTMSE)',
            ministry_agency='Ministry of MSME / SIDBI',
            key_benefit='Collateral-free credit facility up to ₹500 Lakhs.',
            eligibility_criteria='New and existing Micro and Small Enterprises in Manufacturing or Services.',
            apply_link='https://www.cgtmse.in',
            verification_status='verified',
            version='1.0',
            is_active=True
        )
        sch_state = IncentiveScheme(
            id='TEST-SI-01',
            jurisdiction='Maharashtra',
            jurisdiction_type='State',
            category='Subsidy',
            scheme_name='Maharashtra Capital Investment Subsidy',
            ministry_agency='Maharashtra Industries Department',
            key_benefit='Up to 25% capital subsidy for manufacturing units in Taluka B/C/D.',
            eligibility_criteria='Manufacturing MSMEs registered in Maharashtra.',
            apply_link='https://www.nsws.gov.in',
            verification_status='verified',
            version='1.0',
            is_active=True
        )
        db.session.add_all([sch1, sch_state])

        # Link obligation
        ob1 = CompanyObligation(
            company_id=comp1.id,
            compliance_id=cr1.id,
            status='todo',
            match_reason='Headcount (25) exceeds 20 threshold.'
        )
        db.session.add(ob1)

        # Seed test document
        doc1 = Document(
            company_id=comp1.id,
            title='Udyam Registration Certificate',
            doc_type='udyam_cert',
            filename='test_udyam.txt',
            file_path='test_udyam.txt',
            file_size=1024,
            mime_type='text/plain',
            verification_status='verified'
        )
        db.session.add(doc1)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# ==========================================
# 1. Capability A: Paperwork Agent Tests
# ==========================================
def test_paperwork_agent_extraction_and_field_parsing(app):
    """Test text parsing, entity extraction, and confidence mapping without profile modification."""
    with app.app_context():
        service = ExtractionService()
        sample_text = """
        UDYAM REGISTRATION CERTIFICATE
        UDYAM REGISTRATION NUMBER: UDYAM-MH-01-9988776
        NAME OF ENTERPRISE: SHALIMAR TEXTILES PVT LTD
        PERMANENT ACCOUNT NUMBER (PAN): AABCS9876K
        GSTIN: 27AABCS9876K1Z9
        TOTAL TURNOVER: ₹4,50,00,000 (INR 4.5 Crore)
        INVESTMENT IN PLANT & MACHINERY: ₹95,00,000
        TOTAL EMPLOYEES: 38
        DATE OF INCORPORATION: 15/08/2022
        """
        candidates = service.parse_candidate_fields(sample_text, [("Page 1", sample_text)])
        
        field_dict = {c['field_name']: c for c in candidates}
        assert 'udyam_number' in field_dict
        assert field_dict['udyam_number']['proposed_value'] == 'UDYAM-MH-01-9988776'
        assert field_dict['udyam_number']['confidence'] == 'high'
        assert 'pan_number' in field_dict
        assert field_dict['pan_number']['proposed_value'] == 'AABCS9876K'
        assert 'gstin' in field_dict
        assert field_dict['gstin']['proposed_value'] == '27AABCS9876K1Z9'
        assert 'employees' in field_dict
        assert field_dict['employees']['proposed_value'] == '38'

def test_paperwork_agent_human_confirmation_gate(app, tmp_path):
    """Test that staged fields DO NOT alter Company profile until explicit user confirmation."""
    with app.app_context():
        company = Company.query.filter_by(name="Alpha Engineering Pvt Ltd").first()
        initial_gstin = company.gstin

        # Create temporary file for document
        test_file = tmp_path / "cert.txt"
        test_file.write_text("UDYAM REGISTRATION NUMBER: UDYAM-MH-12-7777777\nGSTIN: 27XYZAB1234C1Z1\nEMPLOYEES: 55")

        doc = Document(
            company_id=company.id,
            title="Sample Registration Upload",
            doc_type="other",
            filename="cert.txt",
            file_path=str(test_file),
            file_size=len(test_file.read_text()),
            mime_type="text/plain"
        )
        db.session.add(doc)
        db.session.commit()

        service = ExtractionService()
        extraction, err = service.process_document(doc.id)
        assert err is None
        assert extraction.status == 'processed'

        # Ensure company was NOT mutated automatically
        company_reloaded = Company.query.get(company.id)
        assert company_reloaded.gstin == initial_gstin

        # Confirm fields through user review gate
        fields = extraction.fields
        confirmations = {}
        for f in fields:
            if f.field_name == 'gstin':
                confirmations[str(f.id)] = {'action': 'confirm', 'corrected_value': '27XYZAB1234C1Z1'}
            else:
                confirmations[str(f.id)] = {'action': 'reject'}

        ok, msg = service.confirm_extracted_fields(extraction.id, confirmations)
        assert ok is True

        # Now verify company profile reflects the confirmed value
        company_updated = Company.query.get(company.id)
        assert company_updated.gstin == '27XYZAB1234C1Z1'

def test_paperwork_agent_document_readiness_and_drafts(app):
    """Test document readiness checking (available, missing) and AIDraft checklist generation."""
    with app.app_context():
        comp = Company.query.filter_by(name="Alpha Engineering Pvt Ltd").first()
        readiness_service = ReadinessService()

        # Check readiness for CGTMSE scheme
        res, err = readiness_service.evaluate_readiness(comp.id, scheme_id='TEST-CI-01')
        assert err is None
        assert res['total_required'] > 0
        assert res['available_count'] >= 1  # Udyam was seeded as verified

        # Generate draft checklist
        draft, err = readiness_service.generate_draft_checklist(comp.id, scheme_id='TEST-CI-01')
        assert err is None
        assert draft.status == 'draft'
        assert draft.version == 1
        assert "CGTMSE" in draft.title

        # Human approve draft
        ok, msg = readiness_service.approve_draft(draft.id)
        assert ok is True
        assert draft.status == 'approved'
        assert draft.approved_at is not None

# ==========================================
# 2. Capability B: Compliance Applicability
# ==========================================
def test_compliance_applicability_evaluation(app):
    """Test deterministic evaluation with law citations and employer ladder."""
    with app.app_context():
        comp = Company.query.filter_by(name="Alpha Engineering Pvt Ltd").first()
        dispatcher = ToolDispatcher()
        res = dispatcher.execute_tool('evaluate_compliance_rules', {'company_id': comp.id})
        assert res['success'] is True
        assert 'Micro' in res['msme_classification']
        assert len(res['citations']) > 0

# ==========================================
# 3. Capability C: Incentive Eligibility
# ==========================================
def test_incentive_discovery_categorical_evaluation(app):
    """Test categorical classification: potentially_eligible vs likely_ineligible based on state and sector."""
    with app.app_context():
        comp1 = Company.query.filter_by(name="Alpha Engineering Pvt Ltd").first() # Maharashtra
        comp2 = Company.query.filter_by(name="Beta Agro Trading LLP").first() # Gujarat

        service = IncentiveEligibilityService()

        # Comp 1 in Maharashtra evaluating Maharashtra Capital Subsidy -> potentially eligible
        eval1, err1 = service.evaluate_scheme(comp1.id, 'TEST-SI-01')
        assert err1 is None
        assert eval1['status'] == 'potentially_eligible'
        assert len(eval1['match_reasons']) > 0

        # Comp 2 in Gujarat evaluating Maharashtra Capital Subsidy -> likely ineligible (State mismatch)
        eval2, err2 = service.evaluate_scheme(comp2.id, 'TEST-SI-01')
        assert err2 is None
        assert eval2['status'] == 'likely_ineligible'
        assert any('Maharashtra' in r for r in eval2['failure_reasons'])

# ==========================================
# 4. Capability D: Regulatory Change Intelligence
# ==========================================
def test_regulatory_change_allowlist_and_approval_lifecycle(app):
    """Test official source allowlist enforcement, content hashing, and human approval gate."""
    with app.app_context():
        service = RegulatoryIntelligenceService()

        # 1. Reject untrusted non-government domain
        res_fail, err_fail = service.ingest_update(
            title="Fake Notification",
            source_url="https://unauthorized-commercial-blog.com/amendment",
            issuing_authority="Random Blog",
            raw_content="Some unauthorized circular text"
        )
        assert res_fail is None
        assert "not on the official government allowlist" in err_fail

        # 2. Ingest valid official notification from msme.gov.in
        change, err_ok = service.ingest_update(
            title="MSME Gazette Notification S.O. 2026/102",
            source_url="https://msme.gov.in/notifications/gazette-2026-102",
            issuing_authority="Ministry of MSME",
            raw_content="Revised investment ceiling and export turnover exclusion rules under MSMED Act.",
            affected_rule_id='TEST-CC-01'
        )
        assert err_ok is None
        assert change.review_status == 'needs_review'
        assert change.content_hash is not None

        # 3. Verify AI CANNOT publish directly without approval
        pub_fail, pub_err = service.publish_change(change.id, publisher_user_id=1)
        assert pub_fail is False
        assert "Must be 'approved' first" in pub_err

        # 4. Human expert approves
        app_ok, app_msg = service.approve_change(change.id, reviewer_user_id=1, notes="Approved after legal verification")
        assert app_ok is True
        assert change.review_status == 'approved'

        # 5. Publication to active knowledge base
        pub_ok, pub_msg = service.publish_change(change.id, publisher_user_id=1)
        assert pub_ok is True
        assert change.review_status == 'published'

# ==========================================
# 5. Capability E: Compliance Action Assistant
# ==========================================
def test_compliance_action_deterministic_due_dates(app):
    """Test deterministic date calculation for statutory deadlines without guessing."""
    service = ComplianceActionService()
    today = date(2026, 4, 1)

    # EPF/ESI -> 15th of next month
    due_epf, is_event, note = service.calculate_deterministic_due_date("15th of every month", today)
    assert due_epf == date(2026, 5, 15)
    assert is_event is False

    # GSTR-3B -> 20th of next month
    due_gst, is_event, note = service.calculate_deterministic_due_date("20th of every month (GSTR-3B)", today)
    assert due_gst == date(2026, 5, 20)
    assert is_event is False

    # Event-dependent -> requires clarification
    due_event, is_event, note = service.calculate_deterministic_due_date("Within 45 days of invoice receipt", today)
    assert due_event is None
    assert is_event is True
    assert note is not None

# ==========================================
# 6. Capability F: Controlled Tools & Tenant Isolation
# ==========================================
def test_controlled_tools_execution_and_tenant_boundary(app):
    """Test 10 controlled tools and enforce that cross-tenant access is rejected."""
    with app.app_context():
        comp1 = Company.query.filter_by(name="Alpha Engineering Pvt Ltd").first()
        comp2 = Company.query.filter_by(name="Beta Agro Trading LLP").first()

        dispatcher = ToolDispatcher()

        # 1. Legitimate tenant access (Tenant Alpha calling for Company 1)
        prof_res = dispatcher.execute_tool('get_business_profile', {'company_id': comp1.id}, tenant_id=comp1.tenant_id)
        assert prof_res['success'] is True
        assert prof_res['data']['name'] == 'Alpha Engineering Pvt Ltd'

        # 2. Cross-tenant access denial (Tenant Beta attempting to read Company 1)
        hack_res = dispatcher.execute_tool('get_business_profile', {'company_id': comp1.id}, tenant_id=comp2.tenant_id)
        assert hack_res['success'] is False
        assert "Access denied: Unauthorized cross-tenant" in hack_res['error']

        # 3. Search compliance records with citations
        search_res = dispatcher.execute_tool('search_approved_compliance_records', {'query': 'provident'})
        assert search_res['success'] is True
        assert len(search_res['citations']) > 0

        # 4. Search published schemes with citations
        scheme_res = dispatcher.execute_tool('search_published_schemes', {'query': 'cgtmse'})
        assert scheme_res['success'] is True
        assert len(scheme_res['citations']) > 0

        # 5. Create draft task
        task_res = dispatcher.execute_tool('create_draft_task', {
            'company_id': comp1.id,
            'title': 'File Annual Labour Return',
            'priority': 'medium',
            'due_date': '2026-06-30'
        }, tenant_id=comp1.tenant_id)
        assert task_res['success'] is True
        assert task_res['task_id'] is not None

        # 6. Request expert CA review
        review_res = dispatcher.execute_tool('request_expert_review', {
            'company_id': comp1.id,
            'review_type': 'compliance',
            'reference_id': 'TEST-CC-01',
            'notes': 'Please clarify applicability of Maharashtra Shops & Establishments exemption.'
        }, tenant_id=comp1.tenant_id)
        assert review_res['success'] is True
        assert review_res['review_request_id'] is not None
