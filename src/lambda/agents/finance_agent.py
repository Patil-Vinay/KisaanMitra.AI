"""
Finance Agent - Handles finance, budget, loan, and scheme queries
"""
import sys
sys.path.append('/opt/python')

from services.ai_service import AIService
from services.conversation_service import ConversationService

# Import optional modules
try:
    from onboarding.farmer_onboarding import onboarding_manager
    ONBOARDING_AVAILABLE = True
except:
    ONBOARDING_AVAILABLE = False


class FinanceAgent:
    """Handles finance-related queries with sub-routing"""
    
    @staticmethod
    def handle(user_message, user_id="unknown", language='hindi'):
        """Handle finance-related queries"""
        print(f"[FINANCE AGENT] Processing query: {user_message}, Language: {language}")
        
        # Get conversation history for context
        history = ConversationService.get_history(user_id, limit=10)
        context = ConversationService.build_context(history)
        
        # Determine finance sub-type
        finance_routing_prompt = f"""Analyze this farmer's finance query and determine the specific type.

Message: "{user_message}"

Finance types:
- schemes: Government schemes, subsidies, yojana
- budget: Budget planning, cost calculation, cultivation expenses, crop growing costs
- loan: Loan applications, credit, borrowing money
- general: Other finance questions

Reply with ONLY ONE WORD - the type (schemes/budget/loan/general).
No explanation."""

        try:
            finance_type = AIService.ask(finance_routing_prompt, skip_context=True).strip().lower()
            print(f"[FINANCE AGENT] Sub-type: {finance_type}")
        except Exception as e:
            print(f"[FINANCE AGENT] Routing failed: {e}, defaulting to general")
            finance_type = "general"
        
        # Get user profile for context
        profile_context = ""
        if ONBOARDING_AVAILABLE and user_id != "unknown":
            try:
                profile = onboarding_manager.get_user_profile(user_id)
                if profile:
                    profile_context = f"\nUser Profile: {profile.get('name', 'Farmer')} from {profile.get('village', 'India')}, {profile.get('land_acres', 'N/A')} acres, grows {profile.get('crops', 'various crops')}."
            except Exception as e:
                print(f"[FINANCE AGENT] Could not fetch profile: {e}")
        
        # Build system prompt based on type and language
        system_prompt = FinanceAgent._get_system_prompt(finance_type, language)
        
        # Generate response
        enhanced_message = user_message + profile_context
        result = AIService.ask(enhanced_message, system_prompt, context)
        
        return (result, True)
    
    @staticmethod
    def _get_system_prompt(finance_type, language):
        """Get appropriate system prompt based on finance type and language"""
        
        if language == 'english':
            if finance_type == "schemes":
                return """You are an expert on Indian government agricultural schemes and subsidies.

Format your response for WhatsApp:

🏛️ *Government Schemes for [Crop/Farming]*

*📋 Available Schemes:*

*1. [Scheme Name]*
💰 Benefit: [benefit details]
✅ Eligibility: [who can apply]

*2. [Scheme Name]*
💰 Benefit: [benefit details]
✅ Eligibility: [who can apply]

*🏛️ Where to Apply:*
Visit nearest Krishi Vigyan Kendra (KVK), CSC center, or district agriculture office

Include major schemes: PM-KISAN (₹6,000/year), KCC (₹3 lakh at 7%), PMFBY (crop insurance), etc.
Reply in simple English. Always use ₹ for currency."""
            
            elif finance_type == "loan":
                return """You are an agricultural finance expert specializing in farm loans.

Format your response:

🏦 *Agricultural Loan Options*

*📋 Recommended Schemes:*

*1. [Scheme Name]*
💰 Loan Amount: ₹[amount]
📊 Interest Rate: [rate]%
⏱️ Tenure: [period]

*✅ Eligibility:*
• Land ownership documents
• Aadhaar card
• Bank account

*🏛️ Where to Apply:*
Visit your nearest bank branch or CSC center

Reply in simple English. Always use ₹ for currency."""
            
            else:  # budget or general
                return """You are an expert agricultural finance advisor for Indian farmers.
Provide accurate, practical financial advice for farming operations.
Reply in simple, clear English. Be specific and actionable.
IMPORTANT: Always use ₹ (Rupee symbol) for Indian currency, never use $.
CRITICAL: Respond ONLY in English."""
        
        else:  # Hindi
            if finance_type == "schemes":
                return """आप भारतीय सरकारी कृषि योजनाओं और सब्सिडी के विशेषज्ञ हैं।

अपना जवाब WhatsApp के लिए फॉर्मेट करें:

🏛️ *[फसल/खेती] के लिए सरकारी योजनाएं*

*📋 उपलब्ध योजनाएं:*

*1. [योजना का नाम]*
💰 लाभ: [लाभ विवरण]
✅ पात्रता: [कौन आवेदन कर सकता है]

*2. [योजना का नाम]*
💰 लाभ: [लाभ विवरण]
✅ पात्रता: [कौन आवेदन कर सकता है]

*🏛️ कहां आवेदन करें:*
निकटतम कृषि विज्ञान केंद्र (KVK), CSC केंद्र, या जिला कृषि कार्यालय पर जाएं

प्रमुख योजनाएं शामिल करें: PM-KISAN (₹6,000/वर्ष), KCC (₹3 लाख 7% पर), PMFBY (फसल बीमा), आदि।
सरल हिंदी में जवाब दें। मुद्रा के लिए हमेशा ₹ का उपयोग करें।"""
            
            elif finance_type == "loan":
                return """आप कृषि ऋण में विशेषज्ञता रखने वाले एक विशेषज्ञ हैं।

अपना जवाब फॉर्मेट करें:

🏦 *कृषि ऋण विकल्प*

*📋 अनुशंसित योजनाएं:*

*1. [योजना का नाम]*
💰 ऋण राशि: ₹[राशि]
📊 ब्याज दर: [दर]%
⏱️ अवधि: [समय]

*✅ पात्रता:*
• भूमि स्वामित्व दस्तावेज
• आधार कार्ड
• बैंक खाता

*🏛️ कहां आवेदन करें:*
अपनी निकटतम बैंक शाखा या CSC केंद्र पर जाएं

सरल हिंदी में जवाब दें। मुद्रा के लिए हमेशा ₹ का उपयोग करें।"""
            
            else:  # budget or general
                return """आप भारतीय किसानों के लिए एक विशेषज्ञ कृषि वित्त सलाहकार हैं।
कृषि कार्यों के लिए सटीक, व्यावहारिक वित्तीय सलाह प्रदान करें।
सरल, स्पष्ट हिंदी में जवाब दें। विशिष्ट और कार्रवाई योग्य रहें।
महत्वपूर्ण: भारतीय मुद्रा के लिए हमेशा ₹ (रुपये का प्रतीक) का उपयोग करें।
अत्यंत महत्वपूर्ण: केवल हिंदी में जवाब दें।"""
