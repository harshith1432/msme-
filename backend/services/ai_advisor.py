"""
Action-Oriented AI Advisory Service for MSME Compliance & Incentives Navigator.
Generates structured 5-part Action Cards answering "What you need to do" in 8 languages:
  English, Hindi, Marathi, Gujarati, Tamil, Telugu, Kannada, Bengali.
Strictly grounded in the 628 official Central & State records.
"""
import os
import json
from .rules_engine import RulesEngine

LANGUAGE_NAMES = {
    'en': 'English',
    'hi': 'हिन्दी (Hindi)',
    'mr': 'मराठी (Marathi)',
    'gu': 'ગુજરાતી (Gujarati)',
    'ta': 'தமிழ் (Tamil)',
    'te': 'తెలుగు (Telugu)',
    'kn': 'ಕನ್ನಡ (Kannada)',
    'bn': 'বাংলা (Bengali)'
}

# Multilingual Headers for 5-part Action Cards
ACTION_HEADERS = {
    'en': {
        'title': 'Operational Compliance & Incentive Action Plan',
        'p1': '1. Immediate Priorities (Complete This Week)',
        'p2': '2. Periodic & Recurring Deadlines',
        'p3': '3. Top Government Incentives You Can Claim',
        'p4': '4. Mandatory Document Checklist',
        'p5': '5. Official Action Portals',
        'disclaimer': 'Guidance Notice: This action plan is based on current statutory data. Always verify specific filings on official portals or consult your Chartered Accountant.'
    },
    'hi': {
        'title': 'अनुपालन एवं प्रोत्साहन कार्य योजना (Action Plan)',
        'p1': '1. तत्काल प्राथमिकताएं (इस सप्ताह पूरा करें)',
        'p2': '2. आवधिक एवं नियमित समय सीमा (Deadlines)',
        'p3': '3. सरकारी प्रोत्साहन व सब्सिडी जिनका लाभ आप ले सकते हैं',
        'p4': '4. अनिवार्य दस्तावेजों की चेकलिस्ट',
        'p5': '5. आधिकारिक सरकारी पोर्टल (Official Portals)',
        'disclaimer': 'मार्गदर्शन सूचना: यह कार्य योजना आधिकारिक डेटा पर आधारित है। अंतिम फाइलिंग से पहले आधिकारिक पोर्टल या अपने चार्टर्ड अकाउंटेंट (CA) से परामर्श लें।'
    },
    'mr': {
        'title': 'अनुपालन आणि प्रोत्साहन कृती आराखडा (Action Plan)',
        'p1': '1. तात्काळ प्राधान्यक्रम (या आठवड्यात पूर्ण करा)',
        'p2': '2. नियतकालिक मुदती (Deadlines)',
        'p3': '3. सरकारी प्रोत्साहन आणि अनुदाने जी आपण मिळवू शकता',
        'p4': '4. आवश्यक कागदपत्रांची यादी',
        'p5': '5. अधिकृत सरकारी पोर्टल्स',
        'disclaimer': 'मार्गदर्शन सूचना: हा कृती आराखडा अधिकृत माहितीवर आधारित आहे. अंतिम अर्ज करण्यापूर्वी अधिकृत पोर्टल तपासा.'
    },
    'gu': {
        'title': 'અનુપાલન અને પ્રોત્સાહન એક્શન પ્લાન (Action Plan)',
        'p1': '1. તાત્કાલિક પ્રાથમિકતાઓ (આ અઠવાડિયે પૂર્ણ કરો)',
        'p2': '2. સમયાંતરે આવતી અંતિમ તારીખો (Deadlines)',
        'p3': '3. સરકારી પ્રોત્સાહનો અને સબસિડીઓ જે તમે મેળવી શકો છો',
        'p4': '4. જરૂરી દસ્તાવેજોની ચેકલિસ્ટ',
        'p5': '5. સત્તાવાર સરકારી પોર્ટલ',
        'disclaimer': 'માર્ગદર્શન સૂચના: આ એક્શન પ્લાન અધિકૃત માહિતી પર આધારિત છે. અરજી કરતા પહેલા સત્તાવાર પોર્ટલની ચકાસણી કરો.'
    },
    'ta': {
        'title': 'இணக்கம் மற்றும் சலுகைகளுக்கான செயல் திட்டம் (Action Plan)',
        'p1': '1. உடனடி முன்னுரிமைகள் (இந்த வாரத்திற்குள் முடிக்கவும்)',
        'p2': '2. காலக்கெடு மற்றும் தொடர் கடமைகள் (Deadlines)',
        'p3': '3. நீங்கள் பெறக்கூடிய சிறந்த அரசு சலுகைகள் மற்றும் மானியங்கள்',
        'p4': '4. கட்டாய ஆவணங்களின் சரிபார்ப்புப் பட்டியல்',
        'p5': '5. அதிகாரப்பூர்வ அரசு இணையதளங்கள்',
        'disclaimer': 'வழிகாட்டுதல் குறிப்பு: இந்த செயல் திட்டம் அதிகாரப்பூர்வ அரசுத் தரவுகளை அடிப்படையாகக் கொண்டது.'
    },
    'te': {
        'title': 'నిబంధనల అమలు & ప్రోత్సాహకాల కార్యాచరణ ప్రణాళిక (Action Plan)',
        'p1': '1. తక్షణ ప్రాధాన్యతలు (ఈ వారం పూర్తి చేయండి)',
        'p2': '2. ఆవర్తన గడువులు (Deadlines)',
        'p3': '3. మీరు పొందగల ప్రభుత్వ రాయితీలు & ప్రోత్సాహకాలు',
        'p4': '4. అవసరమైన పత్రాల చెక్‌లిస్ట్',
        'p5': '5. అధికారిక ప్రభుత్వ పోర్టల్‌లు',
        'disclaimer': 'మార్గదర్శక నోటీసు: ఈ కార్యాచరణ ప్రణాళిక అధికారిక ప్రభుత్వ నిబంధనలపై ఆధారపడి ఉంది.'
    },
    'kn': {
        'title': 'ಅನುಸರಣೆ ಮತ್ತು ಪ್ರೋತ್ಸಾಹಕಗಳ ಕ್ರಿಯಾ ಯೋಜನೆ (Action Plan)',
        'p1': '1. ತಕ್ಷಣದ ಆದ್ಯತೆಗಳು (ಈ ವಾರ ಪೂರ್ಣಗೊಳಿಸಿ)',
        'p2': '2. ನಿಯಮಿತ ಗಡುವುಗಳು (Deadlines)',
        'p3': '3. ನೀವು ಪಡೆಯಬಹುದಾದ ಉನ್ನತ ಸರ್ಕಾರಿ ಪ್ರೋತ್ಸಾಹಗಳು ಮತ್ತು ಸಬ್ಸಿಡಿಗಳು',
        'p4': '4. ಕಡ್ಡಾಯ ದಾಖಲೆಗಳ ಪರಿಶೀಲನಾ ಪಟ್ಟಿ',
        'p5': '5. ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಪೋರ್ಟಲ್‌ಗಳು',
        'disclaimer': 'ಮಾರ್ಗದರ್ಶನ ಸೂಚನೆ: ಈ ಕ್ರಿಯಾ ಯೋಜನೆಯು ಅಧಿಕೃತ ನಿಯಮಗಳನ್ನು ಆಧರಿಸಿದೆ. ಅಂತಿಮ ಸಲ್ಲಿಕೆಗೆ ಮುನ್ನ ಅಧಿಕೃತ ಪೋರ್ಟಲ್ ಪರಿಶೀಲಿಸಿ.'
    },
    'bn': {
        'title': 'সম্মতি ও প্রণোদনা কর্মপরিকল্পনা (Action Plan)',
        'p1': '1. তাৎক্ষণিক অগ্রাধিকার (এই সপ্তাহে সম্পূর্ণ করুন)',
        'p2': '2. পর্যায়ক্রমিক সময়সীমা (Deadlines)',
        'p3': '3. শীর্ষ সরকারি প্রণোদনা ও অনুদান যা আপনি দাবি করতে পারেন',
        'p4': '4. প্রয়োজনীয় নথিপত্রের তালিকা',
        'p5': '5. অফিসিয়াল সরকারি পোর্টাল',
        'disclaimer': 'নির্দেশিকা বিজ্ঞপ্তি: এই কর্মপরিকল্পনা অফিসিয়াল সরকারি নিয়মের উপর ভিত্তি করে তৈরি।'
    },
    'ml': {
        'title': 'അനുസരണവും പ്രോത്സാഹനങ്ങളും പ്രവർത്തന പദ്ധതി (Action Plan)',
        'p1': '1. ഉടനടി മുൻഗണനകൾ (ഈ ആഴ്ച പൂർത്തിയാക്കുക)',
        'p2': '2. വരാനിരിക്കുന്ന സമയപരിധികൾ (Deadlines)',
        'p3': '3. നിങ്ങൾക്ക് ക്ലെയിം ചെയ്യാവുന്ന മികച്ച സർക്കാർ സബ്‌സിഡികൾ',
        'p4': '4. നിർബന്ധിത രേഖകളുടെ ചെക്ക്‌ലിസ്റ്റ്',
        'p5': '5. ഔദ്യോഗിക സർക്കാർ പോർട്ടലുകൾ',
        'disclaimer': 'മാർഗ്ഗനിർദ്ദേശ കുറിപ്പ്: ഈ പ്രവർത്തന പദ്ധതി ഔദ്യോഗിക സർക്കാർ ഡാറ്റയെ അടിസ്ഥാനമാക്കിയുള്ളതാണ്.'
    }
}

class AIAdvisor:
    def __init__(self):
        self.rules_engine = RulesEngine()

    def generate_action_plan(self, profile, lang='en'):
        """
        Generates a comprehensive, personalized 5-part Action Card.
        """
        lang = lang if lang in ACTION_HEADERS else 'en'
        headers = ACTION_HEADERS[lang]
        evaluation = self.rules_engine.evaluate_company(profile)

        company_name = profile.get('name', 'Your Enterprise')
        state = profile.get('state', 'Karnataka')
        sector = profile.get('sector', 'Manufacturing')
        turnover = profile.get('turnover', 0)
        employees = profile.get('employees', 0)
        msme_class = evaluation['msme_classification']

        # 1. Immediate Priorities
        immediate_items = []
        immediate_items.append({
            'action': 'Obtain / Update Udyam Registration (Zero Fee)',
            'why': f'Formally certifies you as a {msme_class}. Unlocks Priority Sector Lending and 45-day payment protections under Section 43B(h).',
            'authority': 'Ministry of MSME',
            'portal': 'https://udyamregistration.gov.in'
        })

        if employees >= 10:
            immediate_items.append({
                'action': 'Mandatory ESI Registration & POSH Internal Committee',
                'why': f'Headcount is {employees} (threshold is 10+). Staff earning <= ₹21,000/mo must be enrolled under Social Security Code 2020.',
                'authority': 'ESIC / Ministry of Labour',
                'portal': 'https://www.esic.gov.in'
            })

        if employees >= 20:
            immediate_items.append({
                'action': 'Mandatory EPF Registration & Grievance Committee',
                'why': f'Headcount is {employees} (threshold is 20+). Mandatory 12% employer + 12% employee contribution.',
                'authority': 'EPFO',
                'portal': 'https://unifiedportal-emp.epfindia.gov.in'
            })

        if 'Food' in sector and turnover >= 1200000:
            immediate_items.append({
                'action': 'Obtain FSSAI State Food Licence',
                'why': f'Turnover (₹{turnover:,}) exceeds ₹12 Lakh threshold for basic food registration.',
                'authority': 'FSSAI',
                'portal': 'https://foscos.fssai.gov.in'
            })

        # State single window
        state_portal_url = "https://www.nsws.gov.in"
        state_portal_name = f"{state} Single Window"
        if evaluation['matched_state_compliance']:
            first_sc = evaluation['matched_state_compliance'][0]
            state_portal_url = first_sc.get('Portal / link', state_portal_url)
            state_portal_name = first_sc.get('Requirement', state_portal_name)

        immediate_items.append({
            'action': f'Register on {state} Single Window & Shops & Establishments',
            'why': f'Mandatory state registration for premises and operating approvals in {state}.',
            'authority': f'{state} Industries & Labour Dept',
            'portal': state_portal_url
        })

        # 2. Periodic Deadlines
        periodic_items = [
            {'name': 'Monthly EPF / ESI Contribution Deposit', 'due': '15th of every month', 'notes': 'Deposit ECR returns via EPFO/ESIC portals.'},
            {'name': 'Monthly Salary Payment to Employees', 'due': 'By 7th of following month', 'notes': 'Mandatory under Code on Wages 2019.'},
            {'name': 'Monthly / Quarterly GSTR-3B & GSTR-1', 'due': '11th, 13th, 20th of the month', 'notes': 'File regular outward supplies and tax liability returns.'},
            {'name': 'Quarterly Advance Tax Payment', 'due': '15 Jun, 15 Sep, 15 Dec, 15 Mar', 'notes': '15%, 45%, 75%, 100% installments under Income-tax Act.'},
            {'name': 'Vendor Due Clearance (MSME 45-day Rule)', 'due': 'Ongoing (within 15-45 days)', 'notes': 'Section 43B(h) / Section 15 of MSMED Act; delayed dues disallow tax deductions.'}
        ]

        if turnover > 50000000:
            periodic_items.append({'name': 'GST E-Invoicing (IRN Generation)', 'due': 'Real-time on B2B invoices', 'notes': 'Report invoices on IRP within 30 days.'})

        # 3. Top Incentives to Claim
        top_incentives = []
        for inc in evaluation['matched_central_incentives'][:3]:
            top_incentives.append({
                'title': inc.get('Scheme', ''),
                'benefit': inc.get('Key benefit', ''),
                'apply_link': inc.get('Apply / info link', 'https://www.myscheme.gov.in')
            })
        for inc in evaluation['matched_state_incentives'][:2]:
            top_incentives.append({
                'title': f"{state}: {inc.get('Policy / scheme', '')}",
                'benefit': inc.get('Key benefit', ''),
                'apply_link': inc.get('Apply / info link', state_portal_url)
            })

        # 4. Mandatory Documents Checklist
        docs = [
            'Company PAN & Certificate of Incorporation / Partnership Deed',
            'Directors / Partners Aadhaar & PAN Card with mobile OTP linked',
            'Registered Office Electricity Bill / Rent Agreement & NOC',
            'Bank Statement & Cancelled Cheque (for subsidy direct deposit)',
            'Audited Financial Statements / ITR & GST 3B Summary',
            'Udyam Registration Certificate (with latest turnover & investment details)',
            'Employee Muster Roll / Salary Sheet (for EPF/ESI calculation)'
        ]

        # 5. Official Action Portals
        portals = [
            {'name': 'Udyam Registration Portal', 'url': 'https://udyamregistration.gov.in', 'purpose': 'Free MSME certification & benefits'},
            {'name': 'Jan Samarth Credit Portal', 'url': 'https://www.jansamarth.in', 'purpose': 'Apply for subsidized MSME loans & interest subventions'},
            {'name': 'National Single Window System (NSWS)', 'url': 'https://www.nsws.gov.in', 'purpose': 'Central & State single-window clearances'},
            {'name': f'{state_portal_name}', 'url': state_portal_url, 'purpose': f'{state} state clearances, subsidies & licences'},
            {'name': 'Shram Suvidha Portal', 'url': 'https://shramsuvidha.gov.in', 'purpose': 'Unified labour returns & licensing under 4 Labour Codes'},
            {'name': 'MSME Samadhaan Portal', 'url': 'https://samadhaan.msme.gov.in', 'purpose': 'Delayed payment claims against corporate/buyer dues'}
        ]

        return {
            'language': lang,
            'language_name': LANGUAGE_NAMES[lang],
            'headers': headers,
            'company_name': company_name,
            'msme_classification': msme_class,
            'is_startup': evaluation['is_startup_eligible'],
            'startup_reason': evaluation['startup_reason'],
            'summary_counts': {
                'total_obligations': evaluation['total_obligations'],
                'total_incentives': evaluation['total_incentives'],
                'employer_triggers': len(evaluation['statutory_ladder'])
            },
            'immediate_priorities': immediate_items,
            'periodic_deadlines': periodic_items,
            'top_incentives': top_incentives,
            'documents_checklist': docs,
            'action_portals': portals
        }

    def answer_query(self, user_question, profile, lang='en'):
        """
        Natural language advisor that responds to specific queries through the mandatory RAG pipeline
        using Hugging Face Inference Providers.
        Enforces strict knowledge-base boundaries and refusal protocols.
        """
        from backend.services.rag_chat_service import rag_chat_service
        from backend.services.translation_service import translation_service

        plan = self.generate_action_plan(profile, lang)
        
        # Execute mandatory RAG pipeline with Hugging Face LLM layer
        rag_response = rag_chat_service.answer_question(user_question, profile, lang)
        answer_text = rag_response.get("text", "")

        # Dynamic translation if target language is not English
        if lang and lang != 'en' and answer_text:
            try:
                translated_ans = translation_service.translate_text(answer_text, target_lang=lang, preserve_tokens=True)
                answer_text = translated_ans
            except Exception:
                pass

        return {
            'question': user_question,
            'language': lang,
            'text': answer_text,
            'refusal': rag_response.get("refusal", False),
            'is_greeting': rag_response.get("is_greeting", False),
            'tool_called': rag_response.get("tool_called", "rag_huggingface_llm"),
            'grounded_source': rag_response.get("grounded_source", "published_rag_knowledge"),
            'citations': rag_response.get("citations", []),
            'suggestions': rag_response.get("suggestions", []),
            'available_topics': rag_response.get("available_topics", {}),
            'action_plan': plan,
            'metadata': rag_response.get("metadata", {})
        }

