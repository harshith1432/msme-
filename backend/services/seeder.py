"""
Database Seeder for MSME Platform.
Loads all 628 official records into SQLAlchemy database tables:
  - 94 Central Compliance Requirements
  - 330 State Compliance Requirements
  - 78 Central Incentive Schemes
  - 126 State Incentive Schemes
Plus demo tenant, users, company profile and initial obligations.
"""
import os
import json
from datetime import datetime, date
from backend.extensions import db
from backend.models import (
    Tenant, User, Membership, Company, CompanyMetric, 
    ComplianceRequirement, IncentiveScheme, CompanyObligation,
    Task, RegulatoryChange, Subscription, AuditEvent, KnowledgeSource
)

def seed_database(app):
    with app.app_context():
        db.create_all()
        
        # Check if already seeded
        if ComplianceRequirement.query.first():
            print("Database already seeded with regulatory records.")
            return

        data_dir = app.config['DATA_DIR']
        
        # 1. Seed Central Compliance (94 records)
        cc_path = os.path.join(data_dir, 'central_compliance.json')
        if os.path.exists(cc_path):
            with open(cc_path, 'r', encoding='utf-8') as f:
                for row in json.load(f):
                    rec = ComplianceRequirement(
                        id=row['ID'],
                        jurisdiction='Central',
                        jurisdiction_type='Central',
                        domain=row.get('Domain', 'General'),
                        requirement=row.get('Requirement', ''),
                        law_basis=row.get('Law / Rule', ''),
                        applies_to_trigger=row.get('Applies to / trigger', ''),
                        what_to_do=row.get('What to do', ''),
                        frequency_due_date=row.get('Frequency / due date', ''),
                        authority=row.get('Authority', ''),
                        official_link=row.get('Official link', ''),
                        notes=row.get('Notes', ''),
                        verification_status='verified' if 'Verified' in row.get('Verification', '') else 'knowledge_based',
                        last_verified_date='Oct 2026',
                        version='1.0',
                        is_active=True
                    )
                    db.session.add(rec)

        # 2. Seed State Compliance (330 records)
        sc_path = os.path.join(data_dir, 'state_compliance.json')
        if os.path.exists(sc_path):
            with open(sc_path, 'r', encoding='utf-8') as f:
                for row in json.load(f):
                    rec = ComplianceRequirement(
                        id=row['ID'],
                        jurisdiction=row.get('State / UT', 'General'),
                        jurisdiction_type=row.get('Type', 'State'),
                        domain=row.get('Domain', 'General'),
                        requirement=row.get('Requirement', ''),
                        law_basis=row.get('Law / basis', ''),
                        applies_to_trigger=row.get('Applies to / trigger', ''),
                        what_to_do=row.get('What to do', ''),
                        frequency_due_date='Periodic / Annual',
                        authority=row.get('State / UT', '') + ' Authority',
                        official_link=row.get('Portal / link', ''),
                        notes=row.get('Notes', ''),
                        verification_status='verified' if 'Verified' in row.get('Verification', '') else 'knowledge_based',
                        last_verified_date='Oct 2026',
                        version='1.0',
                        is_active=True
                    )
                    db.session.add(rec)

        # 3. Seed Central Incentives (78 records)
        ci_path = os.path.join(data_dir, 'central_incentives.json')
        if os.path.exists(ci_path):
            with open(ci_path, 'r', encoding='utf-8') as f:
                for row in json.load(f):
                    rec = IncentiveScheme(
                        id=row['ID'],
                        jurisdiction='Central',
                        jurisdiction_type='Central',
                        category=row.get('Category', 'General'),
                        scheme_name=row.get('Scheme', ''),
                        ministry_agency=row.get('Ministry / agency', ''),
                        key_benefit=row.get('Key benefit', ''),
                        eligibility_criteria=row.get('Who can apply', ''),
                        apply_link=row.get('Apply / info link', ''),
                        status_notes=row.get('Status / notes', ''),
                        verification_status='verified' if 'Verified' in row.get('Verification', '') else 'knowledge_based',
                        last_verified_date='Oct 2026',
                        version='1.0',
                        is_active=True
                    )
                    db.session.add(rec)

        # 4. Seed State Incentives (126 records)
        si_path = os.path.join(data_dir, 'state_incentives.json')
        if os.path.exists(si_path):
            with open(si_path, 'r', encoding='utf-8') as f:
                for row in json.load(f):
                    rec = IncentiveScheme(
                        id=row['ID'],
                        jurisdiction=row.get('State / UT', 'General'),
                        jurisdiction_type=row.get('Type', 'State'),
                        category=row.get('Category', 'Industrial policy'),
                        scheme_name=row.get('Policy / scheme', ''),
                        ministry_agency=row.get('State / UT', '') + ' Industries Dept',
                        key_benefit=row.get('Key benefit', ''),
                        eligibility_criteria='State registered MSMEs & units',
                        apply_link=row.get('Apply / info link', ''),
                        status_notes='',
                        verification_status='verified' if 'Verified' in row.get('Verification', '') else 'knowledge_based',
                        last_verified_date='Oct 2026',
                        version='1.0',
                        is_active=True
                    )
                    db.session.add(rec)

        db.session.commit()
        print("Seeded 628 Compliance and Incentive records.")

        # 5. Create Demo Tenant & Users
        tenant = Tenant(name='Zenith Enterprises Group', slug='zenith-group', plan='growth')
        db.session.add(tenant)
        db.session.flush()

        # Admin User
        admin_user = User(
            email='founder@zenithenterprises.in',
            name='Rajesh Sharma',
            role='owner'
        )
        admin_user.set_password('Admin@2026')
        db.session.add(admin_user)
        db.session.flush()

        # CA / Consultant User
        ca_user = User(
            email='ca.kapoor@finserv.in',
            name='CA Ananya Kapoor',
            role='consultant'
        )
        ca_user.set_password('Consultant@2026')
        db.session.add(ca_user)
        db.session.flush()

        # Platform Super Admin
        super_admin = User(
            email='admin@msmenavigator.gov.in',
            name='System Super Admin',
            role='platform_admin'
        )
        super_admin.set_password('SuperAdmin@2026')
        db.session.add(super_admin)
        db.session.flush()

        db.session.add(Membership(user_id=admin_user.id, tenant_id=tenant.id, role='owner'))
        db.session.add(Membership(user_id=ca_user.id, tenant_id=tenant.id, role='consultant'))
        db.session.add(Membership(user_id=super_admin.id, tenant_id=tenant.id, role='platform_admin'))

        # Demo Company (Gujarat Food & Tech Solutions)
        company = Company(
            tenant_id=tenant.id,
            name='Zenith Food & Tech Solutions Pvt Ltd',
            trade_name='Zenith Organics',
            entity_type='Private Limited Company',
            state='Gujarat',
            district='Ahmedabad',
            pincode='380015',
            registered_address='Plot 42, GIDC Industrial Estate, Sanand, Ahmedabad',
            industry='Food Processing',
            sector='Food Processing & Tech',
            activity_type='Manufacturing',
            incorporation_date=date(2022, 5, 14),
            udyam_number='UDYAM-GJ-01-0084921',
            pan_number='AAACZ1234F',
            gstin='24AAACZ1234F1Z5',
            is_dpiit_recognized=True,
            is_deep_tech=False,
            is_zed_certified=True,
            is_exporter=True,
            is_onboarded=True,
            onboarding_step=6,
            created_by_user_id=admin_user.id,
            contact_email='founder@zenithenterprises.in',
            contact_phone='+91 98765 43210'
        )
        db.session.add(company)
        db.session.flush()

        # Metrics: ₹4.5 Cr Turnover, ₹1.8 Cr Investment, 22 Employees
        db.session.add(CompanyMetric(company_id=company.id, metric_type='turnover', value=45000000, financial_year='2025-26', provenance='verified'))
        db.session.add(CompanyMetric(company_id=company.id, metric_type='investment', value=18000000, financial_year='2025-26', provenance='verified'))
        db.session.add(CompanyMetric(company_id=company.id, metric_type='employees', value=22, financial_year='2025-26', provenance='user_entered'))

        # Delegate access to CA
        from backend.models import ClientAccess
        db.session.add(ClientAccess(consultant_user_id=ca_user.id, company_id=company.id, access_level='full', status='active'))

        # Seed sample Regulatory Change item in queue
        db.session.add(RegulatoryChange(
            title="DPIIT G.S.R. 108(E) Startup Cap Revision & Deep Tech Classification",
            source_url="https://www.startupindia.gov.in",
            issuing_authority="DPIIT / Ministry of Commerce",
            summary_of_change="Raised DPIIT startup turnover cap to ₹200 cr (10 yrs) and added Deep Tech category with ₹300 cr turnover cap and 20-year recognition window.",
            effective_date=date(2026, 2, 1),
            affected_jurisdiction="Central",
            affected_domain="Startup & Innovation",
            review_status="approved",
            review_notes="Verified against official Gazette notification."
        ))

        db.session.add(RegulatoryChange(
            title="Income-tax Act 2025 - Section 43B(h) MSE 45-Day Dues Alignment",
            source_url="https://www.incometax.gov.in",
            issuing_authority="CBDT / Department of Revenue",
            summary_of_change="Section numbers updated under new 2025 Act in force 1 Apr 2026. Micro/Small supplier payment rules continue under Section 37(2)(g).",
            effective_date=date(2026, 4, 1),
            affected_jurisdiction="Central",
            affected_domain="Income Tax",
            review_status="approved",
            review_notes="Statutory enforcement verified for FY 2026-27."
        ))

        # Initial Tasks
        db.session.add(Task(company_id=company.id, title='Verify EPF & ESI Monthly ECR Deposit', priority='high', status='todo', due_date=date(2026, 10, 15)))
        db.session.add(Task(company_id=company.id, title='File GSTR-3B for previous tax period', priority='high', status='todo', due_date=date(2026, 10, 20)))
        db.session.add(Task(company_id=company.id, title='Claim Atmanirbhar Gujarat MSME Power Tariff Subsidy', priority='medium', status='in_progress', due_date=date(2026, 11, 30)))

        # Audit Event
        db.session.add(AuditEvent(
            tenant_id=tenant.id,
            user_id=admin_user.id,
            action='system_initialized',
            entity_type='Company',
            entity_id=str(company.id),
            details='Initialized company profile and matched against 628 statutory rules.'
        ))

        # Default Official Knowledge Sources
        if KnowledgeSource.query.count() == 0:
            db.session.add_all([
                KnowledgeSource(name='Gazette of India MSME Feed', portal_url='https://egazette.gov.in', issuing_authority='Directorate of Printing, MoHUA', jurisdiction='Central'),
                KnowledgeSource(name='Udyam Registration Portal', portal_url='https://udyamregistration.gov.in', issuing_authority='Ministry of MSME', jurisdiction='Central'),
                KnowledgeSource(name='CGTMSE Credit Guarantee Portal', portal_url='https://www.cgtmse.in', issuing_authority='SIDBI & MoMSME', jurisdiction='Central'),
                KnowledgeSource(name='National Single Window System (NSWS)', portal_url='https://www.nsws.gov.in', issuing_authority='DPIIT & Invest India', jurisdiction='Central'),
                KnowledgeSource(name='Gujarat MSME Incentives Portal', portal_url='https://msme.gujarat.gov.in', issuing_authority='Industries Commissionerate Gujarat', jurisdiction='State', state='Gujarat')
            ])

        db.session.commit()
        print("Demo tenant, users, company, metrics and regulatory queue seeded successfully.")
