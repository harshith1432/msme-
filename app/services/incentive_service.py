"""
Incentive Discovery & Eligibility Agent.
Categorical eligibility evaluation (potentially_eligible, more_info_required, likely_ineligible, expert_review)
grounded in verified Central (78) and State (126) schemes.
"""
from app.models import Company, IncentiveScheme
from app.services.rules_engine import RulesEngine

class IncentiveEligibilityService:
    def __init__(self):
        self.rules_engine = RulesEngine()

    def evaluate_scheme(self, company_id, scheme_id):
        """
        Evaluates a specific scheme against the company's verified profile.
        Returns categorical status, reasons, supporting sources, and document requirements.
        """
        company = Company.query.get(company_id)
        if not company:
            return None, "Company not found"

        scheme = IncentiveScheme.query.get(scheme_id)
        if not scheme:
            return None, "Incentive scheme not found"

        turnover = company.get_latest_metric('turnover')
        investment = company.get_latest_metric('investment')
        employees = int(company.get_latest_metric('employees'))

        # Determine MSME class
        msme_class = "Micro"
        if investment <= 10000000 and turnover <= 50000000:
            msme_class = "Micro"
        elif investment <= 100000000 and turnover <= 500000000:
            msme_class = "Small"
        elif investment <= 500000000 and turnover <= 2500000000:
            msme_class = "Medium"
        else:
            msme_class = "Beyond MSME"

        crit = (scheme.eligibility_criteria or '').lower()
        cat = (scheme.category or '').lower()
        name = (scheme.scheme_name or '').lower()
        jurisdiction = scheme.jurisdiction

        status = 'potentially_eligible'
        match_reasons = []
        failure_reasons = []
        missing_info = []

        # 1. State / Jurisdiction check
        if scheme.jurisdiction_type != 'Central':
            if company.state.strip().lower() != jurisdiction.strip().lower():
                status = 'likely_ineligible'
                failure_reasons.append(f"Scheme is strictly restricted to enterprises registered in {jurisdiction}. Company state is {company.state}.")
            else:
                match_reasons.append(f"Enterprise premises located in eligible jurisdiction: {company.state}.")

        # 2. Beyond MSME check
        if msme_class == 'Beyond MSME' and ('msme' in crit or 'micro' in crit or 'small' in crit):
            status = 'likely_ineligible'
            failure_reasons.append(f"Enterprise metrics (Turnover: ₹{turnover:,}, Investment: ₹{investment:,}) exceed MSME ceiling.")

        # 3. Startup India / DPIIT criteria
        if 'startup' in cat or 'dpiit' in crit or 'seed fund' in name:
            if not company.is_dpiit_recognized:
                if company.incorporation_date:
                    # check age
                    today = datetime_today()
                    age = today.year - company.incorporation_date.year
                    if age <= 10 and turnover <= 1000000000:
                        status = 'more_info_required'
                        missing_info.append("DPIIT Startup Recognition certificate is required to claim this benefit.")
                    else:
                        status = 'likely_ineligible'
                        failure_reasons.append(f"Company age ({age} yrs) or turnover exceeds Startup India limits.")
                else:
                    status = 'more_info_required'
                    missing_info.append("Date of incorporation and DPIIT recognition status needed.")
            else:
                match_reasons.append("Company holds verified DPIIT Startup Recognition.")

        # 4. ZED Certification check
        if 'zed' in crit or 'zed' in name:
            if not company.is_zed_certified:
                status = 'more_info_required'
                missing_info.append("ZED (Zero Defect Zero Effect) certification required to claim subsidy.")
            else:
                match_reasons.append("Company is ZED certified.")

        # 5. Exporter check
        if 'export' in cat or 'export' in crit:
            if not company.is_exporter:
                status = 'more_info_required'
                missing_info.append("Importer Exporter Code (IEC) and active export proof required.")
            else:
                match_reasons.append("Company has active export operations.")

        # 6. Sector check
        if 'manufacturing' in crit and company.activity_type == 'Services':
            status = 'likely_ineligible'
            failure_reasons.append("Scheme is reserved exclusively for Manufacturing units.")
        elif 'manufacturing' in crit and company.activity_type == 'Manufacturing':
            match_reasons.append("Enterprise activity aligns with manufacturing criteria.")

        # Fallback to expert review if complex criteria
        if 'subject to' in crit or 'discretion' in crit or 'committee' in crit:
            if status == 'potentially_eligible':
                status = 'expert_review'
                match_reasons.append("Scheme requires departmental committee appraisal; CA/expert review recommended.")

        # General matching reason if still eligible
        if not match_reasons and not failure_reasons:
            match_reasons.append(f"General eligibility satisfied for {msme_class} enterprises in {company.state}.")

        return {
            'scheme_id': scheme.id,
            'scheme_name': scheme.scheme_name,
            'category': scheme.category,
            'jurisdiction': scheme.jurisdiction,
            'authority': scheme.ministry_agency,
            'status': status,
            'match_reasons': match_reasons,
            'failure_reasons': failure_reasons,
            'missing_info': missing_info,
            'key_benefit': scheme.key_benefit,
            'official_link': scheme.apply_link,
            'last_verified_date': scheme.last_verified_date,
            'version': scheme.version,
            'notes': scheme.status_notes
        }, None

def datetime_today():
    from datetime import date
    return date.today()
