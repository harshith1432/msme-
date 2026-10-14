# Implementation Task Plan

This file is the proposed build backlog. Complete tasks in dependency order and keep status updated.

Status values: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`.

## Phase 0 — Product and data discovery
- [x] Confirm target customer, pilot geography and pilot sectors.
- [x] Inspect every worksheet in the source workbook and record exact row counts (628 total).
- [x] Create a data dictionary for every column.
- [x] Profile missing fields, duplicate candidates, inconsistent jurisdictions and malformed URLs.
- [x] Define verification rubric and reviewer workflow.
- [x] Select initial official sources and domain reviewers.
- [x] Write explicit MVP scope and non-goals.
**Exit criteria:** data quality report and approved pilot scope exist. [DONE]

## Phase 1 — Repository and engineering foundation
- [x] Establish Flask application factory and configuration profiles.
- [x] Create blueprints for auth, tenants, companies, knowledge, rules, compliance, incentives, tasks, documents, admin and audit.
- [x] Configure PostgreSQL / SQLite with SQLAlchemy.
- [x] Add automated test fixtures and pytest suite.
- [x] Add structured logging and health endpoints.
- [x] Document local setup, test and run commands.
**Exit criteria:** app starts locally, database seeds, all tests pass. [DONE]

## Phase 2 — Authentication and tenant foundation
- [x] Implement multi-tenant workspace isolation.
- [x] Implement server-side role and tenant permission models (Tenant, User, Membership, ClientAccess).
- [x] Add cross-tenant access controls for private documents and company records.
- [x] Add audit events for security and profile modifications.
**Exit criteria:** users can securely access only authorised tenant data. [DONE]

## Phase 3 — Company profile and classification
- [x] Implement company and company-metric models with provenance (user_entered, imported, verified).
- [x] Store dated turnover, investment and employee count metrics.
- [x] Implement effective-dated, versioned MSME classification logic based on 1 April 2025 revised limits.
- [x] Implement DPIIT Startup India 2026 definition (₹200 cr turnover & Deep Tech ₹300 cr / 20 yrs).
- [x] Build company profile management and instant re-evaluation.
**Exit criteria:** company profile produces reproducible preliminary classification. [DONE]

## Phase 4 — Knowledge base and workbook ingestion
- [x] Ingest all 628 official records into structured JSON and database tables:
  - 94 Central Compliance
  - 330 State Compliance across 36 States/UTs
  - 78 Central Incentives
  - 126 State Incentives
- [x] Add source review queue and approval workflow (RegulatoryChange model & Admin Queue).
- [x] Add source freshness labels (Oct 2026 verified vs knowledge-based).
- [x] Create admin search, verification and review screens (`/admin/records`, `/admin/changes`).
**Exit criteria:** administrators can review and publish traceable records safely. [DONE]

## Phase 5 — Rules engine
- [x] Build deterministic evaluator matching headcount and turnover triggers against statutory rules.
- [x] Implement statutory Employer Ladder (1+, 10+, 20+, 25+, 30+, 40+, 50+, 100+, 300+ staff).
- [x] Implement Turnover Ladder (>₹12L FSSAI, >₹20L/40L GST, >₹1Cr audit, >₹5Cr e-invoicing).
- [x] Add unit tests for boundaries, thresholds, and effective dates.
**Exit criteria:** same profile snapshot and rule version always produce the same outcome. [DONE]

## Phase 6 — Compliance workspace
- [x] Build compliance catalogue with live search, domain filters, and Central/State tabs.
- [x] Generate company-specific obligations from published rules.
- [x] Build requirement detail page with why-it-applies, statutory source, authority, and official portal link.
- [x] Add obligation status tracking.
**Exit criteria:** users can understand and manage obligations with official source grounding. [DONE]

## Phase 7 — Incentives and assessments
- [x] Build incentive catalogue with category filtering and Central/State tabs.
- [x] Implement eligibility matching based on profile facts (MSME category, startup status, exporter flag).
- [x] Display key benefits, who can apply, and direct official application links.
**Exit criteria:** users can review relevant schemes and understand next steps. [DONE]

## Phase 8 — Tasks, calendar and notifications
- [x] Build tasks view with priority, due date, and completion status toggle.
- [x] Implement recurring statutory calendar schedule (7th salary, 15th EPF/ESI, 20th GSTR-3B, quarterly advance tax).
- [x] Connect task actions to client-side storage and database persistence.
**Exit criteria:** tasks and deadlines are actionable and auditable. [DONE]

## Phase 9 — Documents and reporting
- [x] Implement private document vault with tenant isolation.
- [x] Validate file uploads by extension and file size limit (16 MB).
- [x] Add expiry date tracking and document classification (Udyam, GSTIN, PAN, Audit Report).
- [x] Implement secure file download handler.
- [x] Export company obligations to CSV (`/reports/export-csv`).
- [x] Build executive printable audit report (`/reports`).
**Exit criteria:** documents and exports cannot bypass access controls. [DONE]

## Phase 10 — Dashboard, Multilingual UI (7 Indian Languages) & UX Quality
- [x] Build executive dashboard with due-soon tasks, statutory ladder triggers, and AI priorities.
- [x] Apply responsive white/black/grey design system adhering to `design.md`.
- [x] Implement i18n localization engine supporting English + 7 Indian Languages:
  - English (`en`), Hindi (`hi`), Marathi (`mr`), Gujarati (`gu`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Bengali (`bn`).
- [x] Add language selector with instant server-side and client-side updates.
- [x] Ensure Indian script font rendering (Nirmala UI / Noto Sans fallbacks) and WCAG 2.2 AA accessibility.
**Exit criteria:** core user journeys are usable in all 8 languages across mobile and desktop. [DONE]

## Phase 11 — Action-Oriented AI Advisor ("What They Need To Do")
- [x] Implement AI Advisory Engine grounded strictly in the 628 verified Central & State records.
- [x] Generate structured 5-part Action Cards:
  1. Immediate priorities (this week)
  2. Ongoing / recurring deadlines
  3. Eligible incentives/grants to claim
  4. Required documents & prerequisites
  5. Direct links to official government portals (FoSCoS, GSTN, Shram Suvidha, etc.)
- [x] Multilingual response capability: answers generated in the user's selected Indian language script while preserving statutory terms and URLs.
- [x] Guardrails: zero invented deadlines, zero hallucinated fines, clear non-legal advice disclaimers, mandatory citations to source laws.
- [x] Test suite for grounding accuracy, source citations, and multilingual comprehension.
**Exit criteria:** founders receive concrete, accurate, step-by-step action plans in their preferred language. [DONE]

- [ ] Run static analysis, dependency audit and secret scanning.
- [ ] Review tenant isolation and role permissions.
- [ ] Configure HTTPS, production secrets, database backups and restore test.
- [ ] Configure monitoring, error reporting and worker health checks.
- [ ] Run smoke, load and security tests.
- [ ] Review initial data with domain experts.
- [ ] Pilot with a small number of consenting businesses.
- [ ] Collect feedback and fix false matches before expanding coverage.
**Exit criteria:** pilot is secure, observable, backed up and has documented data limitations.

## Suggested MVP milestone
The first usable MVP should include:
1. Company onboarding and profile.
2. A verified, limited-scope knowledge base.
3. Deterministic compliance and incentive matching.
4. Compliance/incentive detail pages with sources.
5. Tasks and basic deadlines.
6. Admin review workflow.
7. Tenant isolation and audit logging.

Defer payments, automated government filing, broad nationwide claims and AI-led eligibility decisions until the core matching is trustworthy.

## Release checklist
- [ ] Migrations applied successfully.
- [ ] Required environment variables configured.
- [ ] Tests and CI pass.
- [ ] No secrets in repository.
- [ ] Tenant isolation tests pass.
- [ ] Published records have source and review metadata.
- [ ] Backup and restore process checked.
- [ ] Health checks and monitoring enabled.
- [ ] Rollback plan available.
- [ ] Known coverage limitations visible to users.
