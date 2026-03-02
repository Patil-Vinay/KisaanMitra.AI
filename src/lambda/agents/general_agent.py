"""
General Agent - Handles general farming queries and weather
"""
from services.ai_service import AIService

try:
    from weather_service import get_weather_forecast, analyze_weather_for_farming, format_weather_response
    WEATHER_AVAILABLE = True
except:
    WEATHER_AVAILABLE = False


class GeneralAgent:
    """Handles general farming queries and weather"""
    
    @staticmethod
    def handle(user_message, user_id="unknown", language='hindi'):
        """Handle general queries"""
        print(f"[GENERAL AGENT] Processing query: {user_message}, Language: {language}")
        
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
                    return GeneralAgent._handle_weather(user_message, user_id, language)
            except Exception as e:
                print(f"[GENERAL AGENT] Weather check error: {e}")
        
        # General farming advice
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
        
        result = AIService.ask(user_message, system_prompt, skip_context=True)
        return (result, True)
    
    @staticmethod
    def _handle_weather(user_message, user_id, language):
        """Handle weather-specific queries"""
        location = None
        
        # PRIORITY 1: Check user profile for district
        try:
            from onboarding.farmer_onboarding import onboarding_manager
            if user_id != "unknown":
                profile = onboarding_manager.get_user_profile(user_id)
                if profile:
                    # Use district from profile (villages are too small for weather APIs)
                    location = profile.get('district')
                    if location:
                        print(f"[GENERAL AGENT] Using profile location: {location}")
        except Exception as e:
            print(f"[GENERAL AGENT] Could not get profile location: {e}")
        
        # PRIORITY 2: Extract location from message if not in profile
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
