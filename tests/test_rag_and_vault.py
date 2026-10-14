"""
Comprehensive Test Suite for MSME Navigator:
  1. Translation Service & Token Preservation & DB Caching
  2. Production RAG Ingestion, Chunking & Strict Publication Barrier
  3. AI Advisor Grounded Ingestion & Citation Attribution
  4. SSRF-Protected Official Website Research
  5. Smart Document Vault Virtual Folders & De-duplicated Linking
  6. Application Workspace Wizard & Downloadable Artifact Generation (PDF & DOCX)
"""
import os
import json
import pytest
from datetime import datetime, date
from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import (
    Tenant, User, Company, Document, DocumentFolder, DocumentFolderLink,
    ApplicationWorkspace, GeneratedArtifact, KnowledgeDocument, DocumentChunk,
    TranslationCache, IngestionJob
)
from app.services.translation_service import translation_service
from app.services.rag_service import rag_service
from app.services.website_research import website_research_service, SSRFProtectionError
from app.services.ai_advisor import AIAdvisor
from app.services.document_generator import document_generator

@pytest.fixture
def app():
    test_app = create_app(TestingConfig)
    with test_app.app_context():
        yield test_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_setup(app):
    with app.app_context():
        tenant = Tenant(name='RAG Test Tenant', slug=f'rag-test-{int(datetime.utcnow().timestamp())}')
        db.session.add(tenant)
        db.session.flush()

        user = User(name='RAG Admin', email=f'admin_{int(datetime.utcnow().timestamp())}@gov.in', role='platform_admin')
        user.set_password('Admin@1234')
        db.session.add(user)
        db.session.flush()

        company = Company(
            tenant_id=tenant.id,
            name='Test Precision Gears LLP',
            trade_name='Precision Gears',
            state='Karnataka',
            entity_type='Limited Liability Partnership (LLP)',
            sector='Manufacturing',
            created_by_user_id=user.id,
            is_onboarded=True,
            udyam_number='UDYAM-KR-03-0098765'
        )
        db.session.add(company)
        db.session.commit()

        return {
            'tenant_id': tenant.id,
            'user_id': user.id,
            'company_id': company.id
        }


# --- 1. Translation Service Token Preservation & DB Caching ---

def test_translation_tokens_and_caching(app, test_setup):
    with app.app_context():
        sample_text = "Filing deadline for CC-001 by enterprise UDYAM-KR-03-0098765 with turnover ₹ 5,00,00,000 on https://udyamregistration.gov.in."
        protected_text, token_map = translation_service.protect_tokens(sample_text)

        # Ensure all tokens are replaced by placeholders
        assert "CC-001" not in protected_text
        assert "UDYAM-KR-03-0098765" not in protected_text
        assert "₹ 5,00,00,000" not in protected_text
        assert "https://udyamregistration.gov.in" not in protected_text

        # Restore tokens
        restored_text = translation_service.restore_tokens(protected_text, token_map)
        assert restored_text == sample_text

        # Test DB translation cache
        h = translation_service._generate_hash("Priority Sector Lending", "kn")
        cached_entry = TranslationCache(
            source_hash=h,
            source_text="Priority Sector Lending",
            target_lang="kn",
            translated_text="ಆದ್ಯತಾ ವಲಯದ ಸಾಲ ನೀಡಿಕೆ",
            provider="test_mock",
            is_verified=True
        )
        db.session.add(cached_entry)
        db.session.commit()

        # Translate should retrieve directly from DB
        res = translation_service.translate_text("Priority Sector Lending", target_lang="kn")
        assert res == "ಆದ್ಯತಾ ವಲಯದ ಸಾಲ ನೀಡಿಕೆ"


# --- 2. RAG Ingestion, Chunking & Publication Barrier ---

def test_rag_ingestion_and_strict_publication_barrier(app, test_setup):
    with app.app_context():
        # Create a test circular text file
        doc_filename = f"test_circular_{int(datetime.utcnow().timestamp())}.txt"
        doc_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_filename)
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(
                "--- Master Circular on CGTMSE Coverage 2026 ---\n"
                "Ministry of MSME and SIDBI announce enhanced guarantee coverage up to Rs 5 Crore.\n\n"
                "Section 1: Collateral-Free Lending Requirements\n"
                "All scheduled commercial banks and NBFCs shall extend collateral-free loans to Micro and Small Enterprises "
                "with an annual guarantee fee concession of 10% for women and SC/ST entrepreneurs.\n\n"
                "Section 2: Claim Settlement Timelines\n"
                "Guaranteed claims must be formally processed and credited within 30 statutory days from default notification."
            )

        k_doc = KnowledgeDocument(
            title="Master Circular on CGTMSE Coverage 2026",
            filename=doc_filename,
            file_path=doc_path,
            document_type="circular",
            issuing_authority="Ministry of MSME / SIDBI",
            official_source_url="https://www.cgtmse.in/circulars/2026",
            jurisdiction="Central",
            status="draft"
        )
        db.session.add(k_doc)
        db.session.commit()
        doc_id = k_doc.id

        # Run automated ingestion & chunking
        ok, msg = rag_service.process_document_ingestion(doc_id)
        assert ok is True
        
        # Verify chunks created and status is needs_review
        k_doc = KnowledgeDocument.query.get(doc_id)
        assert k_doc.status == "needs_review"
        assert len(k_doc.chunks) > 0
        assert k_doc.content_hash is not None

        # STRICT PUBLICATION BARRIER CHECK:
        # Before publication, hybrid_retrieve MUST return 0 results
        results_before = rag_service.hybrid_retrieve("guarantee fee concession for women", jurisdiction="Central")
        assert not any(r['document_id'] == doc_id for r in results_before)

        # Admin officially approves and publishes the document
        pub_ok, pub_msg = rag_service.publish_document(doc_id, reviewer_user_id=test_setup['user_id'], notes="Verified with official gazette.")
        assert pub_ok is True

        k_doc = KnowledgeDocument.query.get(doc_id)
        assert k_doc.status == "published"
        assert k_doc.published_at is not None

        # After publication, hybrid_retrieve MUST retrieve the chunk
        results_after = rag_service.hybrid_retrieve("guarantee fee concession for women", jurisdiction="Central", top_k=3)
        assert len(results_after) > 0
        matched = next((r for r in results_after if r['document_id'] == doc_id), None)
        assert matched is not None
        assert matched['document_title'] == "Master Circular on CGTMSE Coverage 2026"
        assert matched['authority'] == "Ministry of MSME / SIDBI"
        assert matched['official_source_url'] == "https://www.cgtmse.in/circulars/2026"
        assert matched['relevance_score'] > 0


# --- 3. AI Advisor RAG Grounded Answer ---

def test_ai_advisor_rag_grounded_answer(app, test_setup):
    with app.app_context():
        comp = Company.query.get(test_setup['company_id'])
        advisor = AIAdvisor()
        profile = {
            'name': comp.name,
            'state': comp.state,
            'sector': comp.sector,
            'turnover': 20000000,
            'investment': 8000000,
            'employees': 15
        }

        # Query asking specifically about the published CGTMSE guarantee fee concession
        res = advisor.answer_query("What is the guarantee fee concession for women under CGTMSE?", profile, lang='en')
        assert res['tool_called'] in ['rag_knowledge_retrieval', 'search_published_schemes']
        assert len(res['citations']) > 0
        assert res['text'] is not None


# --- 4. SSRF-Protected Official Website Research ---

def test_ssrf_website_research_security():
    # 1. Reject localhost / loopback
    with pytest.raises(SSRFProtectionError):
        website_research_service.validate_target_url("http://127.0.0.1:8000/internal")

    # 2. Reject cloud metadata IP
    with pytest.raises(SSRFProtectionError):
        website_research_service.validate_target_url("http://169.254.169.254/latest/meta-data/")

    # 3. Reject non-whitelisted commercial / malicious domain
    with pytest.raises(SSRFProtectionError):
        website_research_service.validate_target_url("https://malicious-external-site.com/exploit")

    # 4. Accept authorized official government portals in domain allowlist
    assert website_research_service.is_domain_allowed("udyamregistration.gov.in") is True
    assert website_research_service.is_domain_allowed("cgtmse.in") is True
    assert website_research_service.is_domain_allowed("nsws.gov.in") is True
    assert website_research_service.is_domain_allowed("shramsuvidha.gov.in") is True
    assert website_research_service.is_domain_allowed("randomhacker.xyz") is False


# --- 5. Smart Document Vault Virtual Folders & Linking ---

def test_smart_vault_virtual_folders_and_linking(app, client, test_setup):
    with app.app_context():
        comp_id = test_setup['company_id']
        
        # Create central physical document
        doc = Document(
            company_id=comp_id,
            title='Tax Audit Report FY 2025-26',
            doc_type='audit_report',
            filename='test_audit.pdf',
            file_path='/tmp/test_audit.pdf',
            file_size=204800,
            verification_status='verified'
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

    with client.session_transaction() as sess:
        sess['user_id'] = test_setup['user_id']
        sess['user_role'] = 'owner'

    # Create Virtual Folder
    res = client.post('/documents/folders/create', data={
        'name': 'Annual Tax Dossier',
        'folder_type': 'compliance_package'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        folder = DocumentFolder.query.filter_by(company_id=comp_id, name='Annual Tax Dossier').first()
        assert folder is not None
        folder_id = folder.id

    # Link document to folder
    res_link = client.post('/documents/link', data={
        'document_id': doc_id,
        'folder_id': folder_id
    }, follow_redirects=True)
    assert res_link.status_code == 200

    # Verify link exists and physical document is NOT duplicated
    with app.app_context():
        link = DocumentFolderLink.query.filter_by(folder_id=folder_id, document_id=doc_id).first()
        assert link is not None
        assert Document.query.filter_by(company_id=comp_id, title='Tax Audit Report FY 2025-26').count() == 1


# --- 6. Application Workspace Wizard & Downloadable Artifact Generation ---

def test_application_workspace_and_artifact_generation(app, client, test_setup):
    with client.session_transaction() as sess:
        sess['user_id'] = test_setup['user_id']
        sess['user_role'] = 'owner'

    # Execute Package Wizard
    res = client.post('/drafts/wizard', data={
        'title': 'CGTMSE Credit Guarantee & Subsidy Package 2026',
        'workspace_type': 'incentive',
        'reference_id': 'CI-001',
        'notes': 'Prepared for SBI Priority Sector Branch submission.'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        ws = ApplicationWorkspace.query.filter_by(
            company_id=test_setup['company_id'],
            title='CGTMSE Credit Guarantee & Subsidy Package 2026'
        ).first()
        assert ws is not None
        assert ws.workspace_type == 'incentive'
        assert ws.folder_id is not None
        
        # Verify generated artifacts
        artifacts = GeneratedArtifact.query.filter_by(workspace_id=ws.id).all()
        assert len(artifacts) >= 2

        pdf_art = next((a for a in artifacts if a.artifact_type == 'checklist'), None)
        docx_art = next((a for a in artifacts if a.artifact_type == 'cover_letter'), None)
        assert pdf_art is not None
        assert docx_art is not None

        # Verify files exist on disk
        assert os.path.exists(pdf_art.file_path)
        assert os.path.getsize(pdf_art.file_path) > 500
        assert os.path.exists(docx_art.file_path)
        assert os.path.getsize(docx_art.file_path) > 500
        
        pdf_art_id = pdf_art.id
        docx_art_id = docx_art.id

    # Test downloading the PDF artifact
    dl_pdf = client.get(f'/drafts/download/{pdf_art_id}')
    assert dl_pdf.status_code == 200
    assert dl_pdf.headers.get('Content-Disposition') is not None
    assert dl_pdf.headers.get('Content-Type') == 'application/pdf'

    # Test downloading the DOCX artifact
    dl_docx = client.get(f'/drafts/download/{docx_art_id}')
    assert dl_docx.status_code == 200
    assert dl_docx.headers.get('Content-Disposition') is not None
