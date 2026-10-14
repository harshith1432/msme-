# Product Design System and UX Specification

## 1. Product experience
The product should feel like a trustworthy business operations tool, not a government portal clone. Users should quickly answer:
1. What requires my attention?
2. Which obligations apply to my business?
3. Which incentives may be relevant?
4. What should I do next, and what evidence supports this recommendation?

## 2. Visual direction
- Palette: white, black and neutral greys; avoid a blue-heavy theme.
- Typography: Inter or Plus Jakarta Sans, with system fallbacks.
- Style: restrained, professional, clean spacing, clear hierarchy and accessible contrast.
- Support light and dark themes where practical.
- Avoid oversized buttons, excessive gradients, decorative charts and crowded cards.
- Use colour only as a secondary status cue; never communicate status by colour alone.
- Responsive design: mobile-first layouts for onboarding, tasks and alerts; desktop layouts for tables and administration.

## 3. Navigation
Primary navigation:
- Overview
- Compliance
- Incentives
- Calendar & Tasks
- Documents
- Reports
- Company Profile
- Settings

Platform administrators additionally see:
- Knowledge Base
- Compliance Rules
- Incentive Schemes
- Source Registry
- Review Queue
- Users & Tenants
- Audit Logs
- System Health

## 4. Onboarding flow
Use a progressive wizard with save-and-resume:
1. Business identity: legal/trade name, legal structure, incorporation date.
2. Location: state, district, registered office and additional operating locations.
3. Business activity: sector, sub-sector, manufacturing/service/trading, activities and licences.
4. Size and metrics: annual turnover, investment in plant/equipment, employee count, financial year and date of measurement.
5. Existing registrations: Udyam, GSTIN and other identifiers only when needed; clearly explain why each is requested.
6. Review: confirm values, show missing facts and explain that results are preliminary until verified.

Ask only for data needed for matching. Avoid collecting highly sensitive identifiers unless there is a clear requirement and appropriate protection.

## 5. Dashboard layout
Top area:
- Company selector (for users with multiple companies).
- Last profile update and data freshness.
- Primary action: “Review recommendations”.

Summary cards:
- Actions due soon.
- Overdue tasks.
- Applicable requirements.
- Incentive schemes to explore.

Main sections:
- Next 30 days: deadlines and tasks.
- Recommended incentives: eligibility status and next action.
- Recent regulatory updates: only updates relevant to the company and backed by a reviewed source.
- Profile gaps: missing information affecting matching.

Do not display a “compliance score” unless its calculation is transparent, defensible and clearly labelled as a tracking indicator rather than legal certification.

## 6. Compliance catalogue and detail page
Filters:
- Jurisdiction: central, state, district/local where supported.
- Topic: tax, labour, environment, safety, registrations, sector-specific.
- Applicability status.
- Frequency and due date.
- Source verification status.

Each record should show:
- Requirement title and plain-language summary.
- Why it may apply to this company.
- Applicability outcome and missing facts.
- Responsible authority and jurisdiction.
- Frequency, deadline logic and renewal information where verified.
- Required actions/documents.
- Official source link and source checked date.
- Effective date and review status.
- “Mark in progress”, “Mark complete” and “Request review” actions.

A completion action means the user has marked it complete; it is not independent proof of legal compliance.

## 7. Incentive catalogue and detail page
Each scheme card:
- Scheme name and administering body.
- Benefit type: grant, subsidy, loan, guarantee, reimbursement, tax benefit or non-financial support.
- Relevant eligibility status.
- State/sector scope.
- Application window, if verified.
- “Why it matches” and “What is missing”.
- Official source and application link.

Scheme details:
- Benefit and calculation basis, with caveats.
- Eligibility criteria and exclusions.
- Documents and preparation checklist.
- Application steps and responsible authority.
- Application link, source date and effective period.
- Clear notice that final approval rests with the scheme authority.

Never combine loans and grants into a single “free money” amount. Do not estimate a monetary benefit unless the formula and required inputs are sourced.

## 8. Calendar, tasks and notifications
- Views: list and month calendar.
- Filters by company, due date, category, assignee and status.
- Reminders configurable by users and tenant administrators.
- Avoid duplicate reminders and support quiet hours.
- Track sent, failed and retried notifications.
- Provide an in-app notification centre as the source of truth.
- Use explicit time zone handling; default to Asia/Kolkata for Indian company profiles.

## 9. Accessibility and content
- Meet WCAG 2.2 AA as a target.
- Keyboard navigation, visible focus, semantic headings and labels.
- Form errors explain how to fix the issue.
- Use plain English and define legal acronyms.
- Provide multilingual-ready translation keys rather than hard-coded interface text.
- Dates should be unambiguous; currency should use INR formatting.
- Every legal or scheme claim should link to evidence.

## 10. Key states
Design empty, loading, partial-data, error, stale-source and needs-review states.
Examples:
- “We need your employee count to assess this requirement.”
- “Potential match — one eligibility condition still needs confirmation.”
- “Source review is overdue. Confirm this requirement before relying on it.”
- “No matching schemes found in the current verified dataset. This does not prove that no scheme exists.”

## 11. Design acceptance criteria
- Users can finish onboarding on mobile.
- Main dashboard clearly separates compliance obligations from incentive opportunities.
- Every recommendation has an explanation and source.
- Status labels are not colour-only.
- No page implies a guaranteed grant, legal opinion or verified compliance without supporting evidence.
- Tables work on narrow screens through responsive cards or controlled horizontal scrolling.
