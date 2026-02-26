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
USER_PROFILE_TABLE = "kisaanmitra-user-profiles"
CONVERSATION_TABLE = "kisaanmitra-conversations"


class OnboardingState(Enum):
    """Onboarding flow states"""
    NEW = "new"
    ASKED_NAME = "asked_name"
    ASKED_CROPS = "asked_crops"
    ASKED_LAND = "asked_land"
    ASKED_VILLAGE = "asked_village"
    COMPLETED = "completed"


class FarmerOnboarding:
    """Manages farmer onboarding process"""
    
    def __init__(self):
        self.onboarding_table = dynamodb.Table(ONBOARDING_TABLE)
        self.profile_table = dynamodb.Table(USER_PROFILE_TABLE)
        self.conversation_table = dynamodb.Table(CONVERSATION_TABLE)
    
    def get_user_language(self, user_id: str) -> str:
        """Get user's language preference from conversation table"""
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
            
            "crops": f"""Extract ONLY crop names from: "{user_message}"

Reply with ONLY comma-separated crop names, no explanation.

Examples:
"मैं गेहूं और धान उगाता हूं" → wheat, rice
"I grow tomato and onion" → tomato, onion
"सोयाबीन" → soybean
"Sugarcane aur Soya Bean" → sugarcane, soybean

Reply with ONLY crop names:""",
            
            "land": f"""Extract ONLY land size number from: "{user_message}"

Reply with ONLY the number, no explanation.

Examples:
"मेरे पास 5 एकड़ जमीन है" → 5
"I have 2 hectares" → 4.94
"10 acre" → 10
"mere paas 3 acre hai" → 3

Reply with ONLY the number:""",
            
            "village": f"""Extract ONLY village/location name from: "{user_message}"

Reply with ONLY the location name, no explanation.

Examples:
"मैं पुणे के पास रहता हूं" → Pune
"I am from Nashik district" → Nashik
"गांव: शिरूर" → Shirur
"Kolhapur se hu" → Kolhapur

Reply with ONLY location name:"""
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
        lang = self.get_user_language(user_id)
        
        print(f"[ONBOARDING] User: {user_id}, State: {state}, Language: {lang}")
        
        # Bilingual messages
        messages = {
            "welcome": {
                "hindi": """🙏 नमस्ते! KisaanMitra में आपका स्वागत है!

मैं आपका कृषि सहायक हूं। मैं आपकी मदद कर सकता हूं:
🌾 फसल रोग पहचान
📊 बाजार भाव
💰 बजट योजना

पहले मुझे आपके बारे में कुछ जानकारी चाहिए।

*आपका नाम क्या है?*""",
                "english": """🙏 Welcome to KisaanMitra!

I'm your agricultural assistant. I can help you with:
🌾 Crop disease detection
📊 Market prices
💰 Budget planning

First, I need some information about you.

*What is your name?*"""
            },
            "ask_crops": {
                "hindi": """धन्यवाद {name} जी! 🙏

*आप कौन सी फसलें उगाते हैं?*
(उदाहरण: गेहूं, धान, कपास)""",
                "english": """Thank you {name}! 🙏

*Which crops do you grow?*
(Example: wheat, rice, cotton)"""
            },
            "ask_land": {
                "hindi": """बढ़िया! आप {crops} उगाते हैं। 🌾

*आपके पास कितनी जमीन है? (एकड़ में)*
(उदाहरण: 5 एकड़)""",
                "english": """Great! You grow {crops}. 🌾

*How much land do you have? (in acres)*
(Example: 5 acres)"""
            },
            "ask_village": {
                "hindi": """अच्छा! {land} एकड़ जमीन। 📏

*आप किस गांव/शहर से हैं?*
(उदाहरण: पुणे, नाशिक)""",
                "english": """Good! {land} acres of land. 📏

*Which village/city are you from?*
(Example: Pune, Nashik)"""
            },
            "completion": {
                "hindi": """✅ *रजिस्ट्रेशन पूरा हुआ!*

📋 *आपकी जानकारी:*
👤 नाम: {name}
🌾 फसलें: {crops}
📏 जमीन: {land_acres} एकड़
📍 गांव: {village}

अब आप मुझसे कुछ भी पूछ सकते हैं:
• फसल की बीमारी के लिए फोटो भेजें
• बाजार भाव पूछें
• बजट योजना के लिए पूछें

कैसे मदद करूं? 😊""",
                "english": """✅ *Registration Complete!*

📋 *Your Information:*
👤 Name: {name}
🌾 Crops: {crops}
📏 Land: {land_acres} acres
📍 Village: {village}

Now you can ask me anything:
• Send crop photo for disease detection
• Ask for market prices
• Request budget planning

How can I help? 😊"""
            },
            "retry_name": {
                "hindi": "कृपया अपना नाम बताएं। उदाहरण: 'मेरा नाम राजेश है'",
                "english": "Please tell me your name. Example: 'My name is Rajesh'"
            },
            "retry_crops": {
                "hindi": "कृपया फसलों के नाम बताएं। उदाहरण: 'गेहूं और धान'",
                "english": "Please tell me crop names. Example: 'wheat and rice'"
            },
            "retry_land": {
                "hindi": "कृपया जमीन का आकार बताएं। उदाहरण: '5 एकड़' या '2 हेक्टेयर'",
                "english": "Please tell me land size. Example: '5 acres' or '2 hectares'"
            },
            "retry_village": {
                "hindi": "कृपया अपना गांव/शहर बताएं। उदाहरण: 'पुणे' या 'नाशिक जिला'",
                "english": "Please tell me your village/city. Example: 'Pune' or 'Nashik district'"
            }
        }
        
        # State machine for onboarding flow
        if state == OnboardingState.NEW.value:
            response = messages["welcome"][lang]
            self.update_onboarding_state(user_id, OnboardingState.ASKED_NAME.value, data)
            return response, False
        
        elif state == OnboardingState.ASKED_NAME.value:
            name = self.extract_info_with_ai(user_message, "name")
            if name:
                data["name"] = name
                response = messages["ask_crops"][lang].format(name=name)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_CROPS.value, data)
                return response, False
            else:
                return messages["retry_name"][lang], False
        
        elif state == OnboardingState.ASKED_CROPS.value:
            crops = self.extract_info_with_ai(user_message, "crops")
            if crops:
                data["crops"] = crops
                response = messages["ask_land"][lang].format(crops=crops)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_LAND.value, data)
                return response, False
            else:
                return messages["retry_crops"][lang], False
        
        elif state == OnboardingState.ASKED_LAND.value:
            land = self.extract_info_with_ai(user_message, "land")
            if land:
                data["land_acres"] = land
                response = messages["ask_village"][lang].format(land=land)
                self.update_onboarding_state(user_id, OnboardingState.ASKED_VILLAGE.value, data)
                return response, False
            else:
                return messages["retry_land"][lang], False
        
        elif state == OnboardingState.ASKED_VILLAGE.value:
            village = self.extract_info_with_ai(user_message, "village")
            if village:
                data["village"] = village
                data["phone"] = user_id
                data["registered_at"] = datetime.now().isoformat()
                
                # Save complete profile
                self.save_user_profile(user_id, data)
                
                # Mark onboarding as completed
                self.update_onboarding_state(user_id, OnboardingState.COMPLETED.value, data)
                
                response = messages["completion"][lang].format(**data)
                return response, True
            else:
                return messages["retry_village"][lang], False
        
        error_msg = "कुछ गलत हो गया। कृपया फिर से शुरू करें।" if lang == "hindi" else "Something went wrong. Please start again."
        return error_msg, False
    
    def save_user_profile(self, user_id: str, data: Dict):
        """Save complete user profile to DynamoDB"""
        try:
            self.profile_table.put_item(
                Item={
                    "user_id": user_id,
                    "name": data.get("name", ""),
                    "crops": data.get("crops", ""),
                    "land_acres": data.get("land_acres", ""),
                    "village": data.get("village", ""),
                    "phone": data.get("phone", ""),
                    "registered_at": data.get("registered_at", datetime.now().isoformat()),
                    "profile_complete": True
                }
            )
            print(f"Profile saved for user {user_id}")
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


# Singleton instance
onboarding_manager = FarmerOnboarding()
