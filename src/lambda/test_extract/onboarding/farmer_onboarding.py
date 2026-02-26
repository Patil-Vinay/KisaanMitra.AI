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
            "name": f"""Extract the farmer's name from this message: "{user_message}"
Rules:
- Extract full name if provided
- Handle Hindi/Marathi names
- Return only the name, nothing else
- If no name found, return "unknown"

Examples:
"मेरा नाम राजेश पाटील है" → Rajesh Patil
"I am Suresh Kumar" → Suresh Kumar
"राम" → Ram

Name:""",
            
            "crops": f"""Extract crop names from this message: "{user_message}"
Rules:
- Extract all crops mentioned
- Return comma-separated list
- Handle Hindi/English crop names
- Standardize names (e.g., "टमाटर" → "tomato")
- If no crops found, return "unknown"

Examples:
"मैं गेहूं और धान उगाता हूं" → wheat, rice
"I grow tomato and onion" → tomato, onion
"सोयाबीन" → soybean

Crops:""",
            
            "land": f"""Extract land size in acres from this message: "{user_message}"
Rules:
- Extract numeric value only
- Convert to acres if in hectares (1 hectare = 2.47 acres)
- Handle Hindi numbers
- If no land size found, return "unknown"

Examples:
"मेरे पास 5 एकड़ जमीन है" → 5
"I have 2 hectares" → 4.94
"10 acre" → 10

Acres:""",
            
            "village": f"""Extract village/location name from this message: "{user_message}"
Rules:
- Extract village, town, or district name
- Handle Hindi/Marathi names
- Return only location name
- If no location found, return "unknown"

Examples:
"मैं पुणे के पास रहता हूं" → Pune
"I am from Nashik district" → Nashik
"गांव: शिरूर" → Shirur

Location:"""
        }
        
        prompt = prompts.get(field, "")
        if not prompt:
            return None
        
        try:
            response = bedrock.converse(
                modelId="us.amazon.nova-pro-v1:0",
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 100, "temperature": 0.2}
            )
            
            extracted = response["output"]["message"]["content"][0]["text"].strip()
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
        
        # State machine for onboarding flow
        if state == OnboardingState.NEW.value:
            # Welcome message
            response = """🙏 नमस्ते! KisaanMitra में आपका स्वागत है!

मैं आपका कृषि सहायक हूं। मैं आपकी मदद कर सकता हूं:
🌾 फसल रोग पहचान
📊 बाजार भाव
💰 बजट योजना

पहले मुझे आपके बारे में कुछ जानकारी चाहिए।

*आपका नाम क्या है?*"""
            
            self.update_onboarding_state(user_id, OnboardingState.ASKED_NAME.value, data)
            return response, False
        
        elif state == OnboardingState.ASKED_NAME.value:
            # Extract name
            name = self.extract_info_with_ai(user_message, "name")
            if name:
                data["name"] = name
                response = f"""धन्यवाद {name} जी! 🙏

*आप कौन सी फसलें उगाते हैं?*
(उदाहरण: गेहूं, धान, कपास)"""
                
                self.update_onboarding_state(user_id, OnboardingState.ASKED_CROPS.value, data)
                return response, False
            else:
                return "कृपया अपना नाम बताएं। उदाहरण: 'मेरा नाम राजेश है'", False
        
        elif state == OnboardingState.ASKED_CROPS.value:
            # Extract crops
            crops = self.extract_info_with_ai(user_message, "crops")
            if crops:
                data["crops"] = crops
                response = f"""बढ़िया! आप {crops} उगाते हैं। 🌾

*आपके पास कितनी जमीन है? (एकड़ में)*
(उदाहरण: 5 एकड़)"""
                
                self.update_onboarding_state(user_id, OnboardingState.ASKED_LAND.value, data)
                return response, False
            else:
                return "कृपया फसलों के नाम बताएं। उदाहरण: 'गेहूं और धान'", False
        
        elif state == OnboardingState.ASKED_LAND.value:
            # Extract land size
            land = self.extract_info_with_ai(user_message, "land")
            if land:
                data["land_acres"] = land
                response = f"""अच्छा! {land} एकड़ जमीन। 📏

*आप किस गांव/शहर से हैं?*
(उदाहरण: पुणे, नाशिक)"""
                
                self.update_onboarding_state(user_id, OnboardingState.ASKED_VILLAGE.value, data)
                return response, False
            else:
                return "कृपया जमीन का आकार बताएं। उदाहरण: '5 एकड़' या '2 हेक्टेयर'", False
        
        elif state == OnboardingState.ASKED_VILLAGE.value:
            # Extract village
            village = self.extract_info_with_ai(user_message, "village")
            if village:
                data["village"] = village
                data["phone"] = user_id
                data["registered_at"] = datetime.now().isoformat()
                
                # Save complete profile
                self.save_user_profile(user_id, data)
                
                # Mark onboarding as completed
                self.update_onboarding_state(user_id, OnboardingState.COMPLETED.value, data)
                
                response = f"""✅ *रजिस्ट्रेशन पूरा हुआ!*

📋 *आपकी जानकारी:*
👤 नाम: {data['name']}
🌾 फसलें: {data['crops']}
📏 जमीन: {data['land_acres']} एकड़
📍 गांव: {data['village']}

अब आप मुझसे कुछ भी पूछ सकते हैं:
• फसल की बीमारी के लिए फोटो भेजें
• बाजार भाव पूछें
• बजट योजना के लिए पूछें

कैसे मदद करूं? 😊"""
                
                return response, True
            else:
                return "कृपया अपना गांव/शहर बताएं। उदाहरण: 'पुणे' या 'नाशिक जिला'", False
        
        return "कुछ गलत हो गया। कृपया फिर से शुरू करें।", False
    
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
