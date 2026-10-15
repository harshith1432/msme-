"""
Deterministic Rules & Classification Engine for India MSME Platform.
Implements:
  - 1 April 2025 Revised MSME Thresholds
  - Feb 2026 DPIIT Startup Definitions (G.S.R. 108(E))
  - Four Labour Codes (w.e.f. 21 Nov 2025)
  - Statutory Employer & Turnover Ladder
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

class RulesEngine:
    def __init__(self):
        self.central_compliance = load_json('central_compliance.json')
        self.central_incentives = load_json('central_incentives.json')
        self.state_compliance = load_json('state_compliance.json')
        self.state_incentives = load_json('state_incentives.json')
        self.schema_seed = load_json('schema_seed.json')

    def classify_msme(self, investment_inr, turnover_inr):
        """
        Classifies MSME category based on 1 Apr 2025 limits:
        Micro:  Investment <= 2.5 Cr  AND Turnover <= 10 Cr
        Small:  Investment <= 25 Cr   AND Turnover <= 100 Cr
        Medium: Investment <= 125 Cr  AND Turnover <= 500 Cr
        """
        inv_cr = (investment_inr or 0) / 10000000.0
        turn_cr = (turnover_inr or 0) / 10000000.0

        if inv_cr <= 2.5 and turn_cr <= 10.0:
            return "Micro Enterprise"
        elif inv_cr <= 25.0 and turn_cr <= 100.0:
            return "Small Enterprise"
        elif inv_cr <= 125.0 and turn_cr <= 500.0:
            return "Medium Enterprise"
        else:
            return "Beyond MSME Threshold (Large / Non-MSME)"

    def check_startup_eligibility(self, age_years, turnover_inr, is_deep_tech=False):
        """
        Checks DPIIT Startup recognition eligibility based on Feb 2026 revision:
        Standard: Age <= 10 years, Turnover <= ₹200 Cr
        Deep Tech: Age <= 20 years, Turnover <= ₹300 Cr
        """
        turn_cr = (turnover_inr or 0) / 10000000.0
        age = age_years or 0

        if is_deep_tech:
            eligible = (age <= 20) and (turn_cr <= 300.0)
            reason = f"Deep Tech: age {age}/20 yrs, turnover ₹{turn_cr:.2f}/300 Cr"
        else:
            eligible = (age <= 10) and (turn_cr <= 200.0)
            reason = f"Standard: age {age}/10 yrs, turnover ₹{turn_cr:.2f}/200 Cr"
        
        return eligible, reason

    def evaluate_employer_ladder(self, employees, turnover_inr):
        """
        Evaluates statutory obligations triggered by employee count and turnover.
        """
        triggers = []
        emp = employees or 0
        turn = turnover_inr or 0

        # Employees Ladder
        if emp >= 1:
            triggers.append({
                "basis": "1+ Employees",
                "obligations": "Minimum wages, timely salary by 7th, appointment letters, equal remuneration, Shops & Establishments registration, Professional Tax deduction (where levied).",
                "source": "Code on Wages 2019; OSH Code 2020; State Acts"
            })
        if emp >= 10:
            triggers.append({
                "basis": "10+ Employees",
                "obligations": "ESI mandatory (wages <= ₹21,000/mo), Gratuity, Maternity Benefit, POSH Internal Committee mandatory.",
                "source": "Social Security Code 2020; POSH Act 2013"
            })
        if emp >= 20:
            triggers.append({
                "basis": "20+ Employees",
                "obligations": "EPF registration & contribution (12% + 12%), Statutory Annual Bonus, Grievance Redressal Committee, Factory licence if using power.",
                "source": "SS Code 2020; Code on Wages 2019; IR Code 2020; OSH Code 2020"
            })
        if emp >= 25:
            triggers.append({
                "basis": "25+ Employees",
                "obligations": "Notification of vacancies to Employment Exchange (Quarterly ER-1).",
                "source": "Employment Exchanges (CNV) Act 1959"
            })
        if emp >= 30:
            triggers.append({
                "basis": "30+ Employees",
                "obligations": "Mandatory engagement of apprentices (2.5% to 15% of workforce).",
                "source": "Apprentices Act 1961"
            })
        if emp >= 40:
            triggers.append({
                "basis": "40+ Employees",
                "obligations": "Factory licence mandatory even without power.",
                "source": "OSH Code 2020"
            })
        if emp >= 50:
            triggers.append({
                "basis": "50+ Employees",
                "obligations": "Mandatory crèche facility, contract-labour licensing threshold.",
                "source": "SS Code 2020; OSH Code 2020"
            })
        if emp >= 100:
            triggers.append({
                "basis": "100+ Employees",
                "obligations": "Works Committee, mandatory canteen facility.",
                "source": "IR Code 2020; OSH Code 2020"
            })
        if emp >= 300:
            triggers.append({
                "basis": "300+ Employees",
                "obligations": "Certified Standing Orders, prior government permission for lay-off/retrenchment/closure.",
                "source": "Industrial Relations Code 2020"
            })

        # Turnover Triggers
        if turn >= 1200000: # 12 L
            triggers.append({
                "basis": "Turnover > ₹12 Lakh (Food Businesses)",
                "obligations": "FSSAI State Licence required instead of basic registration.",
                "source": "Food Safety & Standards Act 2006"
            })
        if turn >= 2000000: # 20 L / 40 L
            triggers.append({
                "basis": "Turnover > ₹20L (Services) / ₹40L (Goods)",
                "obligations": "Mandatory GST Registration (REG-01) with Aadhaar authentication.",
                "source": "CGST Act 2017 s.22"
            })
        if turn > 10000000: # 1 Cr
            triggers.append({
                "basis": "Turnover > ₹1 Crore (₹10 Cr if cash <= 5%)",
                "obligations": "Mandatory Tax Audit (Form 3CA/3CB + 3CD, consolidated Form 26 from FY 2026-27).",
                "source": "Income-tax Act"
            })
        if turn > 50000000: # 5 Cr
            triggers.append({
                "basis": "Turnover > ₹5 Crore",
                "obligations": "Mandatory GST E-Invoicing (IRN generation on IRP) for all B2B supplies; GSTR-9C reconciliation; exit from QRMP.",
                "source": "CGST Rule 48(4)"
            })
        if turn >= 100000000: # 10 Cr
            triggers.append({
                "basis": "Turnover >= ₹10 Crore",
                "obligations": "Invoices must be reported on IRP within 30 days of invoice date.",
                "source": "GSTN Advisory"
            })

        return triggers

    def evaluate_company(self, profile):
        """
        Full evaluation of a company profile against all central & state records.
        profile: {
            "name": str,
            "state": str,
            "sector": str,
            "entity_type": str,
            "turnover": int,
            "investment": int,
            "employees": int,
            "age_years": int,
            "is_dpiit": bool,
            "is_deep_tech": bool,
            "is_exporter": bool
        }
        """
        emp = profile.get("employees", 0)
        turnover = profile.get("turnover", 0)
        inv = profile.get("investment", 0)
        state = profile.get("state", "Karnataka")
        sector = profile.get("sector", "Manufacturing")
        age = profile.get("age_years", 3)
        is_deep_tech = profile.get("is_deep_tech", False)

        msme_class = self.classify_msme(inv, turnover)
        is_startup, startup_reason = self.check_startup_eligibility(age, turnover, is_deep_tech)
        ladder = self.evaluate_employer_ladder(emp, turnover)

        # Match Central Compliances
        matched_cc = []
        for item in self.central_compliance:
            domain = item.get("Domain", "")
            applies = False
            reason = ""

            # Registration rules
            if domain == "Registration":
                applies = True
                reason = "General corporate or establishment requirement."
            # GST rules
            elif domain == "GST":
                if turnover >= 2000000 or item.get("ID") in ["CC-012", "CC-013", "CC-014", "CC-020"]:
                    applies = True
                    reason = f"Applicable based on turnover ₹{turnover:,} or GST threshold."
                if item.get("ID") in ["CC-017", "CC-018"] and turnover >= 50000000:
                    applies = True
                    reason = "Turnover exceeds ₹5 Crore e-invoicing threshold."
            # Income Tax rules
            elif domain == "Income Tax":
                applies = True
                if item.get("ID") == "CC-024":
                    applies = (turnover >= 10000000)
                    reason = "Turnover exceeds tax audit limit."
                else:
                    reason = "Statutory income tax compliance."
            # Labour rules
            elif domain == "Labour":
                if "10+" in item.get("Applies to / trigger", ""):
                    applies = (emp >= 10)
                    reason = f"Triggered because headcount ({emp}) >= 10."
                elif "20+" in item.get("Applies to / trigger", ""):
                    applies = (emp >= 20)
                    reason = f"Triggered because headcount ({emp}) >= 20."
                elif "25+" in item.get("Applies to / trigger", ""):
                    applies = (emp >= 25)
                    reason = f"Triggered because headcount ({emp}) >= 25."
                elif "30+" in item.get("Applies to / trigger", ""):
                    applies = (emp >= 30)
                    reason = f"Triggered because headcount ({emp}) >= 30."
                elif "50+" in item.get("Applies to / trigger", ""):
                    applies = (emp >= 50)
                    reason = f"Triggered because headcount ({emp}) >= 50."
                elif "100+" in item.get("Applies to / trigger", ""):
                    applies = (emp >= 100)
                    reason = f"Triggered because headcount ({emp}) >= 100."
                elif "300+" in item.get("Applies to / trigger", ""):
                    applies = (emp >= 300)
                    reason = f"Triggered because headcount ({emp}) >= 300."
                else:
                    applies = True
                    reason = "Universal labour code requirement under Code on Wages & OSH Code."
            # Product / Food
            elif domain == "Product":
                if "FSSAI" in item.get("Requirement", ""):
                    applies = ("Food" in sector)
                    reason = "Food processing / food business sector obligation."
                else:
                    applies = (sector == "Manufacturing")
                    reason = "Product manufacturing standard."
            else:
                applies = True
                reason = "Applicable statutory framework."

            if applies:
                matched_cc.append({**item, "match_reason": reason})

        # Match State Compliances for this state
        matched_sc = [item for item in self.state_compliance if item.get("State / UT", "").lower() == state.lower()]

        # Match Central Incentives
        matched_ci = []
        for item in self.central_incentives:
            cat = item.get("Category", "")
            applies = False
            reason = ""

            if cat == "Credit & Guarantee":
                applies = True
                reason = "Eligible for MSME credit guarantee / collateral-free lending."
            elif cat == "Startup & Innovation":
                applies = is_startup
                reason = f"Matches Startup India criteria ({startup_reason})."
            elif cat == "Export":
                applies = profile.get("is_exporter", False)
                reason = "Export promotion mission assistance for active exporters."
            elif cat == "Technology & Quality":
                applies = True
                reason = "Eligible for ZED certification / LEAN / RAMP quality subsidies."
            elif cat == "Sector-specific":
                if "Food" in item.get("Scheme", "") and "Food" in sector:
                    applies = True
                    reason = "Sector-specific food processing incentives."
                elif "Electronics" in item.get("Scheme", "") and "IT" in sector:
                    applies = True
                    reason = "Electronics / IT sector incentive."
                else:
                    applies = False
            else:
                applies = True
                reason = "Applicable central MSME assistance scheme."

            if applies:
                matched_ci.append({**item, "match_reason": reason})

        # Match State Incentives
        matched_si = [item for item in self.state_incentives if item.get("State / UT", "").lower() == state.lower()]

        return {
            "msme_classification": msme_class,
            "is_startup_eligible": is_startup,
            "startup_reason": startup_reason,
            "statutory_ladder": ladder,
            "matched_central_compliance_count": len(matched_cc),
            "matched_central_compliance": matched_cc,
            "matched_state_compliance_count": len(matched_sc),
            "matched_state_compliance": matched_sc,
            "matched_central_incentives_count": len(matched_ci),
            "matched_central_incentives": matched_ci,
            "matched_state_incentives_count": len(matched_si),
            "matched_state_incentives": matched_si,
            "total_obligations": len(matched_cc) + len(matched_sc),
            "total_incentives": len(matched_ci) + len(matched_si)
        }
