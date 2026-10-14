# Product Requirements Document (PRD)
## MSME Compliance & Incentive Intelligence Platform

**Status:** Draft for MVP planning  
**Audience:** Product, engineering, design, QA and domain reviewers

## 1. Vision
Provide Indian MSMEs with one trusted place to understand potentially applicable compliance requirements, discover relevant government incentives and organise the actions needed to pursue them.

## 2. Problem statement
Business owners may not know which central, state or local requirements apply to their business. Incentive information is distributed across multiple portals and notifications. The cost of searching, interpreting and tracking this information can be high, especially for small organisations without dedicated compliance teams.

## 3. Goals
- Create a structured, reviewable knowledge base from the existing workbook.
- Personalise results using company facts and versioned rules.
- Explain why a compliance item or scheme may apply.
- Link each material recommendation to an official source.
- Track obligations, tasks, deadlines and user-entered completion evidence.
- Let authorised administrators review and publish changes.
- Provide a secure multi-tenant foundation.

## 4. Non-goals for MVP
- Automatically file forms or make payments on government portals.
- Guarantee legal compliance, eligibility, sanction or disbursement.
- Replace a qualified CA, lawyer or compliance professional.
- Cover every law, district, sector and scheme in India at launch.
- Use AI as the sole source of legal or eligibility decisions.
- Native iOS/Android applications.
- Complex ERP integrations or autonomous agents.
- Billing/payment collection before the core value is validated.

## 5. Personas
### A. MSME owner
Needs clear priorities, simple explanations, reminders and access to schemes without learning regulatory jargon.

### B. Operations/compliance employee
Needs an assigned task list, deadlines, documents, status history and reports.

### C. CA or consultant
Needs to manage multiple client profiles, identify missing information and review recommendations efficiently.

### D. Knowledge administrator/reviewer
Needs to import records, verify official sources, edit rule versions, approve changes and maintain an audit trail.

### E. Platform administrator
Needs tenant/user management, roles, system configuration, security visibility and support tools.

## 6. Core user journeys
### Journey 1: First-time company onboarding
1. User verifies email and creates a workspace.
2. User creates a company profile.
3. User enters location, sector, legal structure, turnover, investment, employee count and relevant activities.
4. System identifies missing facts and explains their impact.
5. User reviews the profile and requests an initial assessment.
6. Dashboard displays results with source and verification labels.

### Journey 2: Understand a compliance obligation
1. User opens Compliance.
2. Filters by applicable, upcoming or overdue.
3. Opens a record.
4. Reads why it may apply, the action required, authority, deadline logic and source.
5. Assigns a task or marks it in progress.
6. Marks it complete and optionally attaches evidence.
7. System records the action and audit event.

### Journey 3: Discover an incentive
1. User opens Incentives.
2. System ranks potential matches based on explicit criteria.
3. User opens a scheme and reviews benefits, exclusions, documents and application steps.
4. User completes missing eligibility questions.
5. System labels the result as likely match, potential match, not matched or needs review.
6. User saves the scheme and creates preparation tasks.

### Journey 4: Administrator updates a rule
1. Admin imports or edits a draft record.
2. Required source, effective date and conditions are validated.
3. Reviewer checks evidence and compares changes.
4. Approved version is published.
5. Affected company evaluations are queued for re-evaluation.
6. Audit log records who changed and approved the record.

## 7. Functional requirements
### FR-01 Authentication
- Email-based registration, verification, login, logout and password reset.
- Secure password hashing, session security, CSRF protection and rate limiting.
- Account status and session invalidation for disabled users.

### FR-02 Tenant and roles
- Users can belong to one or more workspaces.
- Roles are enforced server-side.
- Initial roles: Owner, Admin, Compliance Manager, Contributor, Viewer, Knowledge Reviewer and Platform Admin.
- Knowledge-review roles are separate from company-tenant roles.

### FR-03 Company profile
- Support legal name, trade name, legal structure, incorporation date, state, district, locations, sector, activities, employee count, turnover, investment and financial-year reference.
- Store metric period/date and whether the value is user-entered or verified.
- Allow profile updates and re-evaluation.
- Collect only data required for a clear purpose.

### FR-04 Knowledge base
- Store compliance requirements, incentive schemes, source records and versions.
- Support central/state jurisdiction, category, sector, effective dates, last-checked date, verification status and official links.
- Import workbook rows into a staging area before publication.
- Detect duplicate candidates and missing mandatory fields.

### FR-05 Rule evaluation
- Evaluate structured, validated rules against company facts.
- Return applicable, potentially applicable, not applicable, insufficient data or needs review.
- Include rule version, timestamp, matched conditions, unmet conditions and source links.
- Unknown values must not silently pass.
- Re-evaluate when relevant profile facts or approved rules change.

### FR-06 Compliance workspace
- Show company-specific obligations.
- Support statuses: New, To Do, In Progress, Awaiting External Action, Completed by User, Needs Review and Not Applicable (reviewed).
- Support due dates only when source/rule supports them.
- Support task assignment, notes and optional evidence.
- Keep status history.

### FR-07 Incentive discovery
- Search and filter by sector, jurisdiction, benefit type, company size and status.
- Display eligibility criteria, exclusions, benefit type, official source and application portal.
- Save schemes and create preparation tasks.
- Never represent a preliminary match as an approval.

### FR-08 Calendar and reminders
- Display upcoming and overdue tasks.
- Allow user-controlled reminder preferences.
- Send notifications through a background queue.
- Track delivery state and avoid duplicate messages.
- Support Asia/Kolkata as a default, while storing timestamps consistently.

### FR-09 Document management
- Store document metadata and private file references.
- Restrict access by tenant and role.
- Validate file type and size.
- Support expiry reminders where dates are supplied.
- Avoid public, guessable document URLs.

### FR-10 Admin review workflow
- Draft → In Review → Approved → Published → Retired.
- Capture reviewer, timestamps, notes, source evidence and version.
- Prevent unreviewed draft rules from affecting production assessments.
- Provide a queue for stale and incomplete records.

### FR-11 Audit
- Record authentication/security events and material business changes.
- Include actor, tenant, action, target entity, timestamp and safe change summary.
- Restrict audit-log access and prevent ordinary users from editing entries.

### FR-12 Reporting
- Export company obligations and task statuses.
- Produce scheme shortlist and assessment reports.
- Clearly show report generation date, data freshness and limitations.
- Use appropriate access checks for all exports.

### FR-13 Action-Oriented AI Assistant ("What to Do")
- Provide concrete, step-by-step action plans tailored to the business profile (headcount, turnover, sector, location).
- Answer what they need to do, where to file, and which documents are required.
- Ground all answers strictly in approved Central (94) and State (330) compliance records and incentive schemes.
- Respond in the user's selected language (English + 7 Indian languages).
- Cite official statutory sources and link directly to government portals.
- Never invent a legal deadline, fine amount, or grant eligibility result.
- Explicit non-legal advice disclaimer and transparent uncertainty handling.

## 8. Non-functional requirements
- Security: least privilege, tenant isolation, CSRF protection, secure cookies, rate limits, upload validation, dependency scanning and secret management.
- Privacy: data minimisation, clear purpose, retention controls, deletion/export processes and appropriate consent/notices.
- Reliability: database backups, migrations, health checks and tested restore process.
- Performance: paginate lists; avoid unbounded queries; index tenant, status, jurisdiction and due-date fields.
- Accessibility: target WCAG 2.2 AA with full support for Indian Unicode scripts.
- Maintainability: modular Flask blueprints, service layer, schemas/validation and automated tests.
- Traceability: recommendations can be reproduced from profile snapshot + rule/scheme version.
- Internationalisation (i18n): full support for **English + 7 Indian Languages**:
  - English (`en`), Hindi (`hi`), Marathi (`mr`), Gujarati (`gu`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Bengali (`bn`).
  - Centralised interface locale bundles, regional date/currency (INR, Lakh, Crore), and multilingual AI prompt engineering.

## 9. MVP success metrics
- Percentage of onboarding sessions completed.
- Time from profile completion to first useful recommendation.
- Percentage of recommendations with valid source and review metadata.
- Rate of false-positive/false-negative findings from domain review.
- Weekly active companies and repeat use.
- Task completion and reminder engagement.
- Number of source records verified and freshness compliance.
- User-reported usefulness and trust.
Do not optimise only for number of recommendations; accuracy and explainability matter more.

## 10. Acceptance criteria
- A user can create and update a company profile.
- A company can see only its own authorised data.
- Compliance and incentive results show evidence and data freshness.
- Unknown data yields an uncertainty status.
- Draft or expired rule versions cannot silently act as current approved rules.
- Tasks and reminders are idempotent and auditable.
- Admin publishing requires the configured review permission.
- Tests cover cross-tenant access, role enforcement, rule edge cases and outdated sources.
- No screen guarantees a scheme approval or legal compliance.

## 11. Risks and mitigations
- Stale government information: source registry, review dates, change workflow and visible stale labels.
- Incorrect matching: deterministic versioned rules, domain review and uncertainty states.
- Incomplete coverage: explicitly label geographic/sector scope and dataset coverage.
- AI hallucination: retrieval from approved sources, citations, evaluation tests and non-AI rule decisions.
- Sensitive documents: private storage, access checks, retention policy and logging redaction.
- Overly broad MVP: start with a controlled pilot and expand based on measured quality.

## 12. Decisions needed before implementation
- Initial target persona and pilot geography.
- Initial industries and exact record coverage.
- Email/notification provider.
- Hosting and file-storage choices.
- Whether expert assistance is part of the initial business model.
- AI launch timing.
- Pricing and billing scope.
