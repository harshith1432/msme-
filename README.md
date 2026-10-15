# 🇮🇳 MSME Navigator India

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/database-PostgreSQL%20%7C%20SQLite-336791.svg)](https://www.postgresql.org/)
[![LLM Provider](https://img.shields.io/badge/LLM-Hugging%20Face%20Inference-FFD21E.svg)](https://huggingface.co/)
[![Tests](https://img.shields.io/badge/tests-55%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, multi-tenant regulatory compliance intelligence, government subsidy discovery, and AI-driven document automation platform architected specifically for Indian Micro, Small, and Medium Enterprises (MSMEs).

---

## 🌟 Key Capabilities

### 1. 🤖 AI Regulatory Copilot (Grounded RAG)
- **Mandatory RAG Intermediary**: The LLM is never called directly with raw user prompts. Every interaction passes through input validation, topic verification, vector retrieval, grounded context assembly, and post-generation citation checking.
- **Hugging Face Hub Integration**: Integrates directly with Hugging Face Inference Providers via `huggingface_hub` using token-based backend security.
- **Zero Pretrained Hallucinations**: Enforces strict grounding in authorized government circulars (CGTMSE, PMEGP, Section 43B(h), FSSAI, Factories Act, EPF/ESI). If evidence is absent, it returns a polite, configurable refusal.
- **Dynamic Topic Discovery (No Hardcoded Questions)**: If a topic is missing or a greeting is typed, the assistant dynamically inspects the database and presents authorized circulars, compliance mandates, and subsidy schemes specific to the company's state and sector, complete with 1-click interactive prompt chips.

### 2. 📋 8-Section Executive Regulatory & Incentive Audit
- **Executive Audit Dashboard**: Evaluates enterprise compliance posture, statutory obligations, risk exposure, and financial grant eligibility.
- **Statutory Rules Engine**: Evaluates 600+ central and state laws covering labor welfare, environmental consents, factories registrations, and municipal permits.
- **MSMED Act Section 43B(h) Audit**: Tracks vendor payment terms (15-day / 45-day rules) to prevent disallowed income tax deductions.
- **State-Specific Subsidy Discovery**: Maps eligible capital subsidies, interest subventions, electricity duty exemptions, and stamp duty waivers across all Indian states and Union Territories.

### 3. 📂 Multi-Tenant Document Vault & Applications Workspace
- **Enterprise Isolation**: Cryptographically verified tenant boundaries preventing cross-tenant document or knowledge leakage.
- **Document Ingestion Pipeline**: SHA-256 deduplication, validation, text chunking, and strict publication barriers for regulatory knowledge bases.
- **Automated Document Generation**: Generates court-ready and scheme-ready application checklists (PDF via ReportLab) and formal cover letters (DOCX via python-docx).

### 4. 🌐 Multilingual Accessibility
- Real-time localization across 8 Indian languages: Hindi (हिन्दी), Tamil (தமிழ்), Telugu (తెలుగు), Kannada (ಕನ್ನಡ), Gujarati (ગુજરાતી), Marathi (मराठी), Bengali (বাংলা), and English.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    Client(["🌐 Web Client (Browser)"])
    
    subgraph ReverseProxy ["Reverse Proxy & Static Cache"]
        Nginx["Nginx Reverse Proxy (:80 / :443)"]
    end

    subgraph AppServer ["Flask Application Gateway (:5000)"]
        FlaskCore["Core App Factory & Middleware"]
        AuthModule["Multi-Tenant Auth & RBAC"]
        RulesEngine["MSME Compliance Rules Engine"]
        RAGRouter["RAG Query & Chat Orchestrator"]
    end

    subgraph SecurityShield ["Mandatory RAG Security & Retrieval Barrier"]
        InputVal["Input & Topic Validation"]
        VectorSearch["Vector Retrieval & Tenant Filter"]
        RelevanceGate["Relevance & Sufficiency Validator"]
        ContextBuild["Isolated Context Constructor"]
        CitationVerify["Citation & Grounding Validator"]
    end

    subgraph ExternalLLM ["Hugging Face Inference Layer"]
        HFHub["Hugging Face Serverless API<br/>(e.g., Qwen 2.5 / Mistral / Llama)"]
    end

    subgraph StorageLayer ["Data & Storage Layer"]
        Postgres[(PostgreSQL 16 / SQLite)]
        DocVault["Encrypted Document Storage"]
    end

    Client -->|HTTPS| Nginx
    Nginx -->|WSGI Proxy| FlaskCore
    FlaskCore --> AuthModule
    FlaskCore --> RulesEngine
    FlaskCore --> RAGRouter

    RAGRouter --> InputVal
    InputVal --> VectorSearch
    VectorSearch --> Postgres
    VectorSearch --> RelevanceGate
    RelevanceGate -->|Approved Evidence| ContextBuild
    RelevanceGate -->|Insufficient Evidence| Client
    ContextBuild --> HFHub
    HFHub --> CitationVerify
    CitationVerify --> Client
```

---

## 📁 Repository Structure

```text
msme/
├── app/                        # Main web application package
│   ├── core/                   # Security headers, auth decorators, structured logging
│   ├── models/                 # SQLAlchemy ORM domain models
│   ├── routes/                 # Flask route blueprints (web & API)
│   ├── services/               # RAG, rules engine, document generator, Hugging Face client
│   ├── static/                 # Stylesheets, JS modules, brand assets
│   └── templates/              # Jinja2 layouts & responsive views
├── backend/                    # Core business logic & database services
├── documentation/              # Architectural, storage, deployment, and security manuals
├── scripts/                    # Database backup, restore, and health checks
├── tests/                      # Automated test suite (55 tests)
│   ├── test_huggingface_rag.py # 15 RAG security & boundary tests
│   ├── test_rag_and_vault.py   # Multi-tenant vault & ingestion tests
│   └── test_platform.py        # Core platform & compliance tests
├── .env.example                # Template for environment variables
├── compose.yaml                # Local development Docker Compose
├── compose.production.yaml     # Production Docker Compose with Nginx & Redis
├── Dockerfile                  # Non-root multi-stage production container
├── requirements.txt            # Pinned dependencies
├── run.py                      # Local development runner
└── wsgi.py                     # Gunicorn entrypoint
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Git
- PostgreSQL (or SQLite for quick local trials)
- Hugging Face API Token (optional, fallback offline RAG mode included)

### 1. Clone the Repository
```bash
git clone https://github.com/harshith1432/msme-.git
cd msme-
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your configuration:
```bash
cp .env.example .env
```

Key environment settings:
```env
FLASK_ENV=development
SECRET_KEY=your-secure-random-secret-key
DATABASE_URL=sqlite:///msme_navigator.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/msme

# Hugging Face Inference Settings
HF_TOKEN=your_hugging_face_token
HF_MODEL=Qwen/Qwen2.5-72B-Instruct
```

### 5. Initialize Database & Seed Statutory Rules
```bash
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

### 6. Run the Application
```bash
python run.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## 🧪 Automated Testing

The platform includes 55 comprehensive automated tests covering unit logic, integration flows, RAG guardrails, and tenant security.

```bash
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- ✅ **15 RAG & Hugging Face Security Tests**:
  1. Question directly answered by authorized document.
  2. Out-of-scope / unrelated questions rejected before LLM call.
  3. Absent evidence returns refusal message.
  4. Low retrieval relevance score rejected.
  5. Partially supported questions handled with clarification.
  6. Ambiguous question detection.
  7. Direct prompt injection attempts blocked.
  8. Malicious instructions embedded in retrieved documents sanitized.
  9. Cross-tenant document retrieval strictly blocked.
  10. Unauthorized document access rejected.
  11. Provider timeout / rate limits handled gracefully.
  12. Missing / invalid credentials handled with fail-safe refusal.
  13. Hallucinated / unsupported claims blocked.
  14. Fabricated citation detection.
  15. Multi-turn restriction bypass attempts neutralized.
- ✅ **Document Vault & Multi-Tenant Isolation Tests**
- ✅ **PDF & DOCX Automated Generation Tests**
- ✅ **Statutory Compliance Rules Engine Tests**

---

## 🐳 Docker Deployment

Run with Docker Compose:

```bash
# Start full stack (Flask + PostgreSQL)
docker compose up -d --build
```

To run in production mode with Gunicorn and Nginx:
```bash
docker compose -f compose.production.yaml up -d --build
```

---

## 🛡️ Security & Privacy Principles

1. **Zero Secret Leakage**: API tokens and database credentials remain strictly on the backend and are excluded from source control.
2. **Multi-Tenant Isolation**: Row-level tenant filtering (`tenant_id`) is applied at the query level.
3. **No Unrestricted LLM Direct Access**: The frontend cannot query the model directly.
4. **Context Isolation**: Retrieved reference chunks are isolated from system prompt instructions to prevent indirect prompt injection.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
