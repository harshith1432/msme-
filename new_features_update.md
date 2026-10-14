# MSME Compliance & Incentive Intelligence Platform --- New Feature Update

## Purpose

Use this document as an implementation brief for updating the existing
India MSME Compliance & Incentive Intelligence Platform.

The goal is to improve the current software into a trustworthy,
practical, secure, and commercially viable compliance and
government-incentive intelligence product for Indian MSMEs, accountants,
compliance consultants, and business advisors.

**This is an additive feature specification, not a phase-based
roadmap.** Inspect the existing repository and implement the features in
a way that fits the current architecture. Do not rebuild the project
from scratch, replace the technology stack, or redesign working screens
unnecessarily.

## Instructions for the AI coding tool

Before making changes:

1.  Inspect the repository, existing documentation, database models,
    routes/controllers, templates/components, authentication,
    authorization, tests, and deployment configuration.
2.  Identify which requested features already exist, which are partially
    implemented, and which are missing.
3.  Reuse and extend existing patterns where practical. Avoid duplicate
    modules, duplicate database tables, and parallel implementations of
    the same capability.
4.  Update the existing project documentation, database migrations,
    tests, navigation, and permissions alongside the implementation.
5.  Preserve the current technology stack and established UI design
    unless a change is required for functionality, security,
    accessibility, or consistency.
6.  Do not remove existing features or change existing behavior without
    a clear technical reason.
7.  Implement features end-to-end: UI, backend logic, validation,
    persistence, authorization, error handling, auditability, and tests.
8.  Do not fabricate legal requirements, scheme rules, government URLs,
    eligibility criteria, benefit amounts, or deadlines. Mark missing
    information clearly and require verification.
9.  Do not claim a feature is complete unless it is implemented and
    tested. Report blockers and unfinished integrations honestly.
10. If a requested capability requires a third-party API or paid
    service, create a clean integration boundary and configuration
    documentation. Do not hard-code secrets or pretend the integration
    is live.

## Product principles

-   **Profile-driven:** Results should depend on the user's business
    profile and the relevant jurisdiction.
-   **Source-grounded:** Every regulatory obligation and incentive
    should have traceable supporting information.
-   **Explainable:** Users should understand why a result applies, what
    information is missing, and what action to take.
-   **Human-reviewed:** High-impact regulatory changes and uncertain
    interpretations must support expert review before publication.
-   **Secure by default:** Business records and documents must be
    isolated and accessible only to authorized users.
-   **Action-oriented:** Turn results into tasks, reminders, document
    requests, and reports.
-   **Accessible:** Responsive layouts, readable language, useful empty
    states, and clear error messages.
-   **Maintainable:** Use modular services, migrations, typed/validated
    inputs where supported, tests, and documented configuration.

------------------------------------------------------------------------

## 1. Business Profile and Eligibility Intelligence

Create or improve a structured business profile containing relevant
fields, where applicable:

-   Legal/business name and business type.
-   State and district; registered and operating locations where
    relevant.
-   Industry, sector, and activity.
-   Incorporation/registration date and relevant registration
    identifiers.
-   Udyam/MSME registration status and classification details.
-   Investment in plant and machinery or equipment, where relevant.
-   Annual turnover and the financial year to which it relates.
-   Employee count, where relevant.
-   Ownership/category attributes only when required by a specific
    scheme and voluntarily/appropriately supplied.
-   Export activity, manufacturing/service status, and other
    scheme-specific criteria.
-   Profile data source, last-updated date, and verification status for
    important fields.

Requirements:

-   Use the applicable official MSME classification criteria and retain
    the effective date/source of the criteria.
-   Do not infer that every profile field is mandatory for every
    business.
-   Ask only for data needed for the relevant matching decision.
-   Allow users to update their profile and see which recommendations
    may change.
-   Track relevant profile changes in the audit trail.
-   Clearly distinguish user-provided, imported, and verified
    information.

## 2. Personalized Compliance Engine

Provide a rules-based engine that matches a business profile to
potentially applicable compliance obligations.

Each compliance record should support fields such as:

-   Name and plain-language description.
-   Jurisdiction: central, state, local, or other applicable level.
-   Applicable state/district, industry, entity type, and business
    conditions.
-   Triggering conditions and exclusions.
-   Frequency and due-date logic, when officially established.
-   Effective-from and effective-to dates.
-   Responsible role or suggested owner.
-   Penalties/consequences only where supported by reliable official
    information.
-   Official source URL, issuing authority, source title, and relevant
    reference.
-   Last verified date, review status, and version.
-   Reviewer notes and publication status.

For each matched obligation, show:

-   Why it matched the business.
-   Which profile fields triggered the match.
-   Any missing or unverified information.
-   Required action and due date, if reliably determined.
-   The official source and its last verification date.
-   A clear status such as applicable, potentially applicable, requires
    review, or not enough information.

Do not label a business legally compliant solely because its tasks are
marked complete. Explain that the platform supports compliance
management and does not replace professional legal or tax advice.

## 3. Government Incentive and Scheme Matching

Create a scheme discovery and eligibility module covering relevant
central and state government incentives, subject to data verification.

Support scheme types such as subsidies, grants, reimbursements,
credit-support schemes, tax-related benefits, export support, training
support, and other verified business assistance.

Each scheme should support:

-   Scheme name, issuing authority, and jurisdiction.
-   Official scheme page and application portal URL.
-   Objective, benefit type, and eligible applicant types.
-   Eligibility conditions, exclusions, and required evidence.
-   Benefit amount or calculation method only when supported by an
    official source.
-   Application opening/closing dates where confirmed.
-   Required documents and application steps.
-   Applicable sectors, locations, business sizes, and other conditions.
-   Effective dates, source verification date, version, and publication
    status.
-   Contact/help information when available from a reliable source.

Show match outcomes with clear explanations:

-   **Potentially eligible:** available profile data appears to satisfy
    known criteria.
-   **More information required:** one or more required facts are
    missing or unverified.
-   **Likely not eligible:** a known criterion is not met, with the
    reason shown.
-   **Expert review recommended:** criteria are ambiguous or require
    interpretation.

Never guarantee approval, payment, savings, or eligibility. Link users
to official sources and make it clear that the competent authority makes
the final decision.

## 4. Regulatory Data Management and Verification

Build an admin workspace for maintaining the quality of compliance and
incentive data.

Include:

-   Create, edit, review, approve, publish, archive, and supersede
    records.
-   Draft and published states with role-based permissions.
-   Required source URL and verification metadata for publishable
    records.
-   Reviewer identity, review timestamp, notes, and change reason.
-   Version history and comparison of changes.
-   Effective-date handling so future rules do not incorrectly apply
    early.
-   Expiry/review reminders for records that may become stale.
-   Duplicate detection and missing-field validation.
-   Filters by jurisdiction, authority, topic, status, verification
    date, and owner.
-   Import/export tools with validation, preview, and error reporting.
-   A queue for records requiring verification.

If the existing Excel workbook is used as a source, preserve its useful
data, validate it during import, and flag incomplete or unverified
entries. Do not silently mark imported records as verified.

## 5. Regulatory Change Intelligence

Add a traceable workflow for identifying and processing official
regulatory updates.

Where permitted and technically practical:

-   Monitor configured official government pages, notifications,
    circulars, and scheme portals.
-   Record the source, retrieval time, publication date if available,
    and captured change summary.
-   Compare new source content with the last reviewed version.
-   Suggest which compliance records, incentives, jurisdictions, or
    business profiles may be affected.
-   Create a review task for an authorized domain expert.
-   Require human approval before a material change becomes an active
    rule.
-   Notify affected customers only after the update has been reviewed
    and approved.
-   Keep a history of detected, reviewed, approved, rejected, and
    published changes.

Do not bypass website access controls or assume that every website
permits automated retrieval. Use official APIs or permitted methods
where available. If reliable monitoring is unavailable, support manual
source submission and review.

## 6. Compliance Calendar, Tasks, and Notifications

Provide an actionable workspace for compliance obligations and incentive
application tasks.

Include:

-   Calendar and list views.
-   Upcoming, due today, overdue, completed, and cancelled statuses.
-   One-time and recurring tasks where recurrence is supported by
    verified rules.
-   Task owner, collaborators, priority, notes, and evidence
    attachments.
-   Reminder configuration and notification history.
-   Email notifications and optional WhatsApp/SMS integrations through
    configured providers.
-   Retry/error logging for failed notifications.
-   Escalations and digest summaries where configured.
-   Task completion evidence, completion timestamp, and completing user.
-   Filters by business, jurisdiction, owner, category, and date range.

Avoid generating guessed deadlines. If the date depends on a business
event, financial year, or other missing input, display the dependency
and ask for the necessary information.

## 7. Document and Evidence Management

Create secure document handling for compliance evidence and scheme
applications.

Include:

-   Uploads associated with a business, task, compliance record, or
    incentive application.
-   Document type, description, upload date, owner, and optional expiry
    date.
-   Access controls based on tenant and user permissions.
-   File type and size validation; safe storage; secure download
    authorization.
-   Malware scanning integration point where available.
-   Versioning or replacement history for important evidence.
-   Expiry reminders for documents with confirmed expiry dates.
-   A checklist of required documents for a scheme or task.
-   Audit logs for uploads, downloads, replacements, and deletions where
    appropriate.

Do not expose private documents through guessable public URLs. Keep
sensitive identifiers and document contents out of ordinary application
logs.

## 8. CA and Consultant Multi-Client Workspace

Support accountants, consultants, and compliance service providers who
manage multiple businesses.

Include:

-   A client/business portfolio view.
-   Client invitations and explicit access grants.
-   Per-client roles and permissions.
-   Consolidated deadline and task views.
-   Client-specific compliance and incentive reports.
-   Document requests and status tracking.
-   Assignment of tasks to authorized staff.
-   Client activity history and audit trail.
-   Subscription or usage limits that can be configured by plan.

A consultant must not gain access to a business merely by knowing its
name or identifier. Access must be granted and revocable by an
authorized business user or administrator.

## 9. Reports and Exports

Provide useful, traceable reports, such as:

-   Business compliance overview.
-   Upcoming and overdue obligations.
-   Completed tasks and attached evidence.
-   Potential incentive opportunities with eligibility explanations.
-   Missing information and required documents.
-   Regulatory data verification and update history for administrators.
-   Client portfolio report for authorized consultants.

Support PDF and spreadsheet exports where appropriate. Include the
generation date, business scope, filters, and source references. Respect
access permissions and avoid including data the requesting user cannot
view.

## 10. AI Assistant and Document Intelligence

Add AI features only with clear boundaries and source traceability.

The assistant may:

-   Explain a verified compliance record in plain language.
-   Summarize an official circular or scheme document.
-   Answer questions using approved platform records and retrieved
    source material.
-   Explain why a compliance obligation or scheme was matched.
-   Extract candidate fields from uploaded documents for user review.
-   Draft checklists and task descriptions from verified requirements.
-   Cite the underlying source records and show when they were last
    verified.

The assistant must:

-   Distinguish sourced facts from generated explanations.
-   Say when evidence is missing or conflicting.
-   Avoid inventing rules, dates, benefit values, application links, or
    legal interpretations.
-   Never silently modify published regulatory rules.
-   Never mark a business compliant, approve a scheme application, or
    submit an application without an explicit authorized workflow.
-   Require user confirmation for extracted or inferred data before
    saving it to the business profile.
-   Respect tenant access controls, document permissions, retention
    rules, and privacy requirements.
-   Avoid sending confidential business documents to external AI
    providers unless the integration is explicitly configured and the
    data-handling implications are disclosed.

## 11. Subscriptions, Billing, and Product Administration

Where payment functionality is in scope, provide:

-   Configurable plans and entitlements.
-   Trial and subscription status.
-   Payment-provider integration behind a service boundary.
-   Verified webhook handling, signature validation, idempotency, and
    event logs.
-   Invoice/receipt records and subscription history.
-   Upgrade, downgrade, cancellation, and payment-failure flows.
-   Admin controls for plans, limits, and customer support.
-   Usage metrics for features subject to limits.

Never store raw card details. Do not trust client-side payment status;
verify payment state using the payment provider's signed server-side
events or API.

## 12. Security, Privacy, and Reliability

Review and strengthen the whole application.

-   Tenant isolation enforced server-side for every business-scoped
    query and operation.
-   Role-based access control and least-privilege defaults.
-   Secure password and session handling, appropriate MFA support where
    feasible, and secure account recovery.
-   CSRF, XSS, SQL injection, SSRF, insecure file upload, and
    access-control protections appropriate to the stack.
-   Encryption in transit and appropriate protection for sensitive
    stored data.
-   Secrets only in environment/secret management, never committed to
    source control.
-   Rate limiting, request validation, safe error handling, and security
    headers.
-   Audit logs for security-sensitive and regulatory-data actions.
-   Automated backups and a documented restore test.
-   Monitoring for errors, failed jobs, notification failures, and
    unusual access.
-   Dependency and vulnerability scanning in CI where supported.
-   Retention, deletion, and export workflows aligned with applicable
    privacy obligations.
-   Production-safe migrations and rollback guidance.

Do not log passwords, access tokens, payment secrets, or full sensitive
document contents. Ensure logs themselves have access controls and
retention policies.

## 13. User Experience and Accessibility

Improve the existing interface without unnecessary redesign.

-   Responsive desktop, tablet, and mobile layouts.
-   Consistent navigation, typography, spacing, form validation, and
    status labels.
-   Clear first-use onboarding and profile completion indicators.
-   Search, filtering, sorting, and pagination for large lists.
-   Helpful loading, empty, error, and success states.
-   Accessible labels, keyboard navigation, focus states, and sufficient
    contrast.
-   Plain-language explanations and a glossary for regulatory
    terminology.
-   Localization support where useful, while retaining official legal
    terms and source links.
-   Avoid unsupported badges, alarming warnings, or claims of guaranteed
    savings.

## 14. Analytics and Product Insights

Provide actionable analytics for users and administrators without
exposing other tenants' data.

Business-level metrics may include:

-   Upcoming and overdue tasks.
-   Completion trends.
-   Missing profile data that prevents matching.
-   Potential incentive opportunities by status.
-   Document readiness for selected applications.

Platform-level metrics may include:

-   Active businesses and user engagement.
-   Trial-to-paid conversion and subscription retention.
-   Most-used modules and common search topics.
-   Data records awaiting verification and stale records.
-   Match accuracy from reviewed samples.
-   Notification delivery and system error rates.

Clearly define each metric, its time window, and calculation. Do not
label a potential incentive amount as guaranteed savings or confirmed
revenue.

## 15. Architecture and Engineering Requirements

Adapt these requirements to the existing stack rather than introducing
unnecessary technology.

-   Keep business logic separate from route/controller and presentation
    layers.
-   Keep eligibility and compliance matching in testable service
    modules.
-   Store rule conditions in a structured, validated format; do not use
    arbitrary executable code from database records.
-   Use database migrations for schema changes.
-   Add appropriate indexes and pagination for growing datasets.
-   Use background jobs for slow monitoring, document processing,
    exports, and notifications where needed.
-   Make background jobs idempotent and observable.
-   Use caching only where invalidation and data freshness are defined.
-   Enforce tenant and permission checks at the backend, not only in the
    UI.
-   Provide API validation, consistent error responses, and versioning
    where external APIs exist.
-   Maintain environment-specific configuration and setup documentation.
-   Include automated tests for eligibility rules, tenant isolation,
    permissions, date handling, imports, notifications, and payment
    webhook processing where applicable.

## 16. Acceptance Criteria

Treat a feature as complete only when the applicable criteria below are
met:

1.  Authorized users can use the feature through the interface and
    backend.
2.  Data persists correctly and survives a restart.
3.  Input validation and useful error handling are implemented.
4.  Unauthorized users cannot access or modify the data by changing a
    URL, ID, request body, or API call.
5.  Regulatory matches and incentive recommendations show their
    reasoning and source references.
6.  Unverified or incomplete data is visibly identified.
7.  Effective dates and rule versions are handled correctly.
8.  Database changes are delivered through migrations.
9.  Automated tests cover normal cases, edge cases, and relevant
    security cases.
10. Documentation and environment variables are updated.
11. No credentials or sensitive customer data are committed to the
    repository.
12. The existing application continues to run and existing working
    functionality is not unintentionally broken.

## 17. Required Deliverables from the AI Coding Tool

After inspecting and updating the repository, provide:

-   A short audit of existing versus missing features.
-   A list of files changed and new files created.
-   Database schema/migration summary.
-   Backend routes/services and UI screens updated.
-   Configuration variables and third-party services required.
-   Tests added and their actual results.
-   Security and tenant-isolation checks performed.
-   Any features left incomplete and the reason.
-   Exact local setup, migration, test, and run commands.
-   Any regulatory records that still require expert verification.

Do not return only a proposal or mockup. Make the changes in the
existing project where tool access permits. If repository access is
unavailable, provide an implementation plan and clearly state that no
repository files were changed.

------------------------------------------------------------------------

## Final instruction

Implement the requested improvements as one coherent product update,
integrated with the current codebase and existing documentation. First
inspect what already exists, then implement missing capabilities without
duplicating working features. Prioritize correctness, explainability,
source verification, tenant isolation, and maintainability over adding
superficial features. Do not invent regulatory data, claim unimplemented
functionality, or perform a wholesale redesign unless the current
architecture genuinely requires it.
