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
