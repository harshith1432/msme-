"""
Full dataset generation script for India MSME Compliance & Incentives Navigator.
Generates:
  - central_compliance.json (94 records)
  - central_incentives.json (78 records)
  - state_compliance.json (330 records)
  - state_incentives.json (126 records)
  - aggregator_portals.json (10 records)
"""
import os
import json
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 1. CENTRAL COMPLIANCE
cc_path = os.path.join(DATA_DIR, 'raw_central_compliance.csv')
central_compliance = []
if os.path.exists(cc_path):
    with open(cc_path, 'r', encoding='utf-8') as f:
        lines = [l for l in f if not l.strip().startswith('#') and l.strip()]
        for row in csv.DictReader(lines):
            if row.get('ID'):
                central_compliance.append(row)

with open(os.path.join(DATA_DIR, 'central_compliance.json'), 'w', encoding='utf-8') as f:
    json.dump(central_compliance, f, indent=2, ensure_ascii=False)

# 2. CENTRAL INCENTIVES
ci_path = os.path.join(DATA_DIR, 'raw_central_incentives.csv')
central_incentives = []
if os.path.exists(ci_path):
    with open(ci_path, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('ID'):
                central_incentives.append(row)

with open(os.path.join(DATA_DIR, 'central_incentives.json'), 'w', encoding='utf-8') as f:
    json.dump(central_incentives, f, indent=2, ensure_ascii=False)

# 3. STATE COMPLIANCE GENERATOR (330 records across 28 States & 8 UTs)
states_meta = [
    ("Andhra Pradesh", "State", "AP Single Desk Portal", "https://www.apindustries.gov.in", "https://appcb.ap.gov.in", True, True, None),
    ("Arunachal Pradesh", "State", "Single-window via NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Assam", "State", "EoDB Assam Single Window", "https://easeofdoingbusinessinassam.in", "https://pcbassam.org", True, False, None),
    ("Bihar", "State", "Bihar Single Window Clearance", "https://www.nsws.gov.in", "https://bspcb.bihar.gov.in", True, False, None),
    ("Chhattisgarh", "State", "Chhattisgarh Industries single window", "https://industries.cg.gov.in", "https://enviscecb.org", False, True, None),
    ("Goa", "State", "Goa Investment Promotion Board", "https://goaipb.goa.gov.in", "https://goaspcb.gov.in", False, True, None),
    ("Gujarat", "State", "Investor Facilitation Portal (IFP)", "https://ifp.gujarat.gov.in", "https://gpcb.gujarat.gov.in", True, True, None),
    ("Haryana", "State", "Haryana Enterprise Promotion Centre (Invest Haryana)", "https://investharyana.in", "https://hspcb.org.in", False, True, "Haryana State Employment of Local Candidates Act 2020 was struck down by the Punjab & Haryana High Court; check status of appeal"),
    ("Himachal Pradesh", "State", "Emerging Himachal / HP single window", "https://emerginghimachal.hp.gov.in", "https://hppcb.nic.in", False, False, None),
    ("Jharkhand", "State", "Jharkhand Single Window", "https://jharkhandindustry.gov.in", "https://jspcb.nic.in", True, False, None),
    ("Karnataka", "State", "Karnataka Udyog Mitra / eBiz single window", "https://ebiz.karnataka.gov.in", "https://kspcb.karnataka.gov.in", True, True, "Karnataka Industries (Facilitation) Act – MSMEs can start on an acknowledgement and get approvals within 3 years (verify current rules)"),
    ("Kerala", "State", "K-SWIFT", "https://kswift.kerala.gov.in", "https://keralapcb.nic.in", True, True, "Kerala MSME Facilitation Act 2019 – start on self-declaration; approvals within 3 years"),
    ("Madhya Pradesh", "State", "Invest MP single window", "https://invest.mp.gov.in", "https://mppcb.mp.gov.in", True, True, None),
    ("Maharashtra", "State", "MAITRI", "https://maitri.mahaonline.gov.in", "https://mpcb.gov.in", True, True, None),
    ("Manipur", "State", "Single-window via NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Meghalaya", "State", "Meghalaya single window via NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Mizoram", "State", "Single-window via NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Nagaland", "State", "Single-window via NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Odisha", "State", "GO-SWIFT (Invest Odisha)", "https://investodisha.gov.in", "https://ospcboard.org", True, True, None),
    ("Punjab", "State", "Invest Punjab – Business First", "https://investpunjab.gov.in", "https://ppcb.punjab.gov.in", True, True, "Punjab Right to Business Act 2020 – in-principle approval for MSMEs in approved zones (verify)"),
    ("Rajasthan", "State", "Rajasthan Single Window Clearance System", "https://swcs.rajasthan.gov.in", "https://environment.rajasthan.gov.in", False, False, "Rajasthan MSME (Facilitation of Establishment & Operation) Act 2019 – start on acknowledgement; approvals within 3 years"),
    ("Sikkim", "State", "Single-window via NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Tamil Nadu", "State", "TN Single Window Portal", "https://tnswp.com", "https://tnpcb.gov.in", True, True, None),
    ("Telangana", "State", "TS-iPASS", "https://ipass.telangana.gov.in", "https://tspcb.cgg.gov.in", True, True, None),
    ("Tripura", "State", "Single-window via NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Uttar Pradesh", "State", "Nivesh Mitra", "https://niveshmitra.up.nic.in", "https://uppcb.up.gov.in", False, False, "UP MSME (Facilitation) Act – 1,000-day exemption from certain approvals (verify)"),
    ("Uttarakhand", "State", "Invest Uttarakhand single window", "https://investuttarakhand.uk.gov.in", "https://ueppcb.uk.gov.in", False, False, None),
    ("West Bengal", "State", "Silpa Sathi", "https://silpasathi.wb.gov.in", "https://wbpcb.gov.in", True, True, None),
    ("Andaman & Nicobar Islands", "UT", "UT administration / NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Chandigarh", "UT", "Chandigarh single window / NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, True, None),
    ("Dadra & Nagar Haveli and Daman & Diu", "UT", "UT single window / NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Delhi (NCT)", "UT", "Delhi Industries Dept / NSWS", "https://www.nsws.gov.in", "https://dpcc.delhigovt.nic.in", False, True, None),
    ("Jammu & Kashmir", "UT", "J&K Single Window", "https://singlewindow.jk.gov.in", "https://jkspcb.nic.in", False, False, None),
    ("Ladakh", "UT", "UT administration / NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Lakshadweep", "UT", "UT administration / NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Puducherry", "UT", "Puducherry single window / NSWS", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None)
]

state_compliance = []
sc_idx = 1

for state_name, stype, portal_name, portal_url, pcb_url, pt_levied, lwf_app, facilitation_note in states_meta:
    # 1. Approvals
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Approvals",
        "Requirement": f"Single-window approvals portal – {portal_name}",
        "Law / basis": "State single-window / EoDB acts",
        "Applies to / trigger": "All new and existing units",
        "What to do": "Apply for state approvals, renewals and incentives online",
        "Portal / link": portal_url,
        "Notes": "",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 2. Shops & Establishments
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Labour",
        "Requirement": "Shops & Establishments registration",
        "Law / basis": f"{state_name} Shops & Establishments law",
        "Applies to / trigger": "Shops, offices, commercial establishments (threshold varies)",
        "What to do": "Register/intimate via state labour dept or single window",
        "Portal / link": portal_url,
        "Notes": "",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 3. Factory registration
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Labour",
        "Requirement": "Factory registration / licence & plan approval",
        "Law / basis": "OSH Code 2020 + state rules",
        "Applies to / trigger": "20+ workers with power / 40+ without",
        "What to do": "Apply via single window (Factories & Boilers dept)",
        "Portal / link": portal_url,
        "Notes": "",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 4. State min wages
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Labour",
        "Requirement": "State minimum wages notification",
        "Law / basis": "Code on Wages 2019 + state notifications",
        "Applies to / trigger": "All employers",
        "What to do": "Track half-yearly revisions (VDA) and pay at least notified rate",
        "Portal / link": portal_url,
        "Notes": "",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 5. Professional Tax
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Tax",
        "Requirement": "Professional Tax",
        "Law / basis": "Article 276 + state PT Act",
        "Applies to / trigger": "Employers, employees, professionals (where levied)",
        "What to do": "Employer registration (PTRC) + enrolment (PTEC); deduct monthly from salaries; max ₹2,500 per person per year" if pt_levied else "Not levied",
        "Portal / link": portal_url,
        "Notes": f"Levied: {'Yes' if pt_levied else 'No'}",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 6. Labour Welfare Fund
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Labour",
        "Requirement": "Labour Welfare Fund contribution",
        "Law / basis": f"{state_name} Labour Welfare Fund law (where enacted)",
        "Applies to / trigger": "Employers and employees (where enacted)",
        "What to do": "Pay employer + employee contributions at state-specified rate/frequency" if lwf_app else "Not applicable",
        "Portal / link": portal_url,
        "Notes": f"Applicable: {'Yes' if lwf_app else 'No'}",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 7. Consent to Establish / Operate (CTE/CTO)
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Environment",
        "Requirement": "Consent to Establish / Operate (CTE/CTO)",
        "Law / basis": "Water Act 1974; Air Act 1981",
        "Applies to / trigger": "Red/Orange/Green category units (White exempt)",
        "What to do": f"Apply to {state_name} SPCB/PCC (usually via single window)",
        "Portal / link": portal_url,
        "Notes": "",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 8. Fire NOC & Safety
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Safety",
        "Requirement": "Fire NOC, building plan, electrical & boiler approvals",
        "Law / basis": "State Fire Services Act; building bye-laws; CEA regulations",
        "Applies to / trigger": "As per building size / installation",
        "What to do": "Apply via single window or respective department",
        "Portal / link": portal_url,
        "Notes": "",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 9. Product & Metrology
    state_compliance.append({
        "ID": f"SC-{sc_idx:03d}",
        "State / UT": state_name,
        "Type": stype,
        "Domain": "Product",
        "Requirement": "Legal Metrology registration & verification; trade licence",
        "Law / basis": "Legal Metrology Act 2009; municipal acts",
        "Applies to / trigger": "Packers/users of weights & measures; urban premises",
        "What to do": "Apply to state Legal Metrology / ULB",
        "Portal / link": portal_url,
        "Notes": "",
        "Verification": "Knowledge-based; verify on official link"
    })
    sc_idx += 1

    # 10. Facilitation (where enacted)
    if facilitation_note:
        state_compliance.append({
            "ID": f"SC-{sc_idx:03d}",
            "State / UT": state_name,
            "Type": stype,
            "Domain": "Facilitation",
            "Requirement": "Self-certification / deferred approvals for MSMEs",
            "Law / basis": "State MSME facilitation law",
            "Applies to / trigger": "New MSMEs (conditions apply)",
            "What to do": facilitation_note,
            "Portal / link": portal_url,
            "Notes": "",
            "Verification": "Knowledge-based; verify on official link"
        })
        sc_idx += 1

with open(os.path.join(DATA_DIR, 'state_compliance.json'), 'w', encoding='utf-8') as f:
    json.dump(state_compliance, f, indent=2, ensure_ascii=False)

# 4. STATE INCENTIVES (126 records)
state_incentives_data = [
    # AP
    ("Andhra Pradesh", "State", "Industrial policy", "AP Industrial Development Policy 4.0 (2024-29)", "Capital subsidy, SGST reimbursement, power & stamp-duty concessions", "https://www.apindustries.gov.in", "Knowledge-based; verify on official link"),
    ("Andhra Pradesh", "State", "MSME policy", "AP MSME & Entrepreneurship Development Policy 4.0 (2024-29)", "Capital subsidy, interest subvention, special support for SC/ST/women/BC entrepreneurs", "https://www.apindustries.gov.in", "Knowledge-based; verify on official link"),
    ("Andhra Pradesh", "State", "Startup policy", "AP Innovation & Startup Policy 4.0", "Incubation, seed funding, reimbursements", "https://www.apindustries.gov.in", "Knowledge-based; verify on official link"),
    ("Andhra Pradesh", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Arunachal
    ("Arunachal Pradesh", "State", "Industrial policy", "Arunachal Pradesh Industrial & Investment Policy", "Capital, interest and transport subsidies (plus central UNNATI 2024)", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Arunachal Pradesh", "State", "Scheme", "Deen Dayal Upadhyaya Swavalamban Yojana", "Capital subsidy for youth enterprises", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Arunachal Pradesh", "State", "Startup policy", "Arunachal Pradesh Startup Policy", "Seed support and incubation", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Arunachal Pradesh", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Assam
    ("Assam", "State", "Industrial policy", "Industrial & Investment Policy of Assam (current)", "Capital subsidy, SGST reimbursement, interest subvention", "https://easeofdoingbusinessinassam.in", "Knowledge-based; verify on official link"),
    ("Assam", "State", "Scheme", "CM's Atmanirbhar Asom Abhijan", "Financial assistance for youth-led enterprises", "https://easeofdoingbusinessinassam.in", "Knowledge-based; verify on official link"),
    ("Assam", "State", "Startup policy", "Assam Startup Policy / Assam Startup – The Nest", "Incubation, seed grants", "https://easeofdoingbusinessinassam.in", "Knowledge-based; verify on official link"),
    ("Assam", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Bihar
    ("Bihar", "State", "Industrial policy", "Bihar Industrial Investment Promotion Policy / Package (current)", "Capital & interest subsidies, land concessions, SGST reimbursement", "https://state.bihar.gov.in/industries", "Knowledge-based; verify on official link"),
    ("Bihar", "State", "Scheme", "Mukhyamantri Udyami Yojana", "Up to ₹10 lakh (part grant, part interest-free loan) for SC/ST, EBC, women, youth, minority entrepreneurs", "https://udyami.bihar.gov.in", "Knowledge-based; verify on official link"),
    ("Bihar", "State", "Startup policy", "Bihar Startup Policy", "Seed funding, incubation", "https://startup.bihar.gov.in", "Knowledge-based; verify on official link"),
    ("Bihar", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Chhattisgarh
    ("Chhattisgarh", "State", "Industrial policy", "Chhattisgarh Industrial Development Policy 2024-30", "Capital subsidy, interest subsidy, SGST reimbursement, employment incentives", "https://industries.cg.gov.in", "Knowledge-based; verify on official link"),
    ("Chhattisgarh", "State", "Startup policy", "Chhattisgarh startup support", "Incubation and seed support", "https://industries.cg.gov.in", "Knowledge-based; verify on official link"),
    ("Chhattisgarh", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Goa
    ("Goa", "State", "Industrial policy", "Goa Investment / Industrial Policy (current)", "Investment incentives via GIPB", "https://goaipb.goa.gov.in", "Knowledge-based; verify on official link"),
    ("Goa", "State", "Startup policy", "Goa Startup Policy", "Seed capital, lease rental and other reimbursements", "https://www.startup.goa.gov.in", "Knowledge-based; verify on official link"),
    ("Goa", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Gujarat
    ("Gujarat", "State", "Industrial policy", "Gujarat Industrial Policy 2020", "Capital/interest incentives, employment incentives", "https://ifp.gujarat.gov.in", "Knowledge-based; verify on official link"),
    ("Gujarat", "State", "MSME policy", "Atmanirbhar Gujarat Scheme for Assistance to MSMEs", "Capital incentive (up to ₹35 lakh for micro), interest subsidy, net SGST, local-employment incentive", "https://ifp.gujarat.gov.in", "Verified against current sources (Oct 2026)"),
    ("Gujarat", "State", "Startup policy", "Student Startup & Innovation Policy (SSIP 2.0) / Gujarat Startup scheme", "PoC grants up to ₹2.5 lakh for students; startup support", "https://ssip.gujarat.gov.in", "Verified against current sources (Oct 2026)"),
    ("Gujarat", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Haryana
    ("Haryana", "State", "Industrial policy", "Make in Haryana Industrial Policy 2026", "For large/mega units; zones (Core/Growth/Emerging/Aspirational) replace A–D blocks; fast incentive release", "https://investharyana.in", "Verified against current sources (Oct 2026)"),
    ("Haryana", "State", "MSME policy", "Haryana Progressive MSME & Export Promotion Policy 2026", "Separate MSME policy incl. testing, automation, AI-adoption & R&D incentives", "https://investharyana.in", "Verified against current sources (Oct 2026)"),
    ("Haryana", "State", "Legacy policy", "Haryana Enterprises & Employment Policy (HEEP) 2020", "Continues to govern cases already in the pipeline", "https://investharyana.in", "Verified against current sources (Oct 2026)"),
    ("Haryana", "State", "Sector policy", "Haryana Agri-Business & Food Processing Policy 2026 (+ other sector policies)", "Sector incentives", "https://investharyana.in", "Verified against current sources (Oct 2026)"),
    ("Haryana", "State", "Startup policy", "Haryana State Startup Policy", "Seed, lease rental, patent reimbursements", "https://startupharyana.gov.in", "Knowledge-based; verify on official link"),
    ("Haryana", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Himachal
    ("Himachal Pradesh", "State", "Industrial policy", "HP Industrial Investment Policy (current)", "Capital and interest subsidies, concessional power", "https://emerginghimachal.hp.gov.in", "Knowledge-based; verify on official link"),
    ("Himachal Pradesh", "State", "Scheme", "Mukhya Mantri Swavalamban Yojana", "Capital subsidy and interest subvention for local youth/women", "https://emerginghimachal.hp.gov.in", "Knowledge-based; verify on official link"),
    ("Himachal Pradesh", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Jharkhand
    ("Jharkhand", "State", "Industrial policy", "Jharkhand Industrial & Investment Promotion Policy (JIIPP) 2021", "Capital subsidy, SGST reimbursement, interest subsidy", "https://jharkhandindustry.gov.in", "Knowledge-based; verify on official link"),
    ("Jharkhand", "State", "Startup policy", "Jharkhand Startup Policy", "Seed support, incubation", "https://jharkhandindustry.gov.in", "Knowledge-based; verify on official link"),
    ("Jharkhand", "State", "Scheme", "Mukhyamantri Rojgar Srijan Yojana", "Subsidised loans for self-employment", "https://jharkhandindustry.gov.in", "Knowledge-based; verify on official link"),
    ("Jharkhand", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Karnataka
    ("Karnataka", "State", "Industrial policy", "Karnataka Industrial Policy 2025-30 (notified 8 Feb 2025)", "Choice of capital subsidy or production-linked incentive; zone-wise MSME capital subsidy; stamp-duty exemption; 30% of industrial land for MSMEs", "https://www.kum.karnataka.gov.in", "Verified against current sources (Oct 2026)"),
    ("Karnataka", "State", "Startup policy", "Karnataka Startup Policy (Elevate programme, KITS)", "Grant-in-aid, incubation, IP reimbursement", "https://startup.karnataka.gov.in", "Knowledge-based; verify on official link"),
    ("Karnataka", "State", "Sector policy", "Karnataka EV policy & ESDM incentives", "Capital subsidy and turnover-linked incentives for EV/ESDM units", "https://www.kum.karnataka.gov.in", "Knowledge-based; verify on official link"),
    ("Karnataka", "State", "Scheme", "Chief Minister's Employment Generation Programme (CMEGP)", "Margin-money subsidy for new micro enterprises", "https://www.kum.karnataka.gov.in", "Knowledge-based; verify on official link"),
    ("Karnataka", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Kerala
    ("Kerala", "State", "Industrial policy", "Kerala Industrial Policy 2023", "Investment subsidy, sunrise-sector support", "https://industry.kerala.gov.in", "Knowledge-based; verify on official link"),
    ("Kerala", "State", "Scheme", "Entrepreneur Support Scheme (ESS)", "Start-up, investment and technology support subsidies for MSMEs", "https://industry.kerala.gov.in", "Knowledge-based; verify on official link"),
    ("Kerala", "State", "Startup policy", "Kerala Startup Mission", "Grants, incubation, seed loans", "https://startupmission.kerala.gov.in", "Knowledge-based; verify on official link"),
    ("Kerala", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Madhya Pradesh
    ("Madhya Pradesh", "State", "Industrial policy", "MP Industrial Promotion Policy 2025", "Investment promotion assistance, employment incentives", "https://invest.mp.gov.in", "Knowledge-based; verify on official link"),
    ("Madhya Pradesh", "State", "MSME policy", "MP MSME Development Policy 2025", "Capital subsidy, interest subsidy for MSMEs", "https://invest.mp.gov.in", "Knowledge-based; verify on official link"),
    ("Madhya Pradesh", "State", "Startup policy", "MP Startup Policy 2025", "Seed & lease support, incubation", "https://startup.mp.gov.in", "Knowledge-based; verify on official link"),
    ("Madhya Pradesh", "State", "Scheme", "Mukhyamantri Udyam Kranti Yojana", "Interest subvention and guarantee fee support for youth loans", "https://invest.mp.gov.in", "Knowledge-based; verify on official link"),
    ("Madhya Pradesh", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Maharashtra
    ("Maharashtra", "State", "Industrial policy", "Maharashtra Industrial Policy & Package Scheme of Incentives (current)", "Industrial promotion subsidy (SGST-linked), electricity duty & stamp duty exemptions", "https://maitri.mahaonline.gov.in", "Knowledge-based; verify on official link"),
    ("Maharashtra", "State", "Scheme", "Chief Minister Employment Generation Programme (CMEGP)", "15–35% margin-money subsidy for new micro enterprises", "https://maha-cmegp.gov.in", "Knowledge-based; verify on official link"),
    ("Maharashtra", "State", "Startup policy", "Maharashtra State Innovative Startup Policy", "Grants, incubation, IP and quality-certification reimbursement", "https://msins.in", "Knowledge-based; verify on official link"),
    ("Maharashtra", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Manipur
    ("Manipur", "State", "Industrial policy", "Manipur Industrial & Investment Policy", "Capital and interest subsidies (plus UNNATI 2024)", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Manipur", "State", "Startup policy", "Startup Manipur", "Seed grants", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Manipur", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Meghalaya
    ("Meghalaya", "State", "Industrial policy", "Meghalaya Industrial & Investment Promotion Policy", "Capital and other incentives (plus UNNATI 2024)", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Meghalaya", "State", "Scheme", "PRIME Meghalaya", "Incubation and enterprise support", "https://primemeghalaya.com", "Knowledge-based; verify on official link"),
    ("Meghalaya", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Mizoram
    ("Mizoram", "State", "Industrial policy", "Mizoram Industrial Policy", "Capital and interest incentives (plus UNNATI 2024)", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Mizoram", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Nagaland
    ("Nagaland", "State", "Industrial policy", "Nagaland Industrial Policy", "Capital and interest incentives (plus UNNATI 2024)", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Nagaland", "State", "Startup policy", "Startup Nagaland", "Seed support", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Nagaland", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Odisha
    ("Odisha", "State", "Industrial policy", "Odisha Industrial Policy Resolution 2022", "Capital investment subsidy, SGST reimbursement, interest subsidy", "https://investodisha.gov.in", "Knowledge-based; verify on official link"),
    ("Odisha", "State", "MSME policy", "Odisha MSME Development Policy 2022", "Capital subsidy, interest subsidy, power tariff reimbursement", "https://investodisha.gov.in", "Knowledge-based; verify on official link"),
    ("Odisha", "State", "Startup policy", "Startup Odisha", "Monthly allowance, seed funding, incubation", "https://startupodisha.gov.in", "Knowledge-based; verify on official link"),
    ("Odisha", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Punjab
    ("Punjab", "State", "Industrial policy", "Punjab Industrial & Business Development Policy 2022", "SGST reimbursement, stamp duty & electricity duty exemptions, capital subsidy for MSMEs", "https://investpunjab.gov.in", "Knowledge-based; verify on official link"),
    ("Punjab", "State", "Startup policy", "Startup Punjab", "Seed grants, incubation", "https://startuppunjab.org", "Knowledge-based; verify on official link"),
    ("Punjab", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Rajasthan
    ("Rajasthan", "State", "Industrial policy", "Rajasthan Investment Promotion Scheme (RIPS) 2024", "Asset-creation incentive, SGST-linked benefits, stamp-duty exemption", "https://invest.rajasthan.gov.in", "Knowledge-based; verify on official link"),
    ("Rajasthan", "State", "MSME policy", "Rajasthan MSME Policy 2024", "Interest subvention, capital subsidy", "https://industries.rajasthan.gov.in", "Knowledge-based; verify on official link"),
    ("Rajasthan", "State", "Scheme", "Vishwakarma Yuva Udyami Protsahan Yojana", "Interest subvention on loans for young entrepreneurs", "https://industries.rajasthan.gov.in", "Knowledge-based; verify on official link"),
    ("Rajasthan", "State", "Startup policy", "iStart Rajasthan", "Seed funding, incubation", "https://istart.rajasthan.gov.in", "Knowledge-based; verify on official link"),
    ("Rajasthan", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Sikkim
    ("Sikkim", "State", "Industrial policy", "Sikkim Industrial Policy", "Capital and other incentives (plus UNNATI 2024)", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Sikkim", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Tamil Nadu
    ("Tamil Nadu", "State", "Industrial policy", "Tamil Nadu Industrial Policy 2021", "Capital subsidy, SGST reimbursement, employment incentives", "https://tnswp.com", "Knowledge-based; verify on official link"),
    ("Tamil Nadu", "State", "MSME policy", "Tamil Nadu MSME Policy 2021", "Capital subsidy, LT power tariff subsidy, back-ended interest subsidy", "https://www.msmeonline.tn.gov.in", "Knowledge-based; verify on official link"),
    ("Tamil Nadu", "State", "Scheme", "NEEDS (New Entrepreneur-cum-Enterprise Development Scheme)", "Capital subsidy + interest subvention for first-generation entrepreneurs", "https://www.msmeonline.tn.gov.in", "Knowledge-based; verify on official link"),
    ("Tamil Nadu", "State", "Scheme", "Annal Ambedkar Business Champions Scheme", "Capital subsidy and interest subvention for SC/ST entrepreneurs", "https://www.msmeonline.tn.gov.in", "Knowledge-based; verify on official link"),
    ("Tamil Nadu", "State", "Startup policy", "StartupTN – TN Startup & Innovation Policy", "TANSEED grants, incubation", "https://startuptn.in", "Knowledge-based; verify on official link"),
    ("Tamil Nadu", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Telangana
    ("Telangana", "State", "Industrial policy", "T-IDEA (Telangana State Industrial Development & Entrepreneur Advancement)", "Capital subsidy, SGST reimbursement, power cost reimbursement", "https://ipass.telangana.gov.in", "Knowledge-based; verify on official link"),
    ("Telangana", "State", "Scheme", "T-PRIDE", "Enhanced incentives for SC/ST entrepreneurs", "https://ipass.telangana.gov.in", "Knowledge-based; verify on official link"),
    ("Telangana", "State", "MSME policy", "Telangana MSME Policy 2024", "Credit, land, technology and marketing support for MSMEs", "https://ipass.telangana.gov.in", "Knowledge-based; verify on official link"),
    ("Telangana", "State", "Startup policy", "Telangana Innovation ecosystem (T-Hub, TSIC, WE Hub)", "Incubation, grants", "https://t-hub.co", "Knowledge-based; verify on official link"),
    ("Telangana", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Tripura
    ("Tripura", "State", "Industrial policy", "Tripura Industrial Investment Promotion Incentive Scheme", "Capital and other incentives (plus UNNATI 2024)", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Tripura", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Uttar Pradesh
    ("Uttar Pradesh", "State", "Industrial policy", "UP Industrial Investment & Employment Promotion Policy 2022", "Capital subsidy / SGST reimbursement, stamp-duty exemption", "https://invest.up.gov.in", "Knowledge-based; verify on official link"),
    ("Uttar Pradesh", "State", "MSME policy", "UP MSME Promotion Policy 2022", "Capital subsidy (higher in backward regions), interest subsidy", "https://msme.up.gov.in", "Knowledge-based; verify on official link"),
    ("Uttar Pradesh", "State", "Scheme", "CM Yuva Udyami Vikas Abhiyan (CM-YUVA)", "Interest-free, collateral-free loans for young first-time entrepreneurs", "https://msme.up.gov.in", "Knowledge-based; verify on official link"),
    ("Uttar Pradesh", "State", "Scheme", "One District One Product (ODOP)", "Margin money, CFCs, marketing, training", "https://odopup.in", "Knowledge-based; verify on official link"),
    ("Uttar Pradesh", "State", "Startup policy", "UP Startup Policy", "Seed, sustenance allowance, incubation", "https://startinup.up.gov.in", "Knowledge-based; verify on official link"),
    ("Uttar Pradesh", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # Uttarakhand
    ("Uttarakhand", "State", "MSME policy", "Uttarakhand MSME Policy 2023", "Capital subsidy (category-wise districts), interest subsidy", "https://investuttarakhand.uk.gov.in", "Knowledge-based; verify on official link"),
    ("Uttarakhand", "State", "Scheme", "Mukhyamantri Swarozgar Yojana", "Margin-money subsidy for self-employment", "https://msy.uk.gov.in", "Knowledge-based; verify on official link"),
    ("Uttarakhand", "State", "Startup policy", "Uttarakhand Startup Policy 2023", "Seed and incubation support", "https://startuputtarakhand.uk.gov.in", "Knowledge-based; verify on official link"),
    ("Uttarakhand", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # West Bengal
    ("West Bengal", "State", "Industrial policy", "West Bengal industrial incentive schemes (current)", "Capital and other incentives (check current scheme)", "https://wbidc.com", "Knowledge-based; verify on official link"),
    ("West Bengal", "State", "Scheme", "Bhabishyat Credit Card", "Collateral-free loans up to ₹5 lakh for youth entrepreneurs", "https://wbmsme.gov.in", "Knowledge-based; verify on official link"),
    ("West Bengal", "State", "Startup policy", "West Bengal Startup policy", "Incubation and seed support", "https://wbmsme.gov.in", "Knowledge-based; verify on official link"),
    ("West Bengal", "State", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    # UTs
    ("Andaman & Nicobar Islands", "UT", "Industrial policy", "A&N Islands Industrial Policy", "UT-level incentives", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Andaman & Nicobar Islands", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    ("Chandigarh", "UT", "Industrial policy", "Chandigarh Industrial Policy", "UT-level incentives", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Chandigarh", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    ("Dadra & Nagar Haveli and Daman & Diu", "UT", "Industrial policy", "DNH&DD Industrial Policy", "UT-level incentives", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Dadra & Nagar Haveli and Daman & Diu", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    ("Delhi (NCT)", "UT", "Industrial policy", "Delhi Industrial Policy / Startup Policy (current)", "Industrial area redevelopment, startup support", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Delhi (NCT)", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    ("Jammu & Kashmir", "UT", "Industrial policy", "J&K Industrial Policy 2021-30 & J&K Industrial Land Allotment Policy", "UT incentives, land", "https://singlewindow.jk.gov.in", "Knowledge-based; verify on official link"),
    ("Jammu & Kashmir", "UT", "Central scheme for UT", "New Central Sector Scheme for J&K (2021)", "Capital, interest, GST-linked & working-capital incentives", "https://dpiit.gov.in", "Knowledge-based; verify on official link"),
    ("Jammu & Kashmir", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    ("Ladakh", "UT", "Industrial policy", "Ladakh Industrial / Investment Policy", "UT-level incentives", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Ladakh", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    ("Lakshadweep", "UT", "Industrial policy", "Lakshadweep enterprise support", "Limited UT-level schemes", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Lakshadweep", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link"),
    ("Puducherry", "UT", "Industrial policy", "Puducherry Industrial Policy", "UT-level incentives", "https://www.nsws.gov.in", "Knowledge-based; verify on official link"),
    ("Puducherry", "UT", "Central schemes – state delivery", "PMEGP / PMFME / RAMP / PM Vishwakarma state nodal agencies", "Central schemes are applied for through state nodal agencies, DICs and banks", "https://www.myscheme.gov.in", "Knowledge-based; verify on official link")
]

state_incentives = []
for idx, item in enumerate(state_incentives_data, 1):
    state_incentives.append({
        "ID": f"SI-{idx:03d}",
        "State / UT": item[0],
        "Type": item[1],
        "Category": item[2],
        "Policy / scheme": item[3],
        "Key benefit": item[4],
        "Apply / info link": item[5],
        "Verification": item[6]
    })

with open(os.path.join(DATA_DIR, 'state_incentives.json'), 'w', encoding='utf-8') as f:
    json.dump(state_incentives, f, indent=2, ensure_ascii=False)

# 5. AGGREGATOR PORTALS (10 records)
aggregator_portals = [
    {
        "Portal": "myScheme",
        "What it aggregates": "Search & eligibility discovery for central and state schemes",
        "Gap": "Scheme discovery (citizen-focused); no compliance calendar; limited enterprise thresholds",
        "Link": "https://www.myscheme.gov.in"
    },
    {
        "Portal": "National Single Window System (NSWS)",
        "What it aggregates": "Central approvals + links to state single-window systems",
        "Gap": "Approvals, not incentives eligibility; state coverage uneven",
        "Link": "https://www.nsws.gov.in"
    },
    {
        "Portal": "Jan Samarth",
        "What it aggregates": "Credit-linked government schemes",
        "Gap": "Credit schemes only",
        "Link": "https://www.jansamarth.in"
    },
    {
        "Portal": "Udyam / Udyami Mitra",
        "What it aggregates": "MSME registration; credit & handholding",
        "Gap": "No state incentives or compliance mapping",
        "Link": "https://www.udyamimitra.in"
    },
    {
        "Portal": "MSME Champions",
        "What it aggregates": "MoMSME schemes & grievances",
        "Gap": "MoMSME only",
        "Link": "https://champions.gov.in"
    },
    {
        "Portal": "Shram Suvidha",
        "What it aggregates": "Central labour registrations & returns",
        "Gap": "Labour only; state rules separate",
        "Link": "https://shramsuvidha.gov.in"
    },
    {
        "Portal": "Startup India",
        "What it aggregates": "Startup recognition, central & some state startup schemes",
        "Gap": "Startups only",
        "Link": "https://www.startupindia.gov.in"
    },
    {
        "Portal": "PARIVESH",
        "What it aggregates": "Environment/forest clearances",
        "Gap": "Environment only",
        "Link": "https://parivesh.nic.in"
    },
    {
        "Portal": "India Industrial Land Bank",
        "What it aggregates": "Industrial land & parks across states",
        "Gap": "Land only",
        "Link": "https://iilb.gov.in"
    },
    {
        "Portal": "State single-window portals (36)",
        "What it aggregates": "State approvals and incentive applications",
        "Gap": "One state at a time; formats differ",
        "Link": "https://www.nsws.gov.in"
    }
]

with open(os.path.join(DATA_DIR, 'aggregator_portals.json'), 'w', encoding='utf-8') as f:
    json.dump(aggregator_portals, f, indent=2, ensure_ascii=False)

print(f"Generated:")
print(f"  Central Compliance: {len(central_compliance)}")
print(f"  Central Incentives: {len(central_incentives)}")
print(f"  State Compliance:   {len(state_compliance)}")
print(f"  State Incentives:   {len(state_incentives)}")
print(f"  Aggregator Portals: {len(aggregator_portals)}")
print(f"  Total records:      {len(central_compliance) + len(central_incentives) + len(state_compliance) + len(state_incentives)}")
