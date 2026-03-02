"""
Market Agent - Handles market price queries
"""
import sys
sys.path.append('/opt/python')

from services.ai_service import AIService

# Import optional modules
try:
    from farmer_onboarding import onboarding_manager
    ONBOARDING_AVAILABLE = True
except:
    ONBOARDING_AVAILABLE = False
    print("[MARKET AGENT] Onboarding module not available")

try:
    from market_data_sources import get_fast_market_prices, format_market_response_fast
    FAST_MARKET_DATA_AVAILABLE = True
except:
    FAST_MARKET_DATA_AVAILABLE = False


class MarketAgent:
    """Handles market price and mandi rate queries"""
    
    @staticmethod
    def handle(user_message, language='hindi', user_id="unknown"):
        """Handle market-related queries"""
        print(f"[MARKET AGENT] Processing query: {user_message}, Language: {language}")
        
        # ALWAYS fetch user profile first
        profile = None
        state_name = None
        district = None
        
        if ONBOARDING_AVAILABLE and user_id != "unknown":
            try:
                profile = onboarding_manager.get_user_profile(user_id)
                if profile:
                    village = profile.get('village', '')
                    district = profile.get('district', '')
                    print(f"[MARKET AGENT] Profile loaded: {village}, {district}")
                    
                    # Use district as state approximation for market data
                    if district:
                        state_name = district
            except Exception as e:
                print(f"[MARKET AGENT] Could not fetch profile: {e}")
        
        if language == 'english':
            system_prompt = """You are a market expert helping farmers.
Provide market prices and trends in simple English.
Keep it short (2-3 sentences) and practical.
CRITICAL: Respond ONLY in English. Do not use any Hindi words or phrases."""
        else:
            system_prompt = """आप एक बाजार विशेषज्ञ हैं जो किसानों की मदद कर रहे हैं।
सरल हिंदी में बाजार भाव और रुझान बताएं।
संक्षिप्त (2-3 वाक्य) और व्यावहारिक रखें।
अत्यंत महत्वपूर्ण: केवल हिंदी में जवाब दें। कोई अंग्रेजी शब्द या वाक्यांश का उपयोग न करें।"""
        
        # Extract crop name using AI
        detected_crop = AIService.extract_crop(user_message)
        
        if detected_crop and FAST_MARKET_DATA_AVAILABLE:
            # If no profile location, extract from message
            if not state_name:
                state_name = AIService.extract_state(user_message)
            
            print(f"[MARKET AGENT] Using market data for {detected_crop} in {state_name}")
            market_data = get_fast_market_prices(detected_crop, state_name)
            
            if market_data:
                print(f"[MARKET AGENT] Market data retrieved successfully")
                result = format_market_response_fast(detected_crop, market_data, language)
                return (result, True)
        
        # Fallback to AI with profile context
        profile_context = ""
        if profile:
            if language == 'english':
                profile_context = f"\n\nUser is from {district}. Provide location-specific advice."
            else:
                profile_context = f"\n\nकिसान {district} से है। स्थानीय सलाह दें।"
        
        enhanced_message = user_message + profile_context
        result = AIService.ask(enhanced_message, system_prompt)
        return (result, True)
