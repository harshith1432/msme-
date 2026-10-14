"""
Compliance Action Assistant Service (Capability E).
Converts evaluated obligations and schemes into actionable tasks using deterministic due dates.
Refuses to invent dates when event context is unknown.
Provides summaries for pending, upcoming, and overdue obligations.
"""
from datetime import datetime, date, timedelta
from calendar import monthrange
from app.extensions import db
from app.models import Company, Task, CompanyObligation, ComplianceRequirement, IncentiveScheme, AuditEvent

class ComplianceActionService:
    def __init__(self):
        pass

    def calculate_deterministic_due_date(self, frequency_str, base_date=None):
        """
        Calculates statutory due date deterministically.
        Returns (due_date, is_event_triggered, clarification_needed).
        """
        if not base_date:
            base_date = date.today()

        freq = (frequency_str or '').lower()

        # Monthly rules
        if '15th' in freq or 'monthly' in freq and 'epf' in freq or 'esi' in freq:
            # 15th of next month
            next_month = base_date.month + 1 if base_date.month < 12 else 1
            year = base_date.year if base_date.month < 12 else base_date.year + 1
            return date(year, next_month, 15), False, None

        if '20th' in freq or 'gstr-3b' in freq:
            # 20th of next month
            next_month = base_date.month + 1 if base_date.month < 12 else 1
            year = base_date.year if base_date.month < 12 else base_date.year + 1
            return date(year, next_month, 20), False, None

        if '7th' in freq or 'wage' in freq:
            next_month = base_date.month + 1 if base_date.month < 12 else 1
            year = base_date.year if base_date.month < 12 else base_date.year + 1
            return date(year, next_month, 7), False, None

        # Quarterly rules
        if 'quarterly' in freq or 'advance tax' in freq:
            # Next advance tax date: 15 Jun, 15 Sep, 15 Dec, 15 Mar
            deadlines = [
                date(base_date.year, 3, 15),
                date(base_date.year, 6, 15),
                date(base_date.year, 9, 15),
                date(base_date.year, 12, 15),
                date(base_date.year + 1, 3, 15)
            ]
            for dl in deadlines:
                if dl > base_date:
                    return dl, False, None

        # Annual rules
        if 'annual' in freq or '30 sep' in freq or 'roc' in freq:
            sept_30 = date(base_date.year, 9, 30)
            if sept_30 > base_date:
                return sept_30, False, None
            return date(base_date.year + 1, 9, 30), False, None

        # Event-triggered (Section 43B(h), incident reporting, factory notice)
        if 'within' in freq or 'days' in freq or 'event' in freq or '45' in freq:
            return None, True, "Due date depends on invoice/event date. Please provide the invoice receipt or occurrence date."

        # Default fallback: 30 days from today
        return base_date + timedelta(days=30), False, None

    def suggest_tasks_from_obligations(self, company_id):
        """
        Evaluates company obligations and proposes actionable tasks with deterministic dates.
        Does NOT automatically insert without user confirmation.
        """
        company = Company.query.get(company_id)
        if not company:
            return [], "Company not found"

        obligations = CompanyObligation.query.filter_by(company_id=company.id).all()
        existing_task_sources = set(
            t.source_id for t in Task.query.filter_by(company_id=company.id).all() if t.source_id
        )

        suggested = []
        for ob in obligations:
            req = ob.compliance
            if not req or req.id in existing_task_sources:
                continue

            due_date, is_event, note = self.calculate_deterministic_due_date(req.frequency_due_date)

            suggested.append({
                'source_id': req.id,
                'source_type': 'compliance',
                'title': f"Comply with: {req.requirement[:60]}",
                'description': f"{req.what_to_do or req.requirement}\nLaw Basis: {req.law_basis or 'Statutory'}\nAuthority: {req.authority or 'Regulatory Dept'}",
                'priority': 'high' if 'mandatory' in (req.what_to_do or '').lower() or 'licence' in (req.requirement or '').lower() else 'medium',
                'due_date': due_date.strftime('%Y-%m-%d') if due_date else None,
                'is_event_triggered': is_event,
                'clarification_needed': note,
                'official_link': req.official_link
            })

        return suggested, None

    def create_task(self, company_id, title, description, priority='medium', due_date_str=None, source_type='manual', source_id=None, user_id=None):
        """
        Creates and persists a confirmed task.
        """
        company = Company.query.get(company_id)
        if not company:
            return None, "Company not found"

        due_date = None
        if due_date_str:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    due_date = datetime.strptime(due_date_str, fmt).date()
                    break
                except ValueError:
                    pass

        task = Task(
            company_id=company.id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            source_type=source_type,
            source_id=source_id,
            status='todo'
        )
        db.session.add(task)
        db.session.add(AuditEvent(
            tenant_id=company.tenant_id,
            user_id=user_id,
            action='task_created',
            entity_type='Task',
            entity_id=title,
            details=f"Created task linked to {source_type} ({source_id or 'ad-hoc'})"
        ))
        db.session.commit()
        return task, None

    def get_task_summary(self, company_id):
        """
        Returns structured summary: pending, upcoming (next 30 days), and overdue tasks.
        """
        company = Company.query.get(company_id)
        if not company:
            return None, "Company not found"

        today = date.today()
        tasks = Task.query.filter_by(company_id=company.id).all()

        pending = []
        upcoming = []
        overdue = []
        completed = []

        for t in tasks:
            item = {
                'id': t.id,
                'title': t.title,
                'priority': t.priority,
                'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else 'No fixed deadline',
                'source_type': t.source_type,
                'source_id': t.source_id,
                'status': t.status
            }
            if t.status == 'completed':
                completed.append(item)
            elif t.due_date and t.due_date < today:
                overdue.append(item)
            elif t.due_date and t.due_date <= today + timedelta(days=30):
                upcoming.append(item)
            else:
                pending.append(item)

        return {
            'total_tasks': len(tasks),
            'pending_count': len(pending),
            'upcoming_count': len(upcoming),
            'overdue_count': len(overdue),
            'completed_count': len(completed),
            'pending': pending,
            'upcoming': upcoming,
            'overdue': overdue,
            'completed': completed
        }, None
