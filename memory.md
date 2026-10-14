# Project Memory — MSME Navigator

This file records durable project decisions for contributors and future development sessions. Update it when decisions change.

## Product identity
Working name: **MSME Compliance & Incentive Intelligence Platform** (also referred to as MSME Navigator).

One-line promise:
“Know what your business must comply with, discover what government benefits you may qualify for, and manage everything in one place.”

## Problem
Indian MSMEs often need to search across central, state and local government sources to understand obligations and discover support schemes. Information can be fragmented, difficult to interpret and change over time.

## Product approach
- Build a personalised navigator, not merely a searchable spreadsheet.
- Match recommendations to company profile, size, location, sector, activities, workforce and relevant thresholds.
- Show why each result matches and link to authoritative evidence.
- Provide tasks, reminders and document preparation support.
- Keep deterministic rules separate from AI explanations.
- Never guarantee scheme approval or declare legal compliance based only on automated matching.

## Source workbook & Seed Dataset
Initial seed dataset: `India MSME Compliance & Incentives Navigator – Central + all 28 States & 8 UTs` (v1.0, 4 Oct 2026).
Confirmed counts:
- Central Compliance: 94 records (CC-001 to CC-094)
- Central Incentives: 78 records (CI-001 to CI-078)
- State Compliance: 330 records across 36 States/UTs (SC-001 to SC-330)
- State Incentives: 126 records across 36 States/UTs (SI-001 to SI-126)
- Total: 628 records + Statutory Employer & Turnover Threshold Ladders.

Key 2025–2026 Legal Benchmarks:
- MSME investment & turnover limits revised w.e.f. 1 April 2025 (Micro: ≤₹2.5 cr / ≤₹10 cr; Small: ≤₹25 cr / ≤₹100 cr; Medium: ≤₹125 cr / ≤₹500 cr).
- DPIIT Startup definition updated Feb 2026 via G.S.R. 108(E): ₹200 cr turnover cap (10 yrs) and Deep Tech category with ₹300 cr turnover cap (20 yrs).
- Four Labour Codes in force w.e.f. 21 Nov 2025 (Wages, OSH, Social Security, Industrial Relations).
- Income-tax Act 2025 in force 1 April 2026.
- GST 2.0 rationalised slabs w.e.f. 22 Sept 2025 (5%, 18%).

## Multilingual Support
Full pan-India coverage in **English + 7 Indian languages**:
1. English (`en`)
2. Hindi (`hi`) — हिन्दी
3. Marathi (`mr`) — मराठी
4. Gujarati (`gu`) — ગુજરાતી
5. Tamil (`ta`) — தமிழ்
6. Telugu (`te`) — తెలుగు
7. Kannada (`kn`) — ಕನ್ನಡ
8. Bengali (`bn`) — বাংলা

## Action-Oriented AI ("What They Need To Do")
The platform features an embedded AI assistant that provides concrete, 5-part action plans:
1. Immediate Priorities (This Week)
2. Periodic / Recurring Deadlines
3. Claimable Incentives & Subsidies
4. Required Documentation Checklist
5. Direct Links to Official Government Portals (e.g. FoSCoS, Shram Suvidha, GSTN, NSWS)
All AI answers are strictly grounded in verified records and official citations, preventing hallucinated deadlines.

## Target customers
Initial candidate users:
- Micro and small business owners across Tier-I, II, and III cities.
- Small and medium businesses with operational/compliance staff.
- Chartered accountants and compliance consultants who manage multiple companies.

## Technology preferences
- Backend: Python + Flask.
- Database: PostgreSQL for deployment; SQLite acceptable for local tests.
- Frontend: HTML, Bootstrap 5 and vanilla JavaScript; i18n client dictionary loader.
- Background jobs: Celery + Redis where needed.
- UI preference: professional white/black/grey palette, Inter or Plus Jakarta Sans, responsive layout, restrained components.

## Core modules
1. Authentication and tenant membership.
2. Company onboarding and profile.
3. Compliance knowledge base and rules.
4. Compliance evaluation and obligation tracker.
5. Incentive catalogue and eligibility assessments.
6. Calendar, tasks and reminders.
7. Document metadata and secure vault.
8. Reports and exports.
9. Admin source registry and review workflow.
10. Audit logging.
11. Multilingual Action-Oriented AI Advisor.
12. 7-Language Internationalization (i18n).

## Working rules for contributors
Read `prd.md`, `architecture.md`, `design.md`, `rules.md`, `tasks.md`, and `PROJECT_MASTER_PLAN.md` before implementing features. Update this file when product scope, architecture or critical constraints change. Never record credentials, API keys, real company secrets or production personal data here.

