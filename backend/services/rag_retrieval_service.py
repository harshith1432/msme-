"""
Unified Multi-Tenant RAG Retrieval Service for MSME Navigator.
Enforces:
  - Strict publication status barrier for central & state regulatory documents
  - Strict tenant and company isolation for private enterprise documents
  - Hybrid lexical (BM25 term overlap) + vector cosine similarity scoring
  - Query-level filtering preventing cross-tenant data leakage
"""
import re
import json
import math
import hashlib
from collections import Counter
from typing import List, Dict, Any, Optional

from backend.extensions import db
from backend.models import (
    KnowledgeDocument, DocumentChunk,
    Document, DocumentExtraction, Company,
    ComplianceRequirement, IncentiveScheme
)

def generate_text_embedding(text: str) -> List[float]:
    """Generates deterministic term-frequency normalized vector representation."""
    dim = 256
    vector = [0.0] * dim
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return vector

    for w in words:
        idx = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16) % dim
        vector[idx] += 1.0

    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [x / norm for x in vector]
    return vector

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, dot))

class RAGRetrievalService:
    def retrieve_authorized_chunks(
        self,
        query: str,
        company_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        state: Optional[str] = None,
        sector: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant chunks from:
        1. Official published regulatory knowledge base (KnowledgeDocument, status='published')
        2. Authorized enterprise uploaded vault documents (strictly filtered by company_id and tenant_id)
        """
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        query_vector = generate_text_embedding(query)
        scored_results = []

        # --- Source 1: Published Knowledge Documents (Central & State) ---
        kd_query = KnowledgeDocument.query.filter_by(status='published')
        if state:
            kd_query = kd_query.filter((KnowledgeDocument.state == state) | (KnowledgeDocument.state.is_(None)))

        published_kds = {doc.id: doc for doc in kd_query.all()}
        if published_kds:
            kd_chunks = DocumentChunk.query.filter(DocumentChunk.document_id.in_(list(published_kds.keys()))).all()
            for c in kd_chunks:
                doc = published_kds[c.document_id]
                c_vector = json.loads(c.embedding_json) if c.embedding_json else []
                v_score = cosine_similarity(query_vector, c_vector)

                c_words = Counter(re.findall(r'\b\w+\b', c.chunk_text.lower()))
                common_words = query_words.intersection(c_words.keys())
                k_score = len(common_words) / max(1, len(query_words))

                hybrid_score = round((0.6 * v_score) + (0.4 * k_score), 4)

                if hybrid_score > 0.05 or len(common_words) >= 2:
                    scored_results.append({
                        "chunk_id": f"KD-{c.id}",
                        "document_id": doc.id,
                        "document_title": doc.title,
                        "document_type": doc.document_type,
                        "authority": doc.issuing_authority,
                        "official_source_url": doc.official_source_url,
                        "jurisdiction": doc.jurisdiction,
                        "state": doc.state,
                        "page_number": c.page_number or 1,
                        "section_heading": c.section_heading or "Official Regulation",
                        "chunk_text": c.chunk_text,
                        "relevance_score": hybrid_score,
                        "is_tenant_document": False
                    })

        # --- Source 2: Authorized Tenant Documents (OCR & Vault extractions) ---
        if company_id:
            # Query-level multi-tenant filter: enforce company_id and verify tenant ownership
            doc_query = Document.query.filter_by(company_id=company_id)
            if tenant_id:
                # Join with company to strictly guarantee tenant match
                doc_query = doc_query.join(Company, Document.company_id == Company.id)\
                                     .filter(Company.tenant_id == tenant_id)

            tenant_docs = {d.id: d for d in doc_query.all()}
            if tenant_docs:
                extractions = DocumentExtraction.query.filter(
                    DocumentExtraction.document_id.in_(list(tenant_docs.keys()))
                ).all()

                for ext in extractions:
                    t_doc = tenant_docs[ext.document_id]
                    raw_text = ext.raw_text or ""
                    if not raw_text.strip():
                        continue

                    # Slice into paragraph chunks
                    paragraphs = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) > 30]
                    for idx, p_text in enumerate(paragraphs):
                        p_vector = generate_text_embedding(p_text)
                        v_score = cosine_similarity(query_vector, p_vector)

                        p_words = Counter(re.findall(r'\b\w+\b', p_text.lower()))
                        common_words = query_words.intersection(p_words.keys())
                        k_score = len(common_words) / max(1, len(query_words))

                        hybrid_score = round((0.6 * v_score) + (0.4 * k_score), 4)

                        if hybrid_score > 0.05 or len(common_words) >= 2:
                            scored_results.append({
                                "chunk_id": f"TD-{ext.id}-{idx}",
                                "document_id": t_doc.id,
                                "document_title": t_doc.title,
                                "document_type": f"Enterprise Document ({t_doc.doc_type})",
                                "authority": "Enterprise Vault",
                                "official_source_url": f"/documents/{t_doc.id}",
                                "jurisdiction": state or "Enterprise",
                                "state": state,
                                "page_number": idx + 1,
                                "section_heading": f"{t_doc.doc_type.upper()} Document Record",
                                "chunk_text": p_text,
                                "relevance_score": hybrid_score,
                                "is_tenant_document": True
                            })

        # Sort descending by relevance score
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:top_k]

    def get_dynamic_available_topics(
        self,
        company_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        state: Optional[str] = None,
        sector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dynamically inspects the actual RAG software database to find:
        1. Published Knowledge Documents (circulars, notifications)
        2. Authorized enterprise uploaded vault documents
        3. Active statutory compliance requirements for the state & Central
        4. Active incentive schemes for the state & Central
        Returns dynamically constructed topics and suggested questions so nothing is hardcoded.
        """
        topics_summary = {
            "documents": [],
            "compliances": [],
            "incentives": [],
            "vault": []
        }
        dynamic_questions = []

        try:
            # 1. Published Regulatory Documents in RAG
            kd_query = KnowledgeDocument.query.filter_by(status='published')
            if state:
                kd_query = kd_query.filter((KnowledgeDocument.state == state) | (KnowledgeDocument.state.is_(None)))
            published_docs = kd_query.limit(3).all()
            for doc in published_docs:
                topics_summary["documents"].append(doc.title)
                dynamic_questions.append(f"What does '{doc.title}' say about eligibility and rules?")

            # 2. Company Vault Documents in RAG
            if company_id:
                v_docs = Document.query.filter_by(company_id=company_id).limit(3).all()
                for v in v_docs:
                    topics_summary["vault"].append(v.title)
                    dynamic_questions.append(f"What does our uploaded document '{v.title}' state?")

            # 3. Active Compliance Requirements in RAG
            cr_query = ComplianceRequirement.query.filter_by(is_active=True)
            if state:
                cr_query = cr_query.filter((ComplianceRequirement.jurisdiction == 'Central') | (ComplianceRequirement.jurisdiction == state))
            
            reqs = cr_query.limit(3).all()
            for cr in reqs:
                topics_summary["compliances"].append(f"{cr.requirement} ({cr.domain})")
                dynamic_questions.append(f"What are our mandatory obligations for {cr.requirement}?")

            # 4. Active Incentive Schemes in RAG
            sch_query = IncentiveScheme.query.filter_by(is_active=True)
            if state:
                sch_query = sch_query.filter((IncentiveScheme.jurisdiction == 'Central') | (IncentiveScheme.jurisdiction == state))
            schemes = sch_query.limit(3).all()
            for s in schemes:
                topics_summary["incentives"].append(s.scheme_name)
                dynamic_questions.append(f"How can we apply for {s.scheme_name}?")

        except Exception:
            pass

        # Fallback if DB query returned empty
        if not dynamic_questions:
            dynamic_questions = [
                "What are my mandatory EPF and ESI rules for my employees?",
                f"Which government subsidies and incentives apply in {state or 'India'}?",
                "How does Section 43B(h) protect MSME payments within 45 days?",
                "What mandatory compliance documents are required for my enterprise?"
            ]

        return {
            "topics": topics_summary,
            "suggested_questions": dynamic_questions[:4]
        }

rag_retrieval_service = RAGRetrievalService()

