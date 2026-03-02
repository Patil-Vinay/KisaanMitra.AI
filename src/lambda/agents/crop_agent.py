"""
Crop Agent - Handles crop health queries
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
    print("[CROP AGENT] Onboarding module not available")

try:
    from disease_tracker import hyperlocal_tracker
    HYPERLOCAL_AVAILABLE = True
except:
    HYPERLOCAL_AVAILABLE = False
    print("[CROP AGENT] Hyperlocal module not available")

try:
    from weather_service import get_weather_forecast, analyze_weather_for_farming
    WEATHER_AVAILABLE = True
except:
    WEATHER_AVAILABLE = False


class CropAgent:
    """Handles crop health and disease queries"""
    
    @staticmethod
    def handle(user_message, user_id="unknown", language='hindi', location=None):
        """Handle crop-related text queries"""
        print(f"[CROP AGENT] Processing query: {user_message}, Language: {language}")
        
        # ALWAYS fetch user profile first
        profile = None
        profile_context = ""
        village = None
        district = None
        crops = None
        
        if ONBOARDING_AVAILABLE and user_id != "unknown":
            try:
                profile = onboarding_manager.get_user_profile(user_id)
                if profile:
                    name = profile.get('name', 'Farmer')
                    village = profile.get('village')
                    district = profile.get('district')
                    crops = profile.get('current_crops') or profile.get('crops')
                    land = profile.get('land_acres', '')
                    
                    print(f"[CROP AGENT] Profile loaded: {name} from {village}, {district}. Crops: {crops}")
                    
                    if language == 'english':
                        profile_context = f"\n\nUser Profile: {name} from {village}, {district}. Land: {land} acres. Currently growing: {crops}."
                    else:
                        profile_context = f"\n\nकिसान प्रोफाइल: {name}, {village}, {district}। जमीन: {land} एकड़। वर्तमान फसल: {crops}।"
            except Exception as e:
                print(f"[CROP AGENT] Failed to get profile: {e}")
        
        # Use district for weather if no location provided
        if not location and district:
            location = district
        
        # Get weather context
        weather_context = ""
        if WEATHER_AVAILABLE and location:
            try:
                print(f"[CROP AGENT] Fetching weather for {location}")
                forecast = get_weather_forecast(location)
                analysis = analyze_weather_for_farming(forecast)
                
                if language == 'english':
                    weather_context = f"\n\nCurrent Weather Context for {location}:\n"
                    weather_context += f"Temperature: {analysis['min_temp']}°C - {analysis['max_temp']}°C\n"
                    weather_context += f"Rain expected: {'Yes, in ' + str(analysis['days_until_rain']) + ' days' if analysis['rain_expected'] else 'No rain in next 3 days'}\n"
                    weather_context += "Weather advice: " + ", ".join(analysis['recommendations'])
                else:
                    weather_context = f"\n\n{location} का मौसम:\n"
                    weather_context += f"तापमान: {analysis['min_temp']}°C - {analysis['max_temp']}°C\n"
                    weather_context += f"बारिश: {'हां, ' + str(analysis['days_until_rain']) + ' दिन में' if analysis['rain_expected'] else 'अगले 3 दिन में नहीं'}\n"
                    weather_context += "मौसम सलाह: " + ", ".join(analysis['recommendations'])
            except Exception as e:
                print(f"[CROP AGENT] Weather error: {e}")
        
        # PRIORITY 1: Check hyperlocal data FIRST
        if HYPERLOCAL_AVAILABLE and village and crops:
            try:
                print(f"[CROP AGENT] Checking hyperlocal data for {village}, {crops}")
                
                disease_alert = hyperlocal_tracker.format_disease_alert(village, crops, language)
                nearby_reports = hyperlocal_tracker.get_nearby_diseases(village, district, days=30, crop=crops)
                
                if nearby_reports:
                    print(f"[CROP AGENT] Found {len(nearby_reports)} disease reports")
                    hyperlocal_response = disease_alert + "\n\n"
                    
                    diseases = list(set([r.get('disease_name') for r in nearby_reports if r.get('disease_name')]))
                    
                    treatments_found = False
                    for disease in diseases[:3]:
                        treatment_msg = hyperlocal_tracker.format_treatment_recommendations(disease, language)
                        hyperlocal_response += treatment_msg + "\n"
                        if "✅" in treatment_msg:
                            treatments_found = True
                    
                    # Add footer
                    if language == 'hindi':
                        if treatments_found:
                            hyperlocal_response += "\n💡 *सलाह*: ये उपचार आपके क्षेत्र के किसानों द्वारा सफल पाए गए हैं। अपने स्थानीय कृषि विशेषज्ञ से भी परामर्श करें।"
                        else:
                            hyperlocal_response += "\n💡 *सलाह*: कृपया अपने नजदीकी कृषि विशेषज्ञ या कृषि विज्ञान केंद्र से संपर्क करें।"
                    else:
                        if treatments_found:
                            hyperlocal_response += "\n💡 *Advice*: These treatments worked for farmers in your area. Also consult your local agricultural expert."
                        else:
                            hyperlocal_response += "\n💡 *Advice*: Please contact your nearest agricultural expert or Krishi Vigyan Kendra."
                    
                    if hyperlocal_response.strip():
                        print(f"[CROP AGENT] Using community data")
                        return (hyperlocal_response, True)
            except Exception as e:
                print(f"[CROP AGENT] Hyperlocal error: {e}")
        
        # FALLBACK: Use AI with full context
        print(f"[CROP AGENT] Using AI fallback with profile context")
        
        if language == 'english':
            system_prompt = """You are a helpful farming assistant. 
Help farmers with crop diseases, pests, and treatments.
Reply in simple English. Keep it short (2-3 sentences) and practical.
CRITICAL: Respond ONLY in English. Do not use any Hindi words or phrases."""
        else:
            system_prompt = """आप एक सहायक कृषि सलाहकार हैं।
किसानों को फसल रोग, कीट और उपचार में मदद करें।
सरल हिंदी में जवाब दें। संक्षिप्त (2-3 वाक्य) और व्यावहारिक रखें।
अत्यंत महत्वपूर्ण: केवल हिंदी में जवाब दें। कोई अंग्रेजी शब्द या वाक्यांश का उपयोग न करें।"""
        
        enhanced_message = user_message + profile_context + weather_context
        result = AIService.ask(enhanced_message, system_prompt)
        
        return (result, True)
