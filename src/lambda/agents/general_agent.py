"""
General Agent - Handles general farming queries and weather
"""
import sys
sys.path.append('/opt/python')

from services.ai_service import AIService

try:
    from weather_service import get_weather_forecast, analyze_weather_for_farming, format_weather_response
    WEATHER_AVAILABLE = True
except:
    WEATHER_AVAILABLE = False

try:
    from farmer_onboarding import onboarding_manager
    ONBOARDING_AVAILABLE = True
except:
    ONBOARDING_AVAILABLE = False
    print("[GENERAL AGENT] Onboarding module not available")


class GeneralAgent:
    """Handles general farming queries and weather"""
    
    @staticmethod
    def handle(user_message, user_id="unknown", language='hindi'):
        """Handle general queries"""
        print(f"[GENERAL AGENT] Processing query: {user_message}, Language: {language}")
        
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
                    crops = profile.get('current_crops', '')
                    land = profile.get('land_acres', '')
                    
                    print(f"[GENERAL AGENT] Profile loaded: {name} from {village}, {district}")
                    
                    if language == 'english':
                        profile_context = f"\n\nUser Profile: {name} from {village}, {district}. Land: {land} acres. Growing: {crops}."
                    else:
                        profile_context = f"\n\nकिसान प्रोफाइल: {name}, {village}, {district}। जमीन: {land} एकड़। फसल: {crops}।"
            except Exception as e:
                print(f"[GENERAL AGENT] Could not get profile: {e}")
        
        # Check if this is a community/village query (who else in village)
        if ONBOARDING_AVAILABLE and profile:
            community_check_prompt = f"""Is this asking about OTHER farmers in the village/community? Reply with ONLY "yes" or "no".

Message: "{user_message}"

Examples of community queries: 
- "who else in my village"
- "other farmers growing sugarcane"
- "farmers in my area"
- "who grows rice here"

Examples of non-community: 
- "how to grow tomato"
- "market price"
- "weather forecast"

Reply: """

            try:
                is_community = AIService.ask(community_check_prompt, skip_context=True).strip().lower()
                if is_community == "yes":
                    print(f"[GENERAL AGENT] Detected community query")
                    return GeneralAgent._handle_community_query(user_message, user_id, language, profile)
            except Exception as e:
                print(f"[GENERAL AGENT] Community check error: {e}")
        
        # Check if this is a weather query
        if WEATHER_AVAILABLE:
            weather_check_prompt = f"""Is this a weather-related query? Reply with ONLY "yes" or "no".

Message: "{user_message}"

Examples of weather queries: "what's the weather", "mausam kya hai", "will it rain", "temperature today"
Examples of non-weather: "how to grow tomato", "market price", "loan information"

Reply: """

            try:
                is_weather = AIService.ask(weather_check_prompt, skip_context=True).strip().lower()
                if is_weather == "yes":
                    print(f"[GENERAL AGENT] Detected weather query")
                    return GeneralAgent._handle_weather(user_message, user_id, language, profile)
            except Exception as e:
                print(f"[GENERAL AGENT] Weather check error: {e}")
        
        # General farming advice with profile context
        if language == 'english':
            system_prompt = """You are Kisaan Mitra, a friendly farming assistant.
Provide practical farming advice in simple English.
Keep responses concise (3-4 sentences).
CRITICAL: Respond ONLY in English."""
        else:
            system_prompt = """आप किसान मित्र हैं, एक मित्रवत कृषि सहायक।
सरल हिंदी में व्यावहारिक कृषि सलाह दें।
जवाब संक्षिप्त (3-4 वाक्य) रखें।
अत्यंत महत्वपूर्ण: केवल हिंदी में जवाब दें।"""
        
        enhanced_message = user_message + profile_context
        result = AIService.ask(enhanced_message, system_prompt, skip_context=True)
        return (result, True)
    
    @staticmethod
    def _handle_weather(user_message, user_id, language, profile=None):
        """Handle weather-specific queries"""
        location = None
        
        # PRIORITY 1: Use profile district if available
        if profile:
            location = profile.get('district')
            if location:
                print(f"[GENERAL AGENT] Using profile district: {location}")
        
        # PRIORITY 2: Try to get profile if not passed
        if not location and ONBOARDING_AVAILABLE and user_id != "unknown":
            try:
                if not profile:
                    profile = onboarding_manager.get_user_profile(user_id)
                if profile:
                    location = profile.get('district')
                    if location:
                        print(f"[GENERAL AGENT] Fetched profile district: {location}")
            except Exception as e:
                print(f"[GENERAL AGENT] Could not get profile location: {e}")
        
        # PRIORITY 3: Extract location from message if not in profile
        if not location:
            location_prompt = f"""Extract the city/location name from this message. If not mentioned, return "none".

Message: "{user_message}"

Reply with ONLY the location name (e.g., "Mumbai" or "Kolhapur") or "none". No explanation."""

            try:
                extracted = AIService.ask(location_prompt, skip_context=True).strip().title()
                location = extracted if extracted and extracted.lower() != "none" else "Pune"
                print(f"[GENERAL AGENT] Weather location from message: {location}")
            except:
                location = "Pune"
                print(f"[GENERAL AGENT] Using default location: Pune")
        
        try:
            weather = get_weather_forecast(location)
            weather_analysis = analyze_weather_for_farming(weather)
            result = format_weather_response(location, weather_analysis)
            return (result, True)
        except Exception as e:
            print(f"[GENERAL AGENT] Weather error: {e}")
            return ("Unable to fetch weather information. Please try again.", True)

    @staticmethod
    def _handle_community_query(user_message, user_id, language, profile):
        """Handle queries about other farmers in the village"""
        print(f"[GENERAL AGENT] Handling community query")
        
        village = profile.get('village', '')
        district = profile.get('district', '')
        user_name = profile.get('name', 'Farmer')
        
        if not village or not district:
            if language == 'english':
                return ("I need your village and district information to find other farmers. Please update your profile.", True)
            else:
                return ("अन्य किसानों को खोजने के लिए मुझे आपके गांव और जिले की जानकारी चाहिए। कृपया अपनी प्रोफाइल अपडेट करें।", True)
        
        # Extract crop from query using AI
        crop_prompt = f"""Extract the crop name from this query. If no specific crop mentioned, return "all".

Query: "{user_message}"

Examples:
"who else grows sugarcane" → sugarcane
"farmers in my village" → all
"other rice farmers" → rice

Reply with ONLY the crop name or "all":"""

        try:
            crop = AIService.ask(crop_prompt, skip_context=True).strip().lower()
            print(f"[GENERAL AGENT] Extracted crop: {crop}")
        except:
            crop = "all"
        
        # Query database for farmers
        try:
            all_farmers = onboarding_manager.get_farmers_by_location(village, district)
            print(f"[GENERAL AGENT] Found {len(all_farmers)} total farmers in {village}, {district}")
            
            # Filter by crop if specified
            filtered_farmers = []
            for farmer in all_farmers:
                # Skip the current user
                if farmer.get('user_id') == user_id:
                    continue
                
                # Filter by crop if not "all"
                if crop != "all":
                    farmer_crops = farmer.get('current_crops', '').lower()
                    if crop in farmer_crops:
                        filtered_farmers.append(farmer)
                else:
                    filtered_farmers.append(farmer)
            
            print(f"[GENERAL AGENT] After filtering: {len(filtered_farmers)} farmers")
            
            # Format response
            if len(filtered_farmers) == 0:
                if language == 'english':
                    if crop != "all":
                        return (f"You're currently the only registered farmer growing {crop} in {village} village on KisaanMitra. As more farmers join, you'll be able to connect with them! 🌾", True)
                    else:
                        return (f"You're currently the only registered farmer from {village} village on KisaanMitra. As more farmers join, you'll be able to connect with them! 🌾", True)
                else:
                    if crop != "all":
                        return (f"आप वर्तमान में KisaanMitra पर {village} गांव में {crop} उगाने वाले एकमात्र पंजीकृत किसान हैं। जैसे-जैसे अधिक किसान जुड़ेंगे, आप उनसे जुड़ पाएंगे! 🌾", True)
                    else:
                        return (f"आप वर्तमान में KisaanMitra पर {village} गांव के एकमात्र पंजीकृत किसान हैं। जैसे-जैसे अधिक किसान जुड़ेंगे, आप उनसे जुड़ पाएंगे! 🌾", True)
            
            # Build farmer list
            if language == 'english':
                if crop != "all":
                    response = f"🌾 *Found {len(filtered_farmers)} Farmer(s) Growing {crop.title()}*\n"
                else:
                    response = f"🌾 *Found {len(filtered_farmers)} Other Farmer(s) in {village}*\n"
                response += f"📍 Village: {village}, {district}\n\n"
                
                for i, farmer in enumerate(filtered_farmers[:10], 1):
                    name = farmer.get('name', 'Unknown')
                    crops = farmer.get('current_crops', 'N/A')
                    land = farmer.get('land_acres', 'N/A')
                    
                    response += f"*{i}. {name}*\n"
                    response += f"🌾 Crops: {crops}\n"
                    response += f"📏 Land: {land} acres\n\n"
                
                if len(filtered_farmers) > 10:
                    response += f"_...and {len(filtered_farmers) - 10} more farmers_\n\n"
                
                response += "💡 Connect with them to share farming tips and local insights!"
            else:
                if crop != "all":
                    response = f"🌾 *{crop.title()} उगाने वाले {len(filtered_farmers)} किसान मिले*\n"
                else:
                    response = f"🌾 *{village} में {len(filtered_farmers)} अन्य किसान मिले*\n"
                response += f"📍 गांव: {village}, {district}\n\n"
                
                for i, farmer in enumerate(filtered_farmers[:10], 1):
                    name = farmer.get('name', 'Unknown')
                    crops = farmer.get('current_crops', 'N/A')
                    land = farmer.get('land_acres', 'N/A')
                    
                    response += f"*{i}. {name}*\n"
                    response += f"🌾 फसलें: {crops}\n"
                    response += f"📏 जमीन: {land} एकड़\n\n"
                
                if len(filtered_farmers) > 10:
                    response += f"_...और {len(filtered_farmers) - 10} किसान_\n\n"
                
                response += "💡 खेती के टिप्स और स्थानीय जानकारी साझा करने के लिए उनसे जुड़ें!"
            
            return (response, True)
            
        except Exception as e:
            print(f"[GENERAL AGENT] Community query error: {e}")
            import traceback
            traceback.print_exc()
            if language == 'english':
                return ("Sorry, I couldn't fetch farmer information right now. Please try again.", True)
            else:
                return ("क्षमा करें, मैं अभी किसान की जानकारी नहीं ला सका। कृपया पुनः प्रयास करें।", True)
