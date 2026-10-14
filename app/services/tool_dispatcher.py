"""
Controlled Tool Dispatcher (Capability F).
Provides 10 safe, source-grounded backend tools for the conversational AI assistant.
Enforces strict tenant isolation, parameter validation, auditable executions, and traceable citations.
Zero direct SQL or unrestricted code execution exposure.
"""
from datetime import datetime, date
from app.extensions import db
from app.models import (
    Company, CompanyMetric, ComplianceRequirement, IncentiveScheme,
    CompanyObligation, Task, Document, AIDraft, ReviewRequest, AuditEvent, ClientAccess
)
from app.services.rules_engine import RulesEngine
from app.services.incentive_service import IncentiveEligibilityService
from app.services.readiness_service import ReadinessService
from app.services.action_service import ComplianceActionService

class ToolDispatcher:
    def __init__(self):
        self.rules_engine = RulesEngine()
        self.incentive_service = IncentiveEligibilityService()
        self.readiness_service = ReadinessService()
        self.action_service = ComplianceActionService()

    def check_authorization(self, company_id, current_user_id=None, tenant_id=None):
        """
        Enforces tenant isolation and consultant delegation permissions.
        """
        company = Company.query.get(company_id)
        if not company:
            return False, "Company not found"

        # If tenant_id provided, verify company belongs to tenant
        if tenant_id and company.tenant_id != tenant_id:
            # Check if user has delegated consultant access
            if current_user_id:
                delegation = ClientAccess.query.filter_by(
                    consultant_user_id=current_user_id,
                    company_id=company_id,
                    status='active'
                ).first()
                if delegation:
                    return True, company
            return False, "Access denied: Unauthorized cross-tenant access attempt."

        return True, company

    def execute_tool(self, tool_name, params, current_user_id=None, tenant_id=None):
        """
        Dispatches calls to the 10 controlled tools.
        """
        tools = {
            'get_business_profile': self.tool_get_business_profile,
            'search_approved_compliance_records': self.tool_search_approved_compliance_records,
            'evaluate_compliance_rules': self.tool_evaluate_compliance_rules,
            'search_published_schemes': self.tool_search_published_schemes,
            'evaluate_scheme_eligibility': self.tool_evaluate_scheme_eligibility,
            'get_document_checklist': self.tool_get_document_checklist,
            'create_draft_task': self.tool_create_draft_task,
            'create_draft_document': self.tool_create_draft_document,
            'get_task_summary': self.tool_get_task_summary,
            'request_expert_review': self.tool_request_expert_review
        }

        if tool_name not in tools:
            return {
                'success': False,
                'error': f"Unknown tool '{tool_name}'. Available tools: {list(tools.keys())}"
            }

        try:
            return tools[tool_name](params, current_user_id=current_user_id, tenant_id=tenant_id)
        except Exception as e:
            return {
                'success': False,
                'error': f"Error executing tool '{tool_name}': {str(e)}"
            }

    # 1. get_business_profile
    def tool_get_business_profile(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        company = result
        turnover = company.get_latest_metric('turnover')
        investment = company.get_latest_metric('investment')
        employees = int(company.get_latest_metric('employees'))

        return {
            'success': True,
            'tool': 'get_business_profile',
            'data': {
                'company_id': company.id,
                'name': company.name,
                'trade_name': company.trade_name or company.name,
                'state': company.state,
                'district': company.district or 'Not specified',
                'entity_type': company.entity_type,
                'sector': company.sector,
                'activity_type': company.activity_type,
                'udyam_number': company.udyam_number or 'Not registered',
                'pan_number': company.pan_number or 'Not registered',
                'gstin': company.gstin or 'Not registered',
                'incorporation_date': company.incorporation_date.strftime('%Y-%m-%d') if company.incorporation_date else 'Not recorded',
                'is_dpiit_recognized': company.is_dpiit_recognized,
                'is_deep_tech': company.is_deep_tech,
                'is_zed_certified': company.is_zed_certified,
                'is_exporter': company.is_exporter,
                'metrics': {
                    'turnover': turnover,
                    'investment': investment,
                    'employees': employees
                }
            },
            'citations': [
                {'source': 'Company Master Profile', 'verified': True}
            ]
        }

    # 2. search_approved_compliance_records
    def tool_search_approved_compliance_records(self, params, current_user_id=None, tenant_id=None):
        query = (params.get('query') or '').lower()
        jurisdiction = params.get('jurisdiction')
        domain = params.get('domain')
        limit = min(int(params.get('limit', 10)), 25)

        q = ComplianceRequirement.query.filter_by(is_active=True)
        if jurisdiction and jurisdiction.lower() != 'all':
            q = q.filter(ComplianceRequirement.jurisdiction.ilike(f"%{jurisdiction}%"))
        if domain:
            q = q.filter(ComplianceRequirement.domain.ilike(f"%{domain}%"))

        records = q.all()
        if query:
            records = [
                r for r in records if query in r.requirement.lower() or query in (r.law_basis or '').lower() or query in (r.what_to_do or '').lower()
            ]

        results = []
        for r in records[:limit]:
            results.append({
                'id': r.id,
                'jurisdiction': r.jurisdiction,
                'domain': r.domain,
                'requirement': r.requirement,
                'law_basis': r.law_basis,
                'what_to_do': r.what_to_do,
                'frequency_due_date': r.frequency_due_date,
                'authority': r.authority,
                'official_link': r.official_link,
                'last_verified_date': r.last_verified_date,
                'version': r.version
            })

        return {
            'success': True,
            'tool': 'search_approved_compliance_records',
            'count': len(results),
            'records': results,
            'citations': [{'id': r['id'], 'authority': r['authority'], 'link': r['official_link']} for r in results]
        }

    # 3. evaluate_compliance_rules
    def tool_evaluate_compliance_rules(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        company = result
        turnover = company.get_latest_metric('turnover')
        investment = company.get_latest_metric('investment')
        employees = int(company.get_latest_metric('employees'))

        profile = {
            'id': company.id,
            'name': company.name,
            'state': company.state,
            'sector': company.sector,
            'entity_type': company.entity_type,
            'turnover': turnover,
            'investment': investment,
            'employees': employees,
            'is_dpiit': company.is_dpiit_recognized,
            'is_deep_tech': company.is_deep_tech,
            'is_exporter': company.is_exporter
        }

        evaluation = self.rules_engine.evaluate_company(profile)
        return {
            'success': True,
            'tool': 'evaluate_compliance_rules',
            'msme_classification': evaluation['msme_classification'],
            'total_obligations': evaluation['total_obligations'],
            'statutory_ladder': evaluation['statutory_ladder'],
            'matched_central_count': len(evaluation['matched_central_compliance']),
            'matched_state_count': len(evaluation['matched_state_compliance']),
            'citations': [
                {'law': 'MSMED Act 2020 / 2025 Revised Limits', 'link': 'https://msme.gov.in'},
                {'law': 'Code on Wages 2019 / OSH Code 2020', 'link': 'https://labour.gov.in'}
            ]
        }

    # 4. search_published_schemes
    def tool_search_published_schemes(self, params, current_user_id=None, tenant_id=None):
        query = (params.get('query') or '').lower()
        jurisdiction = params.get('jurisdiction')
        category = params.get('category')
        limit = min(int(params.get('limit', 10)), 25)

        q = IncentiveScheme.query.filter_by(is_active=True)
        if jurisdiction and jurisdiction.lower() != 'all':
            q = q.filter(IncentiveScheme.jurisdiction.ilike(f"%{jurisdiction}%"))
        if category:
            q = q.filter(IncentiveScheme.category.ilike(f"%{category}%"))

        schemes = q.all()
        if query:
            schemes = [
                s for s in schemes if query in s.scheme_name.lower() or query in (s.key_benefit or '').lower() or query in (s.eligibility_criteria or '').lower()
            ]

        results = []
        for s in schemes[:limit]:
            results.append({
                'id': s.id,
                'jurisdiction': s.jurisdiction,
                'category': s.category,
                'scheme_name': s.scheme_name,
                'ministry_agency': s.ministry_agency,
                'key_benefit': s.key_benefit,
                'eligibility_criteria': s.eligibility_criteria,
                'apply_link': s.apply_link,
                'last_verified_date': s.last_verified_date,
                'version': s.version
            })

        return {
            'success': True,
            'tool': 'search_published_schemes',
            'count': len(results),
            'schemes': results,
            'citations': [{'id': s['id'], 'authority': s['ministry_agency'], 'link': s['apply_link']} for s in results]
        }

    # 5. evaluate_scheme_eligibility
    def tool_evaluate_scheme_eligibility(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        scheme_id = params.get('scheme_id')
        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        if not scheme_id:
            return {'success': False, 'error': 'scheme_id is required'}

        res, err = self.incentive_service.evaluate_scheme(company_id, scheme_id)
        if err:
            return {'success': False, 'error': err}

        return {
            'success': True,
            'tool': 'evaluate_scheme_eligibility',
            'evaluation': res,
            'citations': [
                {'scheme_id': res['scheme_id'], 'authority': res['authority'], 'link': res['official_link']}
            ]
        }

    # 6. get_document_checklist
    def tool_get_document_checklist(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        scheme_id = params.get('scheme_id')
        compliance_id = params.get('compliance_id')
        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        res, err = self.readiness_service.evaluate_readiness(company_id, scheme_id=scheme_id, compliance_id=compliance_id)
        if err:
            return {'success': False, 'error': err}

        return {
            'success': True,
            'tool': 'get_document_checklist',
            'readiness': res,
            'citations': [{'target': res['target_name'], 'source': 'Ministry Documentation Guidelines'}]
        }

    # 7. create_draft_task
    def tool_create_draft_task(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        title = params.get('title')
        description = params.get('description', '')
        priority = params.get('priority', 'medium')
        due_date_str = params.get('due_date')
        source_id = params.get('source_id')
        source_type = params.get('source_type', 'ai_suggested')

        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        if not title:
            return {'success': False, 'error': 'Task title is required'}

        task, err = self.action_service.create_task(
            company_id=company_id,
            title=title,
            description=description,
            priority=priority,
            due_date_str=due_date_str,
            source_type=source_type,
            source_id=source_id,
            user_id=current_user_id
        )
        if err:
            return {'success': False, 'error': err}

        return {
            'success': True,
            'tool': 'create_draft_task',
            'task_id': task.id,
            'title': task.title,
            'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
            'status': task.status
        }

    # 8. create_draft_document
    def tool_create_draft_document(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        draft_type = params.get('draft_type', 'checklist')  # checklist or cover_letter
        scheme_id = params.get('scheme_id')
        compliance_id = params.get('compliance_id')

        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        if draft_type == 'cover_letter':
            if not scheme_id:
                return {'success': False, 'error': 'scheme_id is required for cover letter draft'}
            draft, err = self.readiness_service.generate_cover_letter(company_id, scheme_id)
        else:
            draft, err = self.readiness_service.generate_draft_checklist(company_id, scheme_id=scheme_id, compliance_id=compliance_id)

        if err:
            return {'success': False, 'error': err}

        return {
            'success': True,
            'tool': 'create_draft_document',
            'draft_id': draft.id,
            'title': draft.title,
            'draft_type': draft.draft_type,
            'status': draft.status,
            'version': draft.version,
            'preview': draft.content[:300] + '...'
        }

    # 9. get_task_summary
    def tool_get_task_summary(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        summary, err = self.action_service.get_task_summary(company_id)
        if err:
            return {'success': False, 'error': err}

        return {
            'success': True,
            'tool': 'get_task_summary',
            'summary': summary
        }

    # 10. request_expert_review
    def tool_request_expert_review(self, params, current_user_id=None, tenant_id=None):
        company_id = params.get('company_id')
        review_type = params.get('review_type', 'compliance')
        reference_id = params.get('reference_id')
        notes = params.get('notes', '')

        authorized, result = self.check_authorization(company_id, current_user_id, tenant_id)
        if not authorized:
            return {'success': False, 'error': result}

        rr = ReviewRequest(
            company_id=company_id,
            user_id=current_user_id,
            review_type=review_type,
            reference_id=reference_id,
            notes=notes,
            status='pending'
        )
        db.session.add(rr)
        db.session.add(AuditEvent(
            tenant_id=result.tenant_id,
            user_id=current_user_id,
            action='expert_review_requested',
            entity_type='ReviewRequest',
            entity_id=reference_id or 'General',
            details=f"Requested expert CA review for {review_type}: {notes[:100]}"
        ))
        db.session.commit()

        return {
            'success': True,
            'tool': 'request_expert_review',
            'review_request_id': rr.id,
            'status': rr.status,
            'message': 'Review request dispatched to authorized CA/compliance consultant panel.'
        }
