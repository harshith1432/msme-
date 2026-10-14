# MSME Compliance & Incentive Intelligence Platform — Architecture

## 1. Purpose
A multi-tenant SaaS platform that helps Indian MSMEs discover applicable compliance obligations, understand government incentives, manage deadlines and maintain an auditable record of actions.

The platform is guidance and workflow software. It must not claim that a business is legally compliant or guaranteed to receive a grant solely because a rule-matching engine produced a result.

## 2. MVP architecture principles
- Start with a modular monolith; do not introduce microservices until real operational needs justify them.
- Keep deterministic eligibility/compliance rules separate from AI-generated explanations.
- Treat official source evidence, effective dates and verification status as first-class data.
- Use tenant isolation and least-privilege access from the first release.
- Make all important rule and record changes auditable.
- Prefer official government sources and clearly expose source links to users.
- Build for Indian date formats, INR, Indian states/UTs, and English first; design for future Kannada, Hindi and other languages.

## 3. Recommended stack
- Frontend: HTML, Bootstrap, vanilla JavaScript.
- Backend: Python, Flask, Flask-SQLAlchemy / SQLAlchemy.
- Database: PostgreSQL in deployed environments; SQLite may be used for local development and tests.
- Background jobs: Celery with Redis for reminders, scheduled source checks and imports.
- File storage: private object storage in production; local storage only for development.
- Authentication: secure session-based authentication initially; email verification and password reset.
- Deployment: Linux VPS or managed hosting, Nginx reverse proxy, HTTPS, environment-based configuration.
- Testing: pytest, Flask test client, database fixtures, security checks and migration tests.
- Optional later: PostgreSQL full-text search, pgvector or another retrieval layer for source-grounded AI answers.

## 4. Logical components
1. Web UI
   - Public landing page and plan information.
   - Authentication and onboarding.
   - Company dashboard.
   - Compliance catalogue and detail pages.
   - Incentive catalogue and eligibility assessments.
   - Calendar, tasks, documents, notifications and reports.
   - Tenant administration and platform administration.
2. Flask application modules
   - `auth`: signup, login, logout, email verification, password reset.
   - `tenants`: organisations, memberships, invitations and roles.
   - `companies`: company profile, locations, activities and MSME profile.
   - `knowledge`: source registry, compliance records, schemes, versions and review workflow.
   - `rules`: versioned deterministic rule evaluation.
   - `compliance`: company-specific obligations, statuses, evidence and due dates.
   - `incentives`: scheme discovery, eligibility assessment and saved schemes.
   - `calendar`: deadlines, reminders and recurring obligations.
   - `documents`: private document metadata and controlled access.
   - `notifications`: in-app and email notifications.
   - `reports`: exports and summary reports.
   - `audit`: append-oriented audit events.
   - `billing`: plan and subscription abstractions; payment integration can be deferred.
3. Background workers
   - Reminder dispatch.
   - Scheduled source review reminders.
   - Workbook import and validation.
   - Rule re-evaluation after approved changes.
   - Retry and delivery tracking for notifications.
4. Data layer
   - PostgreSQL as source of truth.
   - Redis for job queue/cache/rate limiting only; never the sole source of important business records.
   - Private file storage for uploaded documents.

## 5. High-level request flow
1. User signs in and selects an authorised company.
2. API loads the company profile and current approved rule/scheme versions.
3. Rule engine evaluates structured conditions using known company facts.
4. Results are stored with the rule version, evaluation time and explanation inputs.
5. UI displays applicable, potentially applicable, not applicable, and needs-review outcomes.
6. User marks tasks as in progress or complete and may attach evidence.
7. Background worker sends reminders according to preferences.
8. Audit events record important changes.

## 6. Core data entities
- `User`: identity, email, password hash, verification state, account status.
- `Tenant`: organisation/workspace and plan.
- `Membership`: user, tenant, role, status.
- `Company`: tenant-owned legal/business profile and primary location.
- `CompanyLocation`: additional plants/offices and jurisdiction.
- `CompanyActivity`: sector, activities and licences relevant to applicability.
- `CompanyMetric`: dated turnover, investment, employee count and source of value.
- `Source`: official URL, publisher, title, source type, last checked date, reviewer.
- `ComplianceRequirement`: stable identity and descriptive metadata.
- `ComplianceVersion`: jurisdiction, conditions, effective dates, source references, status.
- `IncentiveScheme`: stable scheme identity.
- `IncentiveVersion`: benefits, eligibility, exclusions, application process, effective dates, sources.
- `Rule`: structured condition set and version.
- `Evaluation`: company, rule version, result, explanation, timestamp and input snapshot.
- `CompanyObligation`: company-specific requirement, due date, status, assigned user.
- `SchemeAssessment`: company, scheme version, outcome, unmet criteria and timestamp.
- `Task`: actionable work item linked to obligation or scheme.
- `Document`: metadata, storage key, classification, access policy and expiry.
- `Notification`: recipient, channel, status and delivery timestamps.
- `AuditEvent`: actor, tenant, action, entity, timestamp and safe change summary.
- `ReviewQueueItem`: records awaiting verification or update.
- `Subscription`: plan, status and billing references, when billing is enabled.

## 7. Tenant isolation and security
- Every tenant-owned record must have a tenant identifier or an unambiguous ownership relationship.
- Derive tenant access from authenticated membership; never trust a tenant ID supplied by the browser without authorisation.
- Centralise tenant-scoped query helpers and test cross-tenant access explicitly.
- Apply role-based permissions on every protected endpoint, not only by hiding UI controls.
- Store password hashes using a modern password hashing implementation supported by the framework.
- Protect state-changing requests against CSRF.
- Use secure, HttpOnly, SameSite cookies; enable Secure in HTTPS environments.
- Rate-limit login, OTP, password reset and public endpoints.
- Validate uploads, limit size, prevent path traversal, and keep private files outside public web roots.
- Never commit secrets or production data; use environment variables or a secret manager.
- Redact passwords, tokens, sensitive document contents and personal data from logs.
- Establish retention, export and deletion policies aligned with applicable law.
- Use backups and test restoration.

## 8. Rule engine design
Rules should be structured data, not executable Python or arbitrary user-provided code.
Supported operators in the MVP may include `equals`, `not_equals`, `in`, `not_in`, `gt`, `gte`, `lt`, `lte`, `all`, `any`, and `exists`.
- Validate every rule schema before publication.
- Store effective-from and effective-to dates.
- Store source references and reviewer approval.
- Return an outcome plus a human-readable explanation and missing facts.
- Unknown or missing company facts must result in `needs_review` or `insufficient_data`, not an assumed pass.
- Preserve the exact rule version used for each evaluation.
- Support re-evaluation when company facts or approved rules change.

## 9. AI and retrieval
AI is optional for the first MVP. When added:
- Retrieve only approved, current source material relevant to the question.
- Cite sources in every substantive answer.
- Distinguish facts from interpretation and indicate when evidence is insufficient.
- Do not allow retrieved documents to issue instructions to the model or override platform policy.
- Never let an LLM make the final deterministic eligibility decision.
- Do not send confidential company documents to external AI services without an explicit product policy and user disclosure.
- Record model/provider, prompt version and source references where appropriate.

## 10. Deployment and observability
- Separate development, staging and production configuration.
- Use database migrations for all schema changes.
- Add health checks, structured logs, error tracking and metrics.
- Monitor request latency, error rate, worker queue depth, notification failures and database connections.
- Use connection pooling and backups appropriate to the chosen hosting environment.
- Run dependency and static security checks in CI.
- Deploy with a rollback plan and smoke tests.

## 11. Initial release boundaries
Included: company profile, central and selected state records, deterministic matching, incentive assessments, task/deadline tracking, admin review, source provenance and audit trail.
Deferred: automatic government filing, guaranteed eligibility, payments, full nationwide legal coverage, native mobile apps, complex ERP integrations and autonomous AI actions.
