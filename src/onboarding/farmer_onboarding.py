"""
Farmer Onboarding Module
Handles new user registration and data collection via WhatsApp
"""

import json
import boto3
from datetime import datetime
from typing import Dict, Optional, Tuple
from enum import Enum

# AWS Clients
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Tables
ONBOARDING_TABLE = "kisaanmitra-onboarding"
USER_PROFILE_TABLE = "kisaanmitra-farmer-profiles"  # Fixed: was kisaanmitra-user-profiles
CONVERSATION_TABLE = "kisaanmitra-conversations"


class OnboardingState(Enum):
    """Onboarding flow states - Comprehensive onboarding"""
    NEW = "new"
    ASKED_NAME = "asked_name"
    ASKED_VILLAGE = "asked_village"
    ASKED_DISTRICT = "asked_district"
    ASKED_LAND = "asked_land"
    ASKED_SOIL_TYPE = "asked_soil_type"
    ASKED_WATER_SOURCE = "asked_water_source"
    ASKED_CURRENT_CROPS = "asked_current_crops"
    ASKED_PAST_CROPS = "asked_past_crops"
    ASKED_FARMING_EXPERIENCE = "asked_farming_experience"
    ASKED_CHALLENGES = "asked_challenges"
    ASKED_GOALS = "asked_goals"
    COMPLETED = "completed"


class FarmerOnboarding:
    """Manages farmer onboarding process"""
    
    def __init__(self):
        self.onboarding_table = dynamodb.Table(ONBOARDING_TABLE)
        self.profile_table = dynamodb.Table(USER_PROFILE_TABLE)
        self.conversation_table = dynamodb.Table(CONVERSATION_TABLE)
    
    def get_user_language(self, user_id: str, first_message: str = "") -> str:
        """Get user's language preference from conversation table with auto-detection"""
        # Auto-detect English if first message is English greeting
        if first_message:
            msg_lower = first_message.lower().strip()
            english_greetings = ['hi', 'hii', 'hiii', 'hello', 'hey', 'helo', 'start', 'begin']
            if msg_lower in english_greetings:
                print(f"[LANGUAGE] Auto-detected English from greeting: {first_message}")
                # Save language preference
                try:
                    self.conversation_table.put_item(Item={
                        'user_id': user_id,
                        'timestamp': 'language_preference',
                        'language': 'english'
                    })
                except Exception as e:
                    print(f"[ERROR] Failed to save language: {e}")
                return 'english'
        
        # Otherwise fetch from DynamoDB
        try:
            response = self.conversation_table.get_item(
                Key={
                    "user_id": user_id,
                    "timestamp": "language_preference"
                }
            )
            if "Item" in response:
                return response["Item"].get("language", "hindi")
            return "hindi"  # Default to Hindi
        except Exception as e:
            print(f"Error getting language: {e}")
            return "hindi"
    
    def is_new_user(self, user_id: str) -> bool:
        """Check if user is new (no profile exists)"""
        try:
            response = self.profile_table.get_item(Key={"user_id": user_id})
            return "Item" not in response
        except Exception as e:
            print(f"Error checking user: {e}")
            return True
    
    def get_onboarding_state(self, user_id: str) -> Tuple[str, Dict]:
        """Get current onboarding state and collected data"""
        try:
            response = self.onboarding_table.get_item(Key={"user_id": user_id})
            if "Item" in response:
                item = response["Item"]
                return item.get("state", OnboardingState.NEW.value), item.get("data", {})
            return OnboardingState.NEW.value, {}
        except Exception as e:
            print(f"Error getting onboarding state: {e}")
            return OnboardingState.NEW.value, {}
    
    def update_onboarding_state(self, user_id: str, state: str, data: Dict):
        """Update onboarding state and data"""
        try:
            self.onboarding_table.put_item(
                Item={
                    "user_id": user_id,
                    "state": state,
                    "data": data,
                    "updated_at": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"Error updating onboarding state: {e}")
    
    def extract_info_with_ai(self, user_message: str, field: str) -> Optional[str]:
        """Use AI to extract information from user message"""
        prompts = {
            "name": f"""Extract ONLY the farmer's name from: "{user_message}"

Reply with ONLY the name, no explanation.

Examples:
"मेरा नाम राजेश पाटील है" → Rajesh Patil
"I am Suresh Kumar" → Suresh Kumar
"राम" → Ram
"Mera Naam Aditya Rane hai" → Aditya Rane

Reply with ONLY the name:""",
            
            "village": f"""Extract ONLY village/location name from: "{user_message}"

Reply with ONLY the location name, no explanation.

Examples:
"मैं पुणे के पास रहता हूं" → Pune
"I am from Nashik district" → Nashik
"गांव: शिरूर" → Shirur
"Kolhapur se hu" → Kolhapur
"Uruli Kanchan" → Uruli Kanchan

Reply with ONLY location name:""",
            
            "district": f"""Extract ONLY district name from: "{user_message}"

Reply with ONLY the district name, no explanation.

Examples:
"पुणे जिला" → Pune
"Nashik district" → Nashik
"Kolhapur" → Kolhapur
"मैं सतारा से हूं" → Satara

Reply with ONLY district name:""",
            
            "land": f"""Extract ONLY land size number from: "{user_message}"

Reply with ONLY the number, no explanation.

Examples:
"मेरे पास 5 एकड़ जमीन है" → 5
"I have 2 hectares" → 4.94
"10 acre" → 10
"mere paas 3 acre hai" → 3

Reply with ONLY the number:""",
            
            "soil_type": f"""Extract ONLY soil type from: "{user_message}"

Reply with ONLY the soil type, no explanation.

Examples:
"काली मिट्टी" → Black Cotton Soil
"Red soil" → Red Soil
"Laterite" → Laterite Soil
"मेरी जमीन में लाल मिट्टी है" → Red Soil

Common types: Black Cotton Soil, Red Soil, Laterite Soil, Alluvial Soil, Sandy Soil

Reply with ONLY soil type:""",
            
            "water_source": f"""Extract ONLY water source from: "{user_message}"

Reply with ONLY the water source, no explanation.

Examples:
"बोरवेल से पानी मिलता है" → Borewell
"I have drip irrigation" → Drip Irrigation
"नहर" → Canal
"बारिश पर निर्भर" → Rainfed

Common sources: Borewell, Canal, Well, Drip Irrigation, Rainfed

Reply with ONLY water source:""",
            
            "crops": f"""Extract ONLY crop names from: "{user_message}"

Reply with ONLY comma-separated crop names, no explanation.

Examples:
"मैं गेहूं और धान उगाता हूं" → wheat, rice
"I grow tomato and onion" → tomato, onion
"सोयाबीन" → soybean
"Sugarcane aur Soya Bean" → sugarcane, soybean

Reply with ONLY crop names:""",
            
            "experience": f"""Extract ONLY years of farming experience from: "{user_message}"

Reply with ONLY the number, no explanation.

Examples:
"मैं 10 साल से खेती कर रहा हूं" → 10
"I have 5 years experience" → 5
"15 saal" → 15

Reply with ONLY the number:""",
            
            "challenges": f"""Extract farming challenges from: "{user_message}"

Reply with a brief summary.

Examples:
"पानी की कमी और कीट समस्या" → Water scarcity, pest issues
"Market prices are low" → Low market prices
"बारिश नहीं होती" → Lack of rainfall

Reply with brief summary:""",
            
            "goals": f"""Extract farming goals from: "{user_message}"

Reply with a brief summary.

Examples:
"मैं अपनी आय बढ़ाना चाहता हूं" → Increase income
"I want to grow organic crops" → Grow organic crops
"नई फसलें उगाना चाहता हूं" → Try new crops

Reply with brief summary:"""
        }
        
        prompt = prompts.get(field, "")
        if not prompt:
            return None
        
        try:
            response = bedrock.converse(
                modelId="us.amazon.nova-pro-v1:0",
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 20, "temperature": 0.1}  # Very low tokens and temp for concise output
            )
            
            extracted = response["output"]["message"]["content"][0]["text"].strip()
            
            # Clean up the response - take only the first line if multi-line
            if '\n' in extracted:
                extracted = extracted.split('\n')[0].strip()
            
            # Remove common prefixes
            for prefix in ["Name:", "Crops:", "Acres:", "Location:", "Reply:", "Answer:"]:
                if extracted.startswith(prefix):
                    extracted = extracted[len(prefix):].strip()
            
            return extracted if extracted.lower() != "unknown" else None
        except Exception as e:
            print(f"Error extracting {field}: {e}")
            return None
    
    def process_onboarding_message(self, user_id: str, user_message: str) -> Tuple[str, bool]:
        """
        Process user message during onboarding
        Returns: (response_message, is_completed)
        """
        state, data = self.get_onboarding_state(user_id)
        
        # For NEW users, detect language from first message
        if state == OnboardingState.NEW.value:
            lang = self.get_user_language(user_id, user_message)
        else:
            lang = self.get_user_language(user_id)
        
        print(f"[ONBOARDING] User: {user_id}, State: {state}, Language: {lang}, Message: {user_message}")
        
        # Comprehensive bilingual messages
        messages = {
            "welcome": {
                "hindi": """🙏 नमस्ते! KisaanMitra में आपका स्वागत है!

मैं आपका व्यक्तिगत कृषि सहायक हूं। मैं आपकी मदद कर सकता हूं:
🌾 फसल रोग पहचान और उपचार
📊 लाइव बाजार भाव
💰 विस्तृत बजट योजना
🌦️ मौसम आधारित सलाह
📅 फसल कैलेंडर और रिमाइंडर

आपको सबसे अच्छी सलाह देने के लिए, मुझे आपके बारे में कुछ जानकारी चाहिए।

*आपका नाम क्या है?* 👤""",
                "english": """🙏 Welcome to KisaanMitra!

I'm your personal agricultural assistant. I can help you with:
🌾 Crop disease detection & treatment
📊 Live market prices
💰 Detailed budget planning
🌦️ Weather-based advice
📅 Crop calendar & reminders

To give you the best advice, I need some information about you.

*What is your name?* 👤"""
            },
            "ask_village": {
                "hindi": """धन्यवाद {name} जी! 🙏

*आप किस गांव से हैं?* 🏘️
(उदाहरण: उरुली कांचन, घुंकी, सायखेडा)""",
                "english": """Thank you {name}! 🙏

*Which village are you from?* 🏘️
(Example: Uruli Kanchan, Ghunki, Saikheda)"""
            },
            "ask_district": {
                "hindi": """अच्छा! {village} गांव। 🏘️

*आप किस जिले में हैं?* 🏛️
(उदाहरण: पुणे, कोल्हापुर, नाशिक, सतारा)""",
                "english": """Good! {village} village. 🏘️

*Which district are you in?* 🏛️
(Example: Pune, Kolhapur, Nashik, Satara)"""
            },
            "ask_land": {
                "hindi": """{district} जिला, बढ़िया! 🏛️

*आपके पास कितनी जमीन है?* 📏
(एकड़ में बताएं - उदाहरण: 5 एकड़, 2.5 एकड़)""",
                "english": """{district} district, great! 🏛️

*How much land do you have?* 📏
(In acres - Example: 5 acres, 2.5 acres)"""
            },
            "ask_soil_type": {
                "hindi": """{land} एकड़ जमीन, अच्छा! 📏

*आपकी जमीन में किस प्रकार की मिट्टी है?* 🌱

विकल्प:
• काली मिट्टी (Black Cotton Soil)
• लाल मिट्टी (Red Soil)
• लेटराइट मिट्टी (Laterite Soil)
• जलोढ़ मिट्टी (Alluvial Soil)
• रेतीली मिट्टी (Sandy Soil)
• अन्य

(उदाहरण: काली मिट्टी)""",
                "english": """{land} acres of land, good! 📏

*What type of soil do you have?* 🌱

Options:
• Black Cotton Soil
• Red Soil
• Laterite Soil
• Alluvial Soil
• Sandy Soil
• Other

(Example: Black Cotton Soil)"""
            },
            "ask_water_source": {
                "hindi": """{soil_type} मिट्टी, समझ गया! 🌱

*पानी का मुख्य स्रोत क्या है?* 💧

विकल्प:
• बोरवेल (Borewell)
• कुआं (Well)
• नहर (Canal)
• ड्रिप सिंचाई (Drip Irrigation)
• बारिश पर निर्भर (Rainfed)
• अन्य

(उदाहरण: बोरवेल)""",
                "english": """{soil_type} soil, understood! 🌱

*What is your main water source?* 💧

Options:
• Borewell
• Well
• Canal
• Drip Irrigation
• Rainfed
• Other

(Example: Borewell)"""
            },
            "ask_current_crops": {
                "hindi": """{water_source} से पानी, बढ़िया! 💧

*अभी आप कौन सी फसलें उगा रहे हैं?* 🌾
(उदाहरण: गेहूं, टमाटर, प्याज)

अगर कोई फसल नहीं है तो "कोई नहीं" लिखें।""",
                "english": """{water_source} water source, great! 💧

*Which crops are you currently growing?* 🌾
(Example: wheat, tomato, onion)

If no crops, write "none"."""
            },
            "ask_past_crops": {
                "hindi": """अच्छा! अभी {current_crops} उगा रहे हैं। 🌾

*पिछले 2-3 सालों में आपने कौन सी फसलें उगाई हैं?* 📅
(उदाहरण: धान, कपास, सोयाबीन, गन्ना)

यह जानकारी मुझे बेहतर सलाह देने में मदद करेगी।""",
                "english": """Good! Currently growing {current_crops}. 🌾

*Which crops have you grown in the past 2-3 years?* 📅
(Example: rice, cotton, soybean, sugarcane)

This helps me give you better advice."""
            },
            "ask_farming_experience": {
                "hindi": """बढ़िया! आपने {past_crops} उगाई हैं। 📅

*आपको खेती का कितने साल का अनुभव है?* ⭐
(उदाहरण: 10 साल, 5 साल)""",
                "english": """Great! You've grown {past_crops}. 📅

*How many years of farming experience do you have?* ⭐
(Example: 10 years, 5 years)"""
            },
            "ask_challenges": {
                "hindi": """{experience} साल का अनुभव, बहुत अच्छा! ⭐

*खेती में आपको कौन सी मुख्य समस्याएं आती हैं?* 🤔

उदाहरण:
• पानी की कमी
• कीट और रोग
• कम बाजार भाव
• मजदूरों की कमी
• मौसम की अनिश्चितता

(अपनी समस्याएं बताएं)""",
                "english": """{experience} years of experience, excellent! ⭐

*What are the main challenges you face in farming?* 🤔

Examples:
• Water scarcity
• Pests and diseases
• Low market prices
• Labor shortage
• Weather uncertainty

(Tell me your challenges)"""
            },
            "ask_goals": {
                "hindi": """समझ गया! आपकी समस्याएं: {challenges} 🤔

*आपके खेती के लक्ष्य क्या हैं?* 🎯

उदाहरण:
• आय बढ़ाना
• नई फसलें आजमाना
• जैविक खेती करना
• कम लागत में खेती
• बेहतर उपज

(अपने लक्ष्य बताएं)""",
                "english": """Understood! Your challenges: {challenges} 🤔

*What are your farming goals?* 🎯

Examples:
• Increase income
• Try new crops
• Organic farming
• Reduce costs
• Better yields

(Tell me your goals)"""
            },
            "completion": {
                "hindi": """✅ *रजिस्ट्रेशन पूरा हुआ!*

🎉 धन्यवाद {name} जी! अब मैं आपको व्यक्तिगत सलाह दे सकता हूं।

📋 *आपकी प्रोफाइल:*
👤 नाम: {name}
🏘️ गांव: {village}
🏛️ जिला: {district}
📏 जमीन: {land_acres} एकड़
🌱 मिट्टी: {soil_type}
💧 पानी: {water_source}
🌾 वर्तमान फसलें: {current_crops}
📅 पिछली फसलें: {past_crops}
⭐ अनुभव: {experience} साल
🤔 समस्याएं: {challenges}
🎯 लक्ष्य: {goals}

अब मैं आपकी मदद कर सकता हूं:
• फसल रोग पहचान (फोटो भेजें)
• आपके क्षेत्र के लाइव बाजार भाव
• आपकी जमीन के लिए बजट योजना
• मौसम आधारित सलाह
• फसल सुझाव

*कैसे मदद करूं?* 😊""",
                "english": """✅ *Registration Complete!*

🎉 Thank you {name}! Now I can give you personalized advice.

📋 *Your Profile:*
👤 Name: {name}
🏘️ Village: {village}
🏛️ District: {district}
📏 Land: {land_acres} acres
🌱 Soil: {soil_type}
💧 Water: {water_source}
🌾 Current crops: {current_crops}
📅 Past crops: {past_crops}
⭐ Experience: {experience} years
🤔 Challenges: {challenges}
🎯 Goals: {goals}

Now I can help you with:
• Crop disease detection (send photo)
• Live market prices for your area
• Budget planning for your land
• Weather-based advice
• Crop recommendations

*How can I help?* 😊"""
            },
            "retry_name": {
                "hindi": "कृपया अपना नाम बताएं। उदाहरण: 'मेरा नाम राजेश है' या 'राजेश पाटील'",
                "english": "Please tell me your name. Example: 'My name is Rajesh' or 'Rajesh Patil'"
            },
            "retry_village": {
                "hindi": "कृपया अपना गांव बताएं। उदाहरण: 'उरुली कांचन' या 'मैं घुंकी से हूं'",
                "english": "Please tell me your village. Example: 'Uruli Kanchan' or 'I am from Ghunki'"
            },
            "retry_district": {
                "hindi": "कृपया अपना जिला बताएं। उदाहरण: 'पुणे' या 'कोल्हापुर जिला'",
                "english": "Please tell me your district. Example: 'Pune' or 'Kolhapur district'"
            },
            "retry_land": {
                "hindi": "कृपया जमीन का आकार बताएं। उदाहरण: '5 एकड़' या '2.5 एकड़'",
                "english": "Please tell me land size. Example: '5 acres' or '2.5 acres'"
            },
            "retry_soil_type": {
                "hindi": "कृपया मिट्टी का प्रकार बताएं। उदाहरण: 'काली मिट्टी' या 'लाल मिट्टी'",
                "english": "Please tell me soil type. Example: 'Black Cotton Soil' or 'Red Soil'"
            },
            "retry_water_source": {
                "hindi": "कृपया पानी का स्रोत बताएं। उदाहरण: 'बोरवेल' या 'नहर'",
                "english": "Please tell me water source. Example: 'Borewell' or 'Canal'"
            },
            "retry_current_crops": {
                "hindi": "कृपया वर्तमान फसलें बताएं। उदाहरण: 'गेहूं और टमाटर' या 'कोई नहीं'",
                "english": "Please tell me current crops. Example: 'wheat and tomato' or 'none'"
            },
            "retry_past_crops": {
                "hindi": "कृपया पिछली फसलें बताएं। उदाहरण: 'धान, कपास, सोयाबीन'",
                "english": "Please tell me past crops. Example: 'rice, cotton, soybean'"
            },
            "retry_experience": {
                "hindi": "कृपया अनुभव के साल बताएं। उदाहरण: '10 साल' या '5'",
                "english": "Please tell me years of experience. Example: '10 years' or '5'"
            },
            "retry_challenges": {
                "hindi": "कृपया अपनी मुख्य समस्याएं बताएं। उदाहरण: 'पानी की कमी और कीट'",
                "english": "Please tell me your main challenges. Example: 'water scarcity and pests'"
            },
            "retry_goals": {
                "hindi": "कृपया अपने लक्ष्य बताएं। उदाहरण: 'आय बढ़ाना और नई फसलें'",
                "english": "Please tell me your goals. Example: 'increase income and try new crops'"
            }
        }
        
        # Comprehensive state machine for onboarding flow
        if state == OnboardingState.NEW.value:
            response = messages["welcome"][lang]
            self.update_onboarding_state(user_id, OnboardingState.ASKED_NAME.value, data)
            return response, False
        
        elif state == OnboardingState.ASKED_NAME.value:
            name = self.extract_info_with_ai(user_message, "name")
            if name:
                data["name"] = name
                response = messages["ask_village"][lang].format(name=name)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_VILLAGE.value, data)
                return response, False
            else:
                return messages["retry_name"][lang], False
        
        elif state == OnboardingState.ASKED_VILLAGE.value:
            village = self.extract_info_with_ai(user_message, "village")
            if village:
                data["village"] = village
                response = messages["ask_district"][lang].format(village=village)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_DISTRICT.value, data)
                return response, False
            else:
                return messages["retry_village"][lang], False
        
        elif state == OnboardingState.ASKED_DISTRICT.value:
            district = self.extract_info_with_ai(user_message, "district")
            if district:
                data["district"] = district
                response = messages["ask_land"][lang].format(district=district)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_LAND.value, data)
                return response, False
            else:
                return messages["retry_district"][lang], False
        
        elif state == OnboardingState.ASKED_LAND.value:
            land = self.extract_info_with_ai(user_message, "land")
            if land:
                data["land_acres"] = land
                response = messages["ask_soil_type"][lang].format(land=land)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_SOIL_TYPE.value, data)
                return response, False
            else:
                return messages["retry_land"][lang], False
        
        elif state == OnboardingState.ASKED_SOIL_TYPE.value:
            soil_type = self.extract_info_with_ai(user_message, "soil_type")
            if soil_type:
                data["soil_type"] = soil_type
                response = messages["ask_water_source"][lang].format(soil_type=soil_type)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_WATER_SOURCE.value, data)
                return response, False
            else:
                return messages["retry_soil_type"][lang], False
        
        elif state == OnboardingState.ASKED_WATER_SOURCE.value:
            water_source = self.extract_info_with_ai(user_message, "water_source")
            if water_source:
                data["water_source"] = water_source
                response = messages["ask_current_crops"][lang].format(water_source=water_source)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_CURRENT_CROPS.value, data)
                return response, False
            else:
                return messages["retry_water_source"][lang], False
        
        elif state == OnboardingState.ASKED_CURRENT_CROPS.value:
            current_crops = self.extract_info_with_ai(user_message, "crops")
            if current_crops:
                data["current_crops"] = current_crops
                response = messages["ask_past_crops"][lang].format(current_crops=current_crops)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_PAST_CROPS.value, data)
                return response, False
            else:
                return messages["retry_current_crops"][lang], False
        
        elif state == OnboardingState.ASKED_PAST_CROPS.value:
            past_crops = self.extract_info_with_ai(user_message, "crops")
            if past_crops:
                data["past_crops"] = past_crops
                response = messages["ask_farming_experience"][lang].format(past_crops=past_crops)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_FARMING_EXPERIENCE.value, data)
                return response, False
            else:
                return messages["retry_past_crops"][lang], False
        
        elif state == OnboardingState.ASKED_FARMING_EXPERIENCE.value:
            experience = self.extract_info_with_ai(user_message, "experience")
            if experience:
                data["experience"] = experience
                response = messages["ask_challenges"][lang].format(experience=experience)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_CHALLENGES.value, data)
                return response, False
            else:
                return messages["retry_experience"][lang], False
        
        elif state == OnboardingState.ASKED_CHALLENGES.value:
            challenges = self.extract_info_with_ai(user_message, "challenges")
            if challenges:
                data["challenges"] = challenges
                response = messages["ask_goals"][lang].format(challenges=challenges)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_GOALS.value, data)
                return response, False
            else:
                return messages["retry_challenges"][lang], False
        
        elif state == OnboardingState.ASKED_GOALS.value:
            goals = self.extract_info_with_ai(user_message, "goals")
            if goals:
                data["goals"] = goals
                data["phone"] = user_id
                data["registered_at"] = datetime.now().isoformat()
                
                # Save complete profile
                self.save_user_profile(user_id, data)
                
                # Mark onboarding as completed
                self.update_onboarding_state(user_id, OnboardingState.COMPLETED.value, data)
                
                response = messages["completion"][lang].format(**data)
                return response, True
            else:
                return messages["retry_goals"][lang], False
        
        error_msg = "कुछ गलत हो गया। कृपया फिर से शुरू करें।" if lang == "hindi" else "Something went wrong. Please start again."
        return error_msg, False
    
    def save_user_profile(self, user_id: str, data: Dict):
        """Save complete user profile to DynamoDB with all comprehensive fields"""
        try:
            self.profile_table.put_item(
                Item={
                    "user_id": user_id,
                    "name": data.get("name", ""),
                    "village": data.get("village", ""),
                    "district": data.get("district", ""),
                    "land_acres": data.get("land_acres", ""),
                    "soil_type": data.get("soil_type", ""),
                    "water_source": data.get("water_source", ""),
                    "current_crops": data.get("current_crops", ""),
                    "past_crops": data.get("past_crops", ""),
                    "experience": data.get("experience", ""),
                    "challenges": data.get("challenges", ""),
                    "goals": data.get("goals", ""),
                    "phone": data.get("phone", ""),
                    "registered_at": data.get("registered_at", datetime.now().isoformat()),
                    "profile_complete": True
                }
            )
            print(f"✅ Comprehensive profile saved for user {user_id}")
            print(f"   - Name: {data.get('name')}")
            print(f"   - Village: {data.get('village')}, District: {data.get('district')}")
            print(f"   - Land: {data.get('land_acres')} acres, Soil: {data.get('soil_type')}")
            print(f"   - Water: {data.get('water_source')}")
            print(f"   - Current crops: {data.get('current_crops')}")
            print(f"   - Experience: {data.get('experience')} years")
        except Exception as e:
            print(f"Error saving profile: {e}")
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        try:
            response = self.profile_table.get_item(Key={"user_id": user_id})
            return response.get("Item")
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def get_farmers_by_location(self, village: str, district: str) -> list:
        """
        Get all farmers in a specific village/district
        
        Args:
            village: Village name
            district: District name
        
        Returns:
            List of farmer profiles
        """
        try:
            # Scan the profile table for farmers in this location
            # Note: In production, use a GSI (Global Secondary Index) for better performance
            response = self.profile_table.scan(
                FilterExpression='village = :v AND district = :d',
                ExpressionAttributeValues={
                    ':v': village,
                    ':d': district
                }
            )
            
            farmers = response.get('Items', [])
            print(f"[ONBOARDING] Found {len(farmers)} farmers in {village}, {district}")
            return farmers
            
        except Exception as e:
            print(f"[ONBOARDING ERROR] Failed to get farmers by location: {e}")
            return []


# Singleton instance
onboarding_manager = FarmerOnboarding()
