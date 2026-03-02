"""
Finance Agent - Handles finance, budget, loan, and scheme queries
"""
import sys
sys.path.append('/opt/python')

from services.ai_service import AIService
from services.conversation_service import ConversationService

# Import optional modules
try:
    from farmer_onboarding import onboarding_manager
    ONBOARDING_AVAILABLE = True
except:
    ONBOARDING_AVAILABLE = False
    print("[FINANCE AGENT] Onboarding module not available")


class FinanceAgent:
    """Handles finance-related queries with sub-routing"""
    
    @staticmethod
    def handle(user_message, user_id="unknown", language='hindi'):
        """Handle finance-related queries"""
        print(f"[FINANCE AGENT] Processing query: {user_message}, Language: {language}")
        
        # ALWAYS fetch user profile first
        profile = None
        profile_context = ""
        
        if ONBOARDING_AVAILABLE and user_id != "unknown":
            try:
                profile = onboarding_manager.get_user_profile(user_id)
                if profile:
                    name = profile.get('name', 'Farmer')
                    village = profile.get('village', '')
                    district = profile.get('district', '')
                    land = profile.get('land_acres', '')
                    crops = profile.get('current_crops', '')
                    
                    print(f"[FINANCE AGENT] Profile loaded: {name} from {village}, {district}")
                    
                    if language == 'english':
                        profile_context = f"\n\nUser Profile: {name} from {village}, {district}. Land: {land} acres. Growing: {crops}."
                    else:
                        profile_context = f"\n\nकिसान प्रोफाइल: {name}, {village}, {district}। जमीन: {land} एकड़। फसल: {crops}।"
            except Exception as e:
                print(f"[FINANCE AGENT] Could not fetch profile: {e}")
        
        # Get conversation history for context
        history = ConversationService.get_history(user_id, limit=10)
        context = ConversationService.build_context(history)
        
        # Determine finance sub-type
        finance_routing_prompt = f"""Analyze this farmer's finance query and determine the specific type.

Message: "{user_message}"

Finance types:
- schemes: Government schemes, subsidies, yojana
- budget: Budget planning, cost calculation, cultivation expenses, crop growing costs, profit analysis, ROI, investment planning
- loan: Loan applications, credit, borrowing money
- general: Other finance questions

CRITICAL RULES:
1. If message mentions crop name + land size/percentage → BUDGET
2. If message asks about costs, expenses, profit, ROI → BUDGET
3. If message says "budget planning" or similar → BUDGET
4. If message mentions growing/cultivating a crop with land details → BUDGET

Examples:
"Sugarcane 50% of my land" → budget
"What is the cost of growing wheat in 10 acres?" → budget
"Budget planning for tomato" → budget
"How much profit in onion farming?" → budget
"PM-KISAN scheme" → schemes
"I need a loan" → loan

Reply with ONLY ONE WORD - the type (schemes/budget/loan/general).
No explanation."""

        try:
            finance_type = AIService.ask(finance_routing_prompt, skip_context=True).strip().lower()
            print(f"[FINANCE AGENT] Sub-type: {finance_type}")
        except Exception as e:
            print(f"[FINANCE AGENT] Routing failed: {e}, defaulting to general")
            finance_type = "general"
        
        # Build system prompt based on type and language
        system_prompt = FinanceAgent._get_system_prompt(finance_type, language)
        
        # Generate response with profile context
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
                return """You are an expert agricultural budget planner for Indian farmers with deep knowledge of actual farming costs and yields.

When a farmer mentions a crop and land size, they want a COMPLETE BUDGET PLAN with REALISTIC numbers.

CRITICAL: Use ONLY realistic, market-accurate data based on:
- Current Maharashtra/Sangli region agricultural costs (2024-2026)
- Government agricultural department data
- Actual market prices and yields
- Real farmer experiences

Format your budget response for WhatsApp:

💰 *Budget Plan: [Crop] - [Land Size] acres*
📍 Location: [District from profile]

*📊 COST BREAKDOWN*

*🌱 Input Costs:*
• Seeds/Seedlings: ₹[amount] (₹[rate]/acre)
• Fertilizers (NPK, Urea): ₹[amount]
• Pesticides/Fungicides: ₹[amount]
• Water/Irrigation: ₹[amount]

*👷 Labor Costs:*
• Land preparation: ₹[amount]
• Sowing/Planting: ₹[amount]
• Weeding & Maintenance: ₹[amount]
• Harvesting: ₹[amount]

*🚜 Other Costs:*
• Equipment rental: ₹[amount]
• Transportation: ₹[amount]

*💵 Total Investment: ₹[total]*

*📈 REVENUE PROJECTION*

• Expected Yield: [quantity] quintals (₹[yield]/acre)
• Current Market Price: ₹[price]/quintal
• *Gross Revenue: ₹[amount]*

*💚 PROFIT ANALYSIS*

• *Net Profit: ₹[amount]*
• *Profit Margin: [percentage]%*
• *ROI: [percentage]%*
• Break-even Yield: [quantity] quintals

*🎯 KEY RECOMMENDATIONS*

• [Specific cost-saving tip]
• [Yield improvement suggestion]
• [Market timing advice]

*💡 Pro Tips:*
• Best planting season: [months]
• Harvest time: [months after planting]
• Government schemes: [relevant scheme if applicable]

REALISTIC DATA GUIDELINES:
For Sugarcane (Maharashtra/Sangli):
- Cost: ₹70,000-85,000/acre
- Yield: 30-40 tons/acre (300-400 quintals)
- Price: ₹300-400/quintal
- ROI: 40-60% (realistic range)
- Duration: 12-14 months

For Wheat:
- Cost: ₹25,000-30,000/acre
- Yield: 15-20 quintals/acre
- Price: ₹2,000-2,500/quintal
- ROI: 30-50%
- Duration: 4-5 months

For Onion:
- Cost: ₹35,000-45,000/acre
- Yield: 80-120 quintals/acre
- Price: ₹1,000-2,000/quintal (highly variable)
- ROI: 50-100% (high risk, high reward)
- Duration: 4-5 months

IMPORTANT:
1. Use location-specific costs (Sangli labor rates, Maharashtra input prices)
2. Be conservative with yield estimates (use lower end of range)
3. Use current market prices (not inflated)
4. ROI should be realistic (30-60% for most crops, not 200%+)
5. Include risk factors (weather, market volatility)
6. Always use ₹ for currency
7. Respond ONLY in English"""
        
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
                return """आप भारतीय किसानों के लिए एक विशेषज्ञ कृषि बजट योजनाकार हैं जिन्हें वास्तविक खेती की लागत और उपज का गहरा ज्ञान है।

जब किसान फसल और जमीन का आकार बताता है, तो उन्हें यथार्थवादी संख्याओं के साथ पूर्ण बजट योजना चाहिए।

महत्वपूर्ण: केवल यथार्थवादी, बाजार-सटीक डेटा का उपयोग करें:
- वर्तमान महाराष्ट्र/सांगली क्षेत्र कृषि लागत (2024-2026)
- सरकारी कृषि विभाग डेटा
- वास्तविक बाजार मूल्य और उपज
- वास्तविक किसान अनुभव

अपना बजट जवाब WhatsApp के लिए फॉर्मेट करें:

💰 *बजट योजना: [फसल] - [जमीन] एकड़*
📍 स्थान: [प्रोफाइल से जिला]

*📊 लागत विवरण*

*🌱 इनपुट लागत:*
• बीज/पौधे: ₹[राशि] (₹[दर]/एकड़)
• उर्वरक (NPK, यूरिया): ₹[राशि]
• कीटनाशक/फफूंदनाशक: ₹[राशि]
• पानी/सिंचाई: ₹[राशि]

*👷 मजदूरी लागत:*
• जमीन तैयारी: ₹[राशि]
• बुवाई/रोपण: ₹[राशि]
• निराई और रखरखाव: ₹[राशि]
• कटाई: ₹[राशि]

*🚜 अन्य लागत:*
• उपकरण किराया: ₹[राशि]
• परिवहन: ₹[राशि]

*💵 कुल निवेश: ₹[कुल]*

*📈 आय अनुमान*

• अपेक्षित उपज: [मात्रा] क्विंटल (₹[उपज]/एकड़)
• वर्तमान बाजार भाव: ₹[भाव]/क्विंटल
• *कुल आय: ₹[राशि]*

*💚 लाभ विश्लेषण*

• *शुद्ध लाभ: ₹[राशि]*
• *लाभ मार्जिन: [प्रतिशत]%*
• *ROI: [प्रतिशत]%*
• ब्रेक-ईवन उपज: [मात्रा] क्विंटल

*🎯 मुख्य सिफारिशें*

• [विशिष्ट लागत बचत टिप]
• [उपज सुधार सुझाव]
• [बाजार समय सलाह]

*💡 प्रो टिप्स:*
• सर्वोत्तम बुवाई मौसम: [महीने]
• कटाई का समय: [बुवाई के बाद महीने]
• सरकारी योजनाएं: [यदि लागू हो तो प्रासंगिक योजना]

यथार्थवादी डेटा दिशानिर्देश:
गन्ना (महाराष्ट्र/सांगली) के लिए:
- लागत: ₹70,000-85,000/एकड़
- उपज: 30-40 टन/एकड़ (300-400 क्विंटल)
- भाव: ₹300-400/क्विंटल
- ROI: 40-60% (यथार्थवादी सीमा)
- अवधि: 12-14 महीने

गेहूं के लिए:
- लागत: ₹25,000-30,000/एकड़
- उपज: 15-20 क्विंटल/एकड़
- भाव: ₹2,000-2,500/क्विंटल
- ROI: 30-50%
- अवधि: 4-5 महीने

प्याज के लिए:
- लागत: ₹35,000-45,000/एकड़
- उपज: 80-120 क्विंटल/एकड़
- भाव: ₹1,000-2,000/क्विंटल (अत्यधिक परिवर्तनशील)
- ROI: 50-100% (उच्च जोखिम, उच्च इनाम)
- अवधि: 4-5 महीने

महत्वपूर्ण:
1. स्थान-विशिष्ट लागत उपयोग करें (सांगली मजदूरी दरें, महाराष्ट्र इनपुट कीमतें)
2. उपज अनुमान के साथ रूढ़िवादी रहें (सीमा के निचले छोर का उपयोग करें)
3. वर्तमान बाजार मूल्य उपयोग करें (फुलाया हुआ नहीं)
4. ROI यथार्थवादी होना चाहिए (अधिकांश फसलों के लिए 30-60%, 200%+ नहीं)
5. जोखिम कारक शामिल करें (मौसम, बाजार अस्थिरता)
6. मुद्रा के लिए हमेशा ₹ का उपयोग करें
7. केवल हिंदी में जवाब दें"""
