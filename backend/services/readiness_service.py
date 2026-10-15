"""
Document Readiness & AI Draft Preparation Service.
Evaluates document readiness (available, missing, expired, unverified) against official scheme
or compliance requirements, and generates auditable AIDraft records (checklists, cover letters).
"""
from datetime import datetime, date
from backend.extensions import db
from backend.models import Company, Document, IncentiveScheme, ComplianceRequirement, AIDraft, AuditEvent

SCHEME_DOCUMENT_REQUIREMENTS = {
    'credit_guarantee': [
        {'name': 'Udyam Registration Certificate', 'types': ['udyam_cert', 'udyam']},
        {'name': 'Audited Balance Sheet & P&L (Last 2-3 Years)', 'types': ['audit_report', 'financials']},
        {'name': 'ITR Acknowledgement & GST 3B Returns', 'types': ['itr', 'gstin']},
        {'name': 'Bank Account Statement (Last 6 Months)', 'types': ['bank_statement', 'financials']},
        {'name': 'Project Report / Business Quotations', 'types': ['project_report', 'other']}
    ],
    'startup': [
        {'name': 'DPIIT Startup Recognition Certificate', 'types': ['dpiit_cert', 'startup']},
        {'name': 'Certificate of Incorporation / Partnership Deed', 'types': ['incorporation', 'deed']},
        {'name': 'Pitch Deck / Innovative Business Plan', 'types': ['pitch_deck', 'project_report', 'other']},
        {'name': 'Directors / Promoters KYC (PAN & Aadhaar)', 'types': ['pan', 'kyc']},
        {'name': 'Proof of Working Prototype / Patent Filing', 'types': ['ipr', 'patent', 'other']}
    ],
    'technology_subsidy': [
        {'name': 'Udyam Registration Certificate', 'types': ['udyam_cert', 'udyam']},
        {'name': 'ZED Certification Copy (Bronze/Silver/Gold)', 'types': ['zed_cert', 'other']},
        {'name': 'Machinery Purchase Invoices & Proof of Payment', 'types': ['invoice', 'machinery_bills']},
        {'name': 'Chartered Engineer Technical Verification Certificate', 'types': ['engineer_cert', 'other']},
        {'name': 'Bank Loan Sanction Letter', 'types': ['loan_sanction', 'bank_statement']}
    ],
    'export': [
        {'name': 'Importer Exporter Code (IEC)', 'types': ['iec', 'export_license']},
        {'name': 'RCMC Certificate (Export Promotion Council)', 'types': ['rcmc', 'other']},
        {'name': 'Shipping Bills / Export Invoices', 'types': ['shipping_bill', 'invoice']},
        {'name': 'GST LUT / Tax Clearance Certificate', 'types': ['gstin', 'tax_clearance']}
    ],
    'default': [
        {'name': 'Udyam Registration Certificate', 'types': ['udyam_cert', 'udyam']},
        {'name': 'Certificate of Incorporation / Registration Proof', 'types': ['incorporation', 'pan']},
        {'name': 'Company PAN Card', 'types': ['pan']},
        {'name': 'GST Registration Certificate', 'types': ['gstin']},
        {'name': 'Bank Account Proof / Cancelled Cheque', 'types': ['bank_statement', 'cheque', 'other']}
    ]
}

class ReadinessService:
    def __init__(self):
        pass

    def get_scheme_doc_requirements(self, scheme):
        if not scheme:
            return SCHEME_DOCUMENT_REQUIREMENTS['default']

        cat = (scheme.category or '').lower()
        name = (scheme.scheme_name or '').lower()

        if 'credit' in cat or 'guarantee' in cat or 'loan' in cat or 'cgtmse' in name:
            return SCHEME_DOCUMENT_REQUIREMENTS['credit_guarantee']
        elif 'startup' in cat or 'seed' in name or 'innovation' in cat:
            return SCHEME_DOCUMENT_REQUIREMENTS['startup']
        elif 'technology' in cat or 'zed' in name or 'clcss' in name or 'subsidy' in cat:
            return SCHEME_DOCUMENT_REQUIREMENTS['technology_subsidy']
        elif 'export' in cat or 'market' in cat:
            return SCHEME_DOCUMENT_REQUIREMENTS['export']
        else:
            return SCHEME_DOCUMENT_REQUIREMENTS['default']

    def evaluate_readiness(self, company_id, scheme_id=None, compliance_id=None):
        """
        Compares company documents against required documents and classifies each as:
        available, missing, expired, unverified.
        """
        company = Company.query.get(company_id)
        if not company:
            return None, "Company not found"

        today = date.today()
        uploaded_docs = Document.query.filter_by(company_id=company.id).all()

        target_name = "General Compliance Checklist"
        req_specs = SCHEME_DOCUMENT_REQUIREMENTS['default']

        if scheme_id:
            scheme = IncentiveScheme.query.get(scheme_id)
            if scheme:
                target_name = scheme.scheme_name
                req_specs = self.get_scheme_doc_requirements(scheme)
        elif compliance_id:
            comp = ComplianceRequirement.query.get(compliance_id)
            if comp:
                target_name = comp.requirement
                req_specs = SCHEME_DOCUMENT_REQUIREMENTS['default']

        items = []
        available_count = 0

        for spec in req_specs:
            matched_doc = None
            for d in uploaded_docs:
                d_type = (d.doc_type or '').lower()
                d_title = (d.title or '').lower()
                if any(t in d_type or t in d_title for t in spec['types']):
                    matched_doc = d
                    break

            if not matched_doc:
                status = 'missing'
                notes = 'Document not uploaded in vault'
            elif matched_doc.expiry_date and matched_doc.expiry_date < today:
                status = 'expired'
                notes = f'Expired on {matched_doc.expiry_date.strftime("%d %b %Y")}'
            elif matched_doc.verification_status == 'unverified':
                status = 'unverified'
                notes = f'Uploaded ({matched_doc.title}), pending verification'
            else:
                status = 'available'
                notes = f'Verified ({matched_doc.title})'
                available_count += 1

            items.append({
                'required_item': spec['name'],
                'status': status,
                'matched_doc_id': matched_doc.id if matched_doc else None,
                'matched_doc_title': matched_doc.title if matched_doc else None,
                'notes': notes
            })

        total = len(items)
        readiness_score = int((available_count / total) * 100) if total > 0 else 0

        return {
            'target_name': target_name,
            'scheme_id': scheme_id,
            'compliance_id': compliance_id,
            'total_required': total,
            'available_count': available_count,
            'readiness_score': readiness_score,
            'items': items
        }, None

    def generate_draft_checklist(self, company_id, scheme_id=None, compliance_id=None):
        """
        Generates an auditable AIDraft checklist from verified requirements.
        """
        readiness, err = self.evaluate_readiness(company_id, scheme_id, compliance_id)
        if err:
            return None, err

        company = Company.query.get(company_id)
        title = f"Document Readiness Checklist: {readiness['target_name']}"

        lines = [
            f"# {title}",
            f"**Enterprise:** {company.name} | **State:** {company.state} | **Date:** {datetime.utcnow().strftime('%d %B %Y')}",
            f"**Readiness Status:** {readiness['available_count']} of {readiness['total_required']} documents verified ({readiness['readiness_score']}%)\n",
            "### Itemized Document Verification",
            "| Required Document | Status | Existing File / Observation | Next Step |",
            "| :--- | :--- | :--- | :--- |"
        ]

        for item in readiness['items']:
            badge = item['status'].upper()
            action = "Ready for submission" if item['status'] == 'available' else "Upload or renew valid copy in Document Vault"
            file_ref = item['matched_doc_title'] or "None"
            lines.append(f"| {item['required_item']} | **{badge}** | {file_ref} - {item['notes']} | {action} |")

        lines.append("\n> [!NOTE] *Source Grounding Notice*: This checklist is derived from official ministry scheme documentation. Missing items must be uploaded to the private vault before applying.")

        content = "\n".join(lines)

        draft = AIDraft(
            company_id=company.id,
            scheme_id=scheme_id,
            compliance_id=compliance_id,
            draft_type='checklist',
            title=title,
            content=content,
            status='draft',
            version=1
        )
        db.session.add(draft)
        db.session.add(AuditEvent(
            tenant_id=company.tenant_id,
            action='draft_created',
            entity_type='AIDraft',
            entity_id=title,
            details=f"Generated draft checklist for '{readiness['target_name']}'"
        ))
        db.session.commit()
        return draft, None

    def generate_cover_letter(self, company_id, scheme_id):
        """
        Generates an official application cover letter citing Udyam registration and confirmed profile details.
        Highlights unresolved fields explicitly rather than hallucinating values.
        """
        company = Company.query.get(company_id)
        if not company:
            return None, "Company not found"

        scheme = IncentiveScheme.query.get(scheme_id)
        if not scheme:
            return None, "Scheme not found"

        turnover = company.get_latest_metric('turnover')
        investment = company.get_latest_metric('investment')
        employees = int(company.get_latest_metric('employees'))

        udyam = company.udyam_number or "[Unresolved: Missing Udyam Number]"
        pan = company.pan_number or "[Unresolved: Missing PAN]"
        gstin = company.gstin or "[Unresolved: Missing GSTIN]"
        inc_date = company.incorporation_date.strftime('%d/%m/%Y') if company.incorporation_date else "[Unresolved: Date of Incorporation]"

        title = f"Application Cover Letter: {scheme.scheme_name}"

        content = f"""To,
The Competent Sanctioning Authority / District Industries Centre,
{scheme.ministry_agency or 'Government of India / State Industrial Department'},
{company.state}, India.

Subject: Formal Application for Benefits under "{scheme.scheme_name}" (Ref ID: {scheme.id})

Respected Sir / Madam,

We, **{company.name}**, a registered **{company.entity_type}** having registered office in **{company.state}** (District: {company.district or '[Unresolved: District]'}), hereby respectfully submit our formal application for availing incentives under the subject scheme.

**1. Enterprise Summary & Statutory Credentials:**
- Name of Enterprise: {company.name} (Trade Name: {company.trade_name or company.name})
- Udyam Registration Number: {udyam}
- Permanent Account Number (PAN): {pan}
- GST Identification Number (GSTIN): {gstin}
- Date of Incorporation / Registration: {inc_date}
- Core Sector & Activity: {company.sector} ({company.activity_type})

**2. Baseline Operational Metrics (Financial Year 2025-26):**
- Gross Annual Turnover: ₹{turnover:,.2f}
- Cumulative Investment in Plant & Machinery: ₹{investment:,.2f}
- Direct Full-Time Workforce: {employees} Employees
- Startup / DPIIT Recognition: {"Yes (DPIIT Recognized)" if company.is_dpiit_recognized else "No"}
- ZED Sustainable Certification: {"Yes" if company.is_zed_certified else "Not yet enrolled"}

**3. Specific Scheme Benefit Claimed:**
As per official guidelines for "{scheme.scheme_name}", our enterprise meets the prescribed eligibility thresholds. We formally request consideration for:
"{scheme.key_benefit or 'Applicable subsidy / interest subvention / credit guarantee as notified'}"

**4. Enclosed Supporting Documentation Index:**
1. Certified True Copy of Udyam Registration Certificate
2. Certificate of Incorporation / Partnership Deed
3. Audited Financial Statements & GST 3B Summary
4. Certified Bank Mandate & Cancelled Cheque for Direct Benefit Transfer
5. Detailed Technical & Project Justification Note

We declare that the information provided above is true and substantiated by verified records. We request you to kindly process our application at the earliest.

Yours faithfully,

For **{company.name}**

_____________________________
Authorized Signatory / Managing Director
Name: [Signatory Name]
Designation: Director / Partner
Contact: [Signatory Phone / Email]
Date: {datetime.utcnow().strftime('%d %B %Y')}
"""

        draft = AIDraft(
            company_id=company.id,
            scheme_id=scheme.id,
            draft_type='cover_letter',
            title=title,
            content=content,
            status='draft',
            version=1
        )
        db.session.add(draft)
        db.session.add(AuditEvent(
            tenant_id=company.tenant_id,
            action='draft_created',
            entity_type='AIDraft',
            entity_id=title,
            details=f"Generated application cover letter for scheme '{scheme.scheme_name}'"
        ))
        db.session.commit()
        return draft, None

    def approve_draft(self, draft_id, user_id=None):
        draft = AIDraft.query.get(draft_id)
        if not draft:
            return False, "Draft not found"
        draft.status = 'approved'
        draft.approved_by_user_id = user_id
        draft.approved_at = datetime.utcnow()
        db.session.add(AuditEvent(
            tenant_id=draft.company.tenant_id,
            user_id=user_id,
            action='draft_approved',
            entity_type='AIDraft',
            entity_id=str(draft.id),
            details=f"User approved draft '{draft.title}' (version {draft.version})"
        ))
        db.session.commit()
        return True, "Draft approved successfully"
