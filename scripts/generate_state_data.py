"""
Script to create the complete state compliance and state incentives dataset files.
"""
import os
import json
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# State metadata
STATES_AND_UTS = [
    ("Andhra Pradesh", "State", "https://www.apindustries.gov.in", "https://appcb.ap.gov.in", True, True, None),
    ("Arunachal Pradesh", "State", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Assam", "State", "https://easeofdoingbusinessinassam.in", "https://pcbassam.org", True, False, None),
    ("Bihar", "State", "https://www.nsws.gov.in", "https://bspcb.bihar.gov.in", True, False, None),
    ("Chhattisgarh", "State", "https://industries.cg.gov.in", "https://enviscecb.org", False, True, None),
    ("Goa", "State", "https://goaipb.goa.gov.in", "https://goaspcb.gov.in", False, True, None),
    ("Gujarat", "State", "https://ifp.gujarat.gov.in", "https://gpcb.gujarat.gov.in", True, True, None),
    ("Haryana", "State", "https://investharyana.in", "https://hspcb.org.in", False, True, "Haryana State Employment of Local Candidates Act 2020 was struck down by the Punjab & Haryana High Court; check status of appeal"),
    ("Himachal Pradesh", "State", "https://emerginghimachal.hp.gov.in", "https://hppcb.nic.in", False, False, None),
    ("Jharkhand", "State", "https://jharkhandindustry.gov.in", "https://jspcb.nic.in", True, False, None),
    ("Karnataka", "State", "https://ebiz.karnataka.gov.in", "https://kspcb.karnataka.gov.in", True, True, "Karnataka Industries (Facilitation) Act – MSMEs can start on an acknowledgement and get approvals within 3 years (verify current rules)"),
    ("Kerala", "State", "https://kswift.kerala.gov.in", "https://keralapcb.nic.in", True, True, "Kerala MSME Facilitation Act 2019 – start on self-declaration; approvals within 3 years"),
    ("Madhya Pradesh", "State", "https://invest.mp.gov.in", "https://mppcb.mp.gov.in", True, True, None),
    ("Maharashtra", "State", "https://maitri.mahaonline.gov.in", "https://mpcb.gov.in", True, True, None),
    ("Manipur", "State", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Meghalaya", "State", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Mizoram", "State", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Nagaland", "State", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Odisha", "State", "https://investodisha.gov.in", "https://ospcboard.org", True, True, None),
    ("Punjab", "State", "https://investpunjab.gov.in", "https://ppcb.punjab.gov.in", True, True, "Punjab Right to Business Act 2020 – in-principle approval for MSMEs in approved zones (verify)"),
    ("Rajasthan", "State", "https://swcs.rajasthan.gov.in", "https://environment.rajasthan.gov.in", False, False, "Rajasthan MSME (Facilitation of Establishment & Operation) Act 2019 – start on acknowledgement; approvals within 3 years"),
    ("Sikkim", "State", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Tamil Nadu", "State", "https://tnswp.com", "https://tnpcb.gov.in", True, True, None),
    ("Telangana", "State", "https://ipass.telangana.gov.in", "https://tspcb.cgg.gov.in", True, True, None),
    ("Tripura", "State", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None),
    ("Uttar Pradesh", "State", "https://niveshmitra.up.nic.in", "https://uppcb.up.gov.in", False, False, "UP MSME (Facilitation) Act – 1,000-day exemption from certain approvals (verify)"),
    ("Uttarakhand", "State", "https://investuttarakhand.uk.gov.in", "https://ueppcb.uk.gov.in", False, False, None),
    ("West Bengal", "State", "https://silpasathi.wb.gov.in", "https://wbpcb.gov.in", True, True, None),
    ("Andaman & Nicobar Islands", "UT", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Chandigarh", "UT", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, True, None),
    ("Dadra & Nagar Haveli and Daman & Diu", "UT", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Delhi (NCT)", "UT", "https://www.nsws.gov.in", "https://dpcc.delhigovt.nic.in", False, True, None),
    ("Jammu & Kashmir", "UT", "https://singlewindow.jk.gov.in", "https://jkspcb.nic.in", False, False, None),
    ("Ladakh", "UT", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Lakshadweep", "UT", "https://www.nsws.gov.in", "https://www.nsws.gov.in", False, False, None),
    ("Puducherry", "UT", "https://www.nsws.gov.in", "https://www.nsws.gov.in", True, False, None)
]

print("State metadata loaded:", len(STATES_AND_UTS))
