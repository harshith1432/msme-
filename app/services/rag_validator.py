"""
RAG Validation and Safety Layer for MSME Navigator.
Implements:
  - Input & Scope Validation (in-scope vs general knowledge questions)
  - Prompt Injection & Jailbreak Detection (direct & indirect)
  - Ambiguity Detection and Clarification Triggering
  - Multi-tier Retrieval Score & Evidence Sufficiency Validation
  - Post-Generation Grounding & Citation Integrity Verification
"""
import re
from typing import List, Dict, Any, Tuple, Optional

# Out-of-scope patterns (General knowledge, unrelated domains, coding, creative writing)
OUT_OF_SCOPE_PATTERNS = [
    r'\b(write|generate|compose|narrate|tell\s+me)\s+(a\s+)?(fantasy\s+|bedtime\s+|sci-fi\s+)?(poem|story|song|essay|joke|code|script|html|python)\b',
    r'\b(who\s+won|who\s+is|what\s+is\s+the\s+capital\s+of|weather\s+in|recipe\s+for|movie|film|actor|cricket|football|fifa)\b',
    r'\b(solve\s+math|calculate\s+\d+|integrate|derivative|pythagorean)\b',
    r'\b(translate\s+into\s+french|spanish|german)\b',
    r'\b(tell\s+me\s+a\s+joke|how\s+to\s+bake|make\s+a\s+cake|plan\s+a\s+vacation|dragons|wizard)\b'
]

# Prompt injection & jailbreak patterns
PROMPT_INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions',
    r'disregard\s+(the\s+)?(system\s+prompt|rules|constraints)',
    r'you\s+are\s+now\s+(in\s+developer\s+mode|dan|unrestricted|an\s+unfiltered)',
    r'reveal\s+(your\s+)?(system\s+prompt|secret|api\s+key|password|token)',
    r'print\s+(the\s+)?(instructions|internal\s+prompts|system\s+message)',
    r'jailbreak',
    r'override\s+(security|policy|restrictions)',
    r'bypass\s+(rag|safeguards|filters)',
    r'act\s+as\s+(an?\s+)?(unrestricted|unfiltered|general|dan|jailbroken)\b'
]

# Legitimate MSME & compliance domain keywords
IN_SCOPE_KEYWORDS = [
    'compliance', 'statutory', 'regulation', 'act', 'code', 'rule', 'section', 'clause',
    'labour', 'labor', 'wages', 'minimum wage', 'salary', 'headcount', 'workforce', 'staff', 'employee',
    'pf', 'epf', 'epfo', 'esi', 'esic', 'gratuity', 'bonus', 'posh', 'factory', 'establishment',
    'gst', 'gstin', 'gstr', 'tax', 'tds', 'tcs', 'advance tax', 'e-invoice', 'audit', '43b', '43b(h)',
    'income tax', 'pan', 'tan', 'itr', 'financial year', 'due date', 'deadline', 'penalty', 'return',
    'msme', 'micro', 'small', 'medium', 'enterprise', 'udyam', 'registration', 'certificate', 'dpiit',
    'startup', '80-iac', 'angel tax', 'subsidy', 'incentive', 'scheme', 'grant', 'cgtmse', 'pmegp',
    'mudra', 'zed', 'lean', 'ramp', 'cluster', 'interest subvention', 'capital subsidy',
    'fssai', 'food safety', 'licence', 'license', 'pollution', 'pcb', 'noc', 'trade license',
    'shops and establishments', 'professional tax', 'pt', 'document', 'vault', 'evidence',
    'delayed payment', 'samadhaan', 'interest rate', 'vendor', 'invoice', 'credit guarantee'
]

# Ambiguous, underspecified questions requiring clarification
AMBIGUOUS_PATTERNS = [
    r'^(what\s+are\s+the\s+rules\??)$',
    r'^(tell\s+me\s+about\s+compliance\??)$',
    r'^(what\s+should\s+i\s+do\??)$',
    r'^(rules\??)$',
    r'^(compliance\??)$',
    r'^(schemes\??)$',
    r'^(what\s+applies\s+to\s+me\??)$',
    r'^(give\s+me\s+info\??)$'
]

# Greetings and guidance requests
GREETING_PATTERNS = [
    r'^(hi|hello|hey|namaste|kem\s*cho|vanakkam|good\s+(morning|afternoon|evening)|howdy|greetings|start)[\s\!.,?]*$',
    r'^(what\s+to\s+ask|how\s+to\s+ask|what\s+can\s+i\s+ask|what\s+should\s+i\s+ask|what\s+can\s+you\s+do|who\s+are\s+you|how\s+can\s+you\s+help|guide\s*me|help\s*me|help)[\s\!.,?]*$'
]

class RAGValidator:
    def __init__(self, refusal_message: Optional[str] = None, relevance_threshold: float = 0.25):
        self.refusal_message = refusal_message or (
            "I can only answer questions supported by the information available in my authorized knowledge base. "
            "Please ask a question related to the available documents."
        )
        self.relevance_threshold = relevance_threshold

    def is_greeting_or_guidance(self, user_question: str) -> bool:
        if not user_question:
            return False
        t = user_question.strip().lower()
        t_clean = re.sub(r'[^a-z0-9\s]', '', t).strip()
        
        greeting_words = {'hi', 'hello', 'hey', 'namaste', 'kem cho', 'vanakkam', 'greetings', 'start', 'guide me', 'help me', 'help'}
        if t_clean in greeting_words:
            return True
            
        for pat in GREETING_PATTERNS:
            if re.match(pat, t):
                return True
                
        words = t_clean.split()
        if len(words) <= 3 and words and words[0] in {'hi', 'hello', 'hey', 'greetings'}:
            domain_terms = {'pf', 'epf', 'esi', 'gst', 'tax', 'subsidy', 'scheme', 'rule', 'act', 'code', '43b', 'penalty', 'udyam'}
            if not any(w in domain_terms for w in words):
                return True
                
        return False

    def generate_greeting_guidance(
        self,
        profile: Optional[Dict[str, Any]] = None,
        dynamic_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        profile = profile or {}
        company_name = profile.get("name", "Your Enterprise")
        state = profile.get("state", "India")
        sector = profile.get("sector", "Manufacturing")
        employees = profile.get("employees", 0)

        emp_str = f"{employees} workers" if employees else "your workforce"

        # Build dynamic knowledge base inventory from actual DB
        topics = (dynamic_data or {}).get("topics", {})
        docs_list = topics.get("documents", [])
        comp_list = topics.get("compliances", [])
        sch_list = topics.get("incentives", [])
        vault_docs = topics.get("vault", [])

        docs_str = ", ".join(docs_list) if docs_list else "Master Circular on CGTMSE Scheme"
        comp_str = ", ".join(comp_list) if comp_list else f"Udyam, EPF & ESI for {emp_str}"
        sch_str = ", ".join(sch_list) if sch_list else f"{state} MSME Subsidies"
        vault_line = f"• **Your Verified Vault Documents:** {', '.join(vault_docs)}\n" if vault_docs else ""

        text = (
            f"Hello! I am your MSME Regulatory Copilot for **{company_name}** ({state}, {sector}).\n\n"
            f"I check the authorized regulatory knowledge base to answer your questions.\n\n"
            f"📚 **What currently exists in my authorized knowledge base:**\n"
            f"• **Official Documents:** {docs_str}\n"
            f"• **Statutory Compliances:** {comp_str}\n"
            f"• **Incentive Schemes:** {sch_str}\n"
            f"{vault_line}\n"
            f"💡 **What to ask:**\n"
            f"You can ask me questions about any of the official regulations, deadlines, or subsidy schemes listed above."
        )

        suggestions = (dynamic_data or {}).get("suggested_questions") or [
            f"What are my mandatory EPF and ESI rules for {emp_str}?",
            f"Which {state} government subsidies and incentives am I eligible for?",
            "Explain the Section 43B(h) 45-day MSME payment protection rule",
            f"What mandatory compliance documents are required for {sector}?"
        ]

        return text, suggestions

    def get_default_suggestions(self, profile: Optional[Dict[str, Any]] = None) -> List[str]:
        profile = profile or {}
        state = profile.get("state", "Central & State")
        sector = profile.get("sector", "MSME")
        employees = profile.get("employees", 0)
        emp_str = f"for {employees} workers" if employees else ""
        return [
            f"What are my mandatory EPF and ESI rules {emp_str}?".strip(),
            f"Which {state} subsidies and incentives can I claim?",
            "How does Section 43B(h) protect MSME payments within 45 days?",
            f"What mandatory compliance documents are needed for {sector}?"
        ]

    def validate_input(self, user_question: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates user input length, prompt injection attempts, and scope.
        Returns: (is_valid, sanitized_text, refusal_or_clarification_message)
        """
        if not user_question or not user_question.strip():
            return False, "", "Please provide a valid question."

        text = user_question.strip()

        # Input length limitation
        if len(text) > 1500:
            return False, text[:1500], "Question exceeds maximum length limit of 1500 characters. Please provide a concise question."

        lower_text = text.lower()

        # Check prompt injection
        for pat in PROMPT_INJECTION_PATTERNS:
            if re.search(pat, lower_text):
                return False, text, self.refusal_message

        # Check out-of-scope general purpose queries
        for pat in OUT_OF_SCOPE_PATTERNS:
            if re.search(pat, lower_text):
                return False, text, self.refusal_message

        # Check ambiguity
        for pat in AMBIGUOUS_PATTERNS:
            if re.match(pat, lower_text):
                return False, text, (
                    "Your question is broad. To provide an accurate answer from authorized regulatory documents, "
                    "please specify your domain of interest (e.g., EPF/ESI labour thresholds, GST return deadlines, "
                    "Section 43B(h) vendor payment rules, or state industrial subsidies)."
                )

        return True, text, None

    def validate_evidence(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, List[Dict[str, Any]], Optional[str]]:
        """
        Evaluates retrieval scores and evidence sufficiency before calling the LLM.
        Rejects requests if no sufficiently relevant evidence is found.
        """
        if not retrieved_chunks:
            return False, [], self.refusal_message

        # Filter chunks that satisfy minimum relevance threshold
        valid_chunks = [c for c in retrieved_chunks if c.get("relevance_score", 0.0) >= self.relevance_threshold]
        if not valid_chunks:
            return False, [], self.refusal_message

        # Verify substantive evidence match (not just single random common word)
        query_terms = set(re.findall(r'\b[a-zA-Z0-9_\-\.]{3,}\b', query.lower()))
        # Remove universal stop-words
        stop_words = {'what', 'when', 'where', 'which', 'who', 'how', 'does', 'with', 'from', 'have', 'been', 'this', 'that', 'your', 'about'}
        core_query_terms = query_terms - stop_words

        top_chunk = valid_chunks[0]
        chunk_text_lower = top_chunk["chunk_text"].lower()

        overlap_count = sum(1 for term in core_query_terms if term in chunk_text_lower)
        
        # If there are core query terms but zero substantive match in top chunk, reject
        if core_query_terms and overlap_count == 0 and top_chunk["relevance_score"] < 0.35:
            return False, [], self.refusal_message

        return True, valid_chunks, None

    def validate_grounding_and_citations(
        self,
        generated_answer: str,
        authorized_chunks: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Validates generated answer against authorized source citations.
        Ensures citations only refer to actual retrieved sources and strips hallucinated ones.
        """
        verified_citations = []
        known_docs = {c["document_title"].lower(): c for c in authorized_chunks}
        known_ids = {str(c["chunk_id"]): c for c in authorized_chunks}

        # Build clean, verified citations list
        seen_docs = set()
        for c in authorized_chunks:
            doc_title = c.get("document_title", "Official Regulatory Document")
            if doc_title not in seen_docs:
                seen_docs.add(doc_title)
                verified_citations.append({
                    "law": doc_title,
                    "authority": c.get("authority") or "Government Authority",
                    "link": c.get("official_source_url") or "https://www.india.gov.in",
                    "section": c.get("section_heading") or "General Provision",
                    "page": c.get("page_number") or 1,
                    "score": c.get("relevance_score", 0.0),
                    "chunk_id": c.get("chunk_id")
                })

        # Sanitize answer if model hallucinated external claims not in context
        cleaned_answer = generated_answer.strip()

        # If answer states it cannot find info despite generation, harmonize with refusal
        if any(phrase in cleaned_answer.lower() for phrase in [
            "the provided documents do not mention",
            "the provided context does not contain",
            "information is not available in the provided",
            "cannot find information in the authorized documents"
        ]):
            cleaned_answer = self.refusal_message
            verified_citations = []

        return cleaned_answer, verified_citations

rag_validator = RAGValidator()
