import json
import urllib3
import os
import boto3
import base64
import time
from datetime import datetime, timedelta
from decimal import Decimal

# Import LangGraph router
try:
    from agent_router import route_message_with_ai, fallback_keyword_routing
    LANGGRAPH_AVAILABLE = True
except ImportError:
    print("LangGraph not available, using fallback routing")
    LANGGRAPH_AVAILABLE = False

# Import fast market data sources
try:
    from market_data_sources import get_fast_market_prices, format_market_response_fast
    FAST_MARKET_DATA_AVAILABLE = True
except ImportError:
    print("Fast market data not available")
    FAST_MARKET_DATA_AVAILABLE = False

# Import onboarding and knowledge graph
import sys
sys.path.append('/opt/python')  # Lambda layer path
try:
    from onboarding.farmer_onboarding import onboarding_manager
    from knowledge_graph.village_graph import knowledge_graph
    ONBOARDING_AVAILABLE = True
    print("✅ Onboarding module loaded successfully")
except ImportError as e:
    print(f"❌ Onboarding module not available: {e}")
    import traceback
    traceback.print_exc()
    ONBOARDING_AVAILABLE = False
except Exception as e:
    print(f"❌ Error loading onboarding module: {e}")
    import traceback
    traceback.print_exc()
    ONBOARDING_AVAILABLE = False

# Import new hackathon features
try:
    from whatsapp_interactive import (
        create_main_menu, create_crop_selection_list, create_back_button,
        create_quick_actions, send_interactive_message, create_language_selection,
        add_navigation_text
    )
    INTERACTIVE_MESSAGES_AVAILABLE = True
    print("✅ WhatsApp Interactive Messages loaded successfully")
except ImportError as e:
    print(f"❌ Interactive messages not available: {e}")
    INTERACTIVE_MESSAGES_AVAILABLE = False

try:
    from navigation_controller import NavigationController
    NAVIGATION_AVAILABLE = True
    print("✅ Navigation Controller loaded successfully")
except ImportError as e:
    print(f"❌ Navigation Controller not available: {e}")
    NAVIGATION_AVAILABLE = False

try:
    from ai_orchestrator import get_orchestrator
    AI_ORCHESTRATOR_AVAILABLE = True
    print("✅ AI Orchestrator loaded successfully")
except ImportError as e:
    print(f"❌ AI Orchestrator not available: {e}")
    AI_ORCHESTRATOR_AVAILABLE = False

try:
    from enhanced_disease_detection import (
        detect_disease_with_confidence, format_disease_response,
        save_disease_detection
    )
    ENHANCED_DISEASE_DETECTION_AVAILABLE = True
    print("✅ Enhanced Disease Detection loaded successfully")
except ImportError as e:
    print(f"❌ Enhanced disease detection not available: {e}")
    ENHANCED_DISEASE_DETECTION_AVAILABLE = False

try:
    from reminder_manager import get_crop_calendar, format_reminders_message
    REMINDERS_AVAILABLE = True
    print("✅ Smart Reminders loaded successfully")
except ImportError as e:
    print(f"❌ Reminders not available: {e}")
    REMINDERS_AVAILABLE = False

try:
    from weather_service import get_weather_forecast, analyze_weather_for_farming, format_weather_response
    WEATHER_AVAILABLE = True
    print("✅ Weather Service loaded successfully")
except ImportError as e:
    print(f"❌ Weather service not available: {e}")
    WEATHER_AVAILABLE = False

http = urllib3.PoolManager()

# Environment variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mySecret_123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
CROP_HEALTH_API_KEY = os.environ.get("CROP_HEALTH_API_KEY")
AGMARKNET_API_KEY = os.environ.get("AGMARKNET_API_KEY")

# AWS clients
# Use direct Anthropic API for better accuracy and higher rate limits
USE_ANTHROPIC_DIRECT = os.environ.get('USE_ANTHROPIC_DIRECT', 'true').lower() == 'true'

if USE_ANTHROPIC_DIRECT:
    print("[INIT] Using direct Anthropic Claude API")
    from anthropic_client import get_anthropic_client
    bedrock = get_anthropic_client()
else:
    print("[INIT] Using AWS Bedrock")
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")  # Cross-region inference

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
s3 = boto3.client("s3", region_name="ap-south-1")

# Tables
conversation_table = dynamodb.Table("kisaanmitra-conversations")
market_data_table = dynamodb.Table("kisaanmitra-market-data")
finance_table = dynamodb.Table("kisaanmitra-finance")

def get_user_language(user_id, message_text=""):
    """Get user's language preference from DynamoDB with auto-detection"""
    # Auto-detect English if message contains only English characters
    if message_text:
        # Check if message is primarily English (no Devanagari script)
        has_hindi = any('\u0900' <= char <= '\u097F' for char in message_text)
        is_english_greeting = message_text.lower().strip() in ['hi', 'hii', 'hiii', 'hello', 'hey', 'helo']
        
        if not has_hindi and (is_english_greeting or len(message_text.split()) > 2):
            # Likely English message, auto-set language
            print(f"[LANGUAGE] Auto-detected English from message: {message_text[:50]}")
            set_user_language(user_id, 'english')
            return 'english'
    
    # Otherwise, fetch from DynamoDB
    try:
        response = conversation_table.get_item(
            Key={'user_id': user_id, 'timestamp': 'language_preference'}
        )
        if 'Item' in response:
            lang = response['Item'].get('language', 'hindi')
            return lang
    except Exception as e:
        print(f"[ERROR] Failed to get language preference: {e}")
    
    return 'hindi'  # Default

def set_user_language(user_id, language):
    """Set user's language preference in DynamoDB"""
    try:
        conversation_table.put_item(Item={
            'user_id': user_id,
            'timestamp': 'language_preference',
            'language': language
        })
        print(f"[LANGUAGE] Set {user_id} language to: {language}")
    except Exception as e:
        print(f"[ERROR] Failed to save language preference: {e}")

# City to State mapping for accurate location detection
CITY_TO_STATE = {
    # Maharashtra
    "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra",
    "nashik": "Maharashtra", "aurangabad": "Maharashtra", "solapur": "Maharashtra",
    "kolhapur": "Maharashtra", "amravati": "Maharashtra", "sangli": "Maharashtra",
    "malegaon": "Maharashtra", "jalgaon": "Maharashtra", "akola": "Maharashtra",
    "latur": "Maharashtra", "dhule": "Maharashtra", "ahmednagar": "Maharashtra",
    
    # Punjab
    "ludhiana": "Punjab", "amritsar": "Punjab", "jalandhar": "Punjab",
    "patiala": "Punjab", "bathinda": "Punjab", "mohali": "Punjab",
    "hoshiarpur": "Punjab", "batala": "Punjab", "pathankot": "Punjab",
    
    # Haryana
    "faridabad": "Haryana", "gurgaon": "Haryana", "gurugram": "Haryana",
    "panipat": "Haryana", "ambala": "Haryana", "yamunanagar": "Haryana",
    "rohtak": "Haryana", "hisar": "Haryana", "karnal": "Haryana",
    
    # Uttar Pradesh
    "lucknow": "Uttar Pradesh", "kanpur": "Uttar Pradesh", "ghaziabad": "Uttar Pradesh",
    "agra": "Uttar Pradesh", "meerut": "Uttar Pradesh", "varanasi": "Uttar Pradesh",
    "allahabad": "Uttar Pradesh", "prayagraj": "Uttar Pradesh", "bareilly": "Uttar Pradesh",
    
    # Gujarat
    "ahmedabad": "Gujarat", "surat": "Gujarat", "vadodara": "Gujarat",
    "rajkot": "Gujarat", "bhavnagar": "Gujarat", "jamnagar": "Gujarat",
    "junagadh": "Gujarat", "gandhinagar": "Gujarat", "anand": "Gujarat",
    
    # Rajasthan
    "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "kota": "Rajasthan",
    "bikaner": "Rajasthan", "udaipur": "Rajasthan", "ajmer": "Rajasthan",
    "bhilwara": "Rajasthan", "alwar": "Rajasthan", "bharatpur": "Rajasthan",
    
    # Madhya Pradesh
    "indore": "Madhya Pradesh", "bhopal": "Madhya Pradesh", "jabalpur": "Madhya Pradesh",
    "gwalior": "Madhya Pradesh", "ujjain": "Madhya Pradesh", "sagar": "Madhya Pradesh",
    "dewas": "Madhya Pradesh", "satna": "Madhya Pradesh", "ratlam": "Madhya Pradesh",
    
    # Karnataka
    "bangalore": "Karnataka", "bengaluru": "Karnataka", "mysore": "Karnataka",
    "hubli": "Karnataka", "mangalore": "Karnataka", "belgaum": "Karnataka",
    "gulbarga": "Karnataka", "davanagere": "Karnataka", "bellary": "Karnataka",
    
    # Tamil Nadu
    "chennai": "Tamil Nadu", "coimbatore": "Tamil Nadu", "madurai": "Tamil Nadu",
    "tiruchirappalli": "Tamil Nadu", "salem": "Tamil Nadu", "tirunelveli": "Tamil Nadu",
    "tiruppur": "Tamil Nadu", "erode": "Tamil Nadu", "vellore": "Tamil Nadu",
    
    # Andhra Pradesh
    "visakhapatnam": "Andhra Pradesh", "vijayawada": "Andhra Pradesh", "guntur": "Andhra Pradesh",
    "nellore": "Andhra Pradesh", "kurnool": "Andhra Pradesh", "kakinada": "Andhra Pradesh",
    "rajahmundry": "Andhra Pradesh", "tirupati": "Andhra Pradesh", "kadapa": "Andhra Pradesh",
    
    # Telangana
    "hyderabad": "Telangana", "warangal": "Telangana", "nizamabad": "Telangana",
    "karimnagar": "Telangana", "khammam": "Telangana", "ramagundam": "Telangana",
    
    # West Bengal
    "kolkata": "West Bengal", "howrah": "West Bengal", "durgapur": "West Bengal",
    "asansol": "West Bengal", "siliguri": "West Bengal", "bardhaman": "West Bengal",
    
    # Kerala
    "thiruvananthapuram": "Kerala", "kochi": "Kerala", "kozhikode": "Kerala",
    "thrissur": "Kerala", "kollam": "Kerala", "palakkad": "Kerala",
    "malappuram": "Kerala", "kannur": "Kerala", "kottayam": "Kerala",
    
    # Bihar
    "patna": "Bihar", "gaya": "Bihar", "bhagalpur": "Bihar",
    "muzaffarpur": "Bihar", "purnia": "Bihar", "darbhanga": "Bihar",
    
    # Odisha
    "bhubaneswar": "Odisha", "cuttack": "Odisha", "rourkela": "Odisha",
    "berhampur": "Odisha", "sambalpur": "Odisha", "puri": "Odisha"
}

# Conversation memory cache (in-memory for Lambda)
conversation_memory = {}

# ─── Conversation Memory ────────────────────────────────────────────────────

def get_conversation_history(user_id, limit=3):
    """Get recent conversation history from DynamoDB (reduced limit for speed)"""
    try:
        print(f"[DEBUG] Fetching conversation history for user: {user_id}, limit: {limit}")
        response = conversation_table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
            ScanIndexForward=False,
            Limit=limit
        )
        items = response.get("Items", [])
        print(f"[DEBUG] Retrieved {len(items)} conversation items from DynamoDB")
        return items
    except Exception as e:
        print(f"[ERROR] Error fetching conversation history: {e}")
        return []

def save_conversation(user_id, message, response, agent_type):
    """Save conversation to DynamoDB"""
    try:
        print(f"[DEBUG] Saving conversation - User: {user_id}, Agent: {agent_type}")
        print(f"[DEBUG] Message length: {len(message)} chars, Response length: {len(response)} chars")
        conversation_table.put_item(Item={
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "response": response,
            "agent": agent_type
        })
        print(f"[DEBUG] Conversation saved successfully to DynamoDB")
    except Exception as e:
        print(f"[ERROR] Error saving conversation: {e}")

def build_context_from_history(history):
    """Build enhanced context string from conversation history (optimized)"""
    if not history or len(history) == 0:
        print("[DEBUG] No conversation history available")
        return ""
    
    print(f"[DEBUG] Building context from {len(history)} history items")
    context = "Previous conversation:\n"
    for item in reversed(history[-2:]):  # Only last 2 messages for speed
        msg = item.get('message', '')
        resp = item.get('response', '')[:200]  # Truncate responses
        
        context += f"User: {msg}\n"
        context += f"Bot: {resp}...\n"
    
    print(f"[DEBUG] Context built, length: {len(context)} chars")
    return context

# ─── Bedrock with Cross-Region Inference ────────────────────────────────────

def ask_bedrock(prompt, system_prompt=None, conversation_context="", skip_context=False):
    """Call Bedrock using cross-region inference profile with context and retry logic"""
    try:
        print(f"[DEBUG] Calling Bedrock - Model: Nova Pro")
        print(f"[DEBUG] Prompt length: {len(prompt)} chars")
        
        # OPTIMIZATION: Skip context for simple queries (saves tokens and time)
        if skip_context:
            full_prompt = prompt
            print(f"[DEBUG] Skipping context for speed")
        else:
            full_prompt = conversation_context + prompt if conversation_context else prompt
            print(f"[DEBUG] Context length: {len(conversation_context)} chars")
        
        if system_prompt:
            print(f"[DEBUG] System prompt: {system_prompt[:100] if system_prompt else 'None'}...")
        
        messages = [{"role": "user", "content": [{"text": full_prompt}]}]
        
        kwargs = {
            "modelId": "us.amazon.nova-pro-v1:0",  # Amazon Nova Pro - High throughput, great quality
            "messages": messages,
            "inferenceConfig": {"maxTokens": 2000, "temperature": 0.6}  # Balanced for natural responses
        }
        
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]
        
        print(f"[DEBUG] Sending request to Bedrock...")
        
        # OPTIMIZED: Faster retry logic
        max_retries = 3
        base_wait = 2  # Reduced from 5
        
        for attempt in range(max_retries):
            try:
                response = bedrock.converse(**kwargs)
                result = response["output"]["message"]["content"][0]["text"]
                print(f"[DEBUG] Bedrock response received, length: {len(result)} chars")
                return result
            except Exception as e:
                if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                    wait_time = base_wait * (attempt + 1)  # 2, 4, 6 seconds
                    print(f"[WARNING] Throttled, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    raise
        
    except Exception as e:
        print(f"[ERROR] Bedrock error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return "I'm having trouble helping you right now. Please try again."

# ─── Crop Health API ─────────────────────────────────────────────────────────

def download_whatsapp_image(media_id):
    """Download image from WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    
    response = http.request("GET", url, headers=headers)
    media_info = json.loads(response.data)
    media_url = media_info.get("url")
    
    if not media_url:
        raise Exception("Could not get media URL")
    
    response = http.request("GET", media_url, headers=headers)
    return response.data

def analyze_crop_image(image_bytes):
    """Analyze crop image using Kindwise API"""
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    payload = {
        "images": [image_base64],
        "similar_images": True,
        "latitude": 20.5937,
        "longitude": 78.9629
    }
    
    headers = {
        "Api-Key": CROP_HEALTH_API_KEY,
        "Content-Type": "application/json"
    }
    
    response = http.request(
        "POST",
        "https://crop.kindwise.com/api/v1/identification",
        body=json.dumps(payload),
        headers=headers
    )
    
    return json.loads(response.data)

def format_crop_result(result):
    """Format crop analysis in English"""
    suggestions = result.get("result", {}).get("disease", {}).get("suggestions", [])
    
    if not suggestions:
        return "I analyzed your crop image but couldn't detect any specific disease. Please try with a clearer image."
    
    message = "🌿 *Crop Disease Analysis*\n\n"
    
    for i, suggestion in enumerate(suggestions[:3], 1):
        name = suggestion.get("name", "Unknown")
        probability = suggestion.get("probability", 0) * 100
        message += f"{i}. *{name}*\n"
        message += f"   Confidence: {probability:.1f}%\n\n"
    
    # Get treatment recommendation from Bedrock
    disease_name = suggestions[0].get("name", "")
    treatment_prompt = f"Suggest treatment for {disease_name} disease in crops. Reply in 2-3 sentences in simple English."
    treatment = ask_bedrock(treatment_prompt)
    
    message += f"💊 *Treatment:*\n{treatment}\n\n"
    message += "💡 For best results, consult a local agriculture expert."
    
    return message

# ─── Agent Router ────────────────────────────────────────────────────────────

def route_message(user_message, user_id="unknown"):
    """
    Route message to appropriate agent using LangGraph AI routing
    Falls back to keyword matching if LangGraph is unavailable
    """
    print(f"[DEBUG] ===== ROUTING MESSAGE =====")
    print(f"[DEBUG] User ID: {user_id}")
    print(f"[DEBUG] Message: {user_message}")
    print(f"[DEBUG] LangGraph Available: {LANGGRAPH_AVAILABLE}")
    
    if LANGGRAPH_AVAILABLE:
        try:
            print(f"[DEBUG] Using LangGraph AI routing...")
            # Use AI-powered routing with LangGraph
            agent = route_message_with_ai(user_message, user_id, bedrock)
            print(f"[INFO] ✅ LangGraph AI routing selected: {agent.upper()}")
            return agent
        except Exception as e:
            print(f"[ERROR] LangGraph routing failed: {e}, using fallback")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
    
    # Fallback to keyword-based routing
    print(f"[DEBUG] Using fallback keyword-based routing...")
    agent = fallback_keyword_routing(user_message)
    print(f"[INFO] ✅ Fallback routing selected: {agent.upper()}")
    return agent


def fallback_keyword_routing(user_message):
    """Simple keyword-based routing as fallback"""
    msg_lower = user_message.lower()
    
    # Greetings - keep it casual
    greetings = ["hi", "hello", "hey", "namaste", "नमस्ते", "हाय", "हेलो"]
    if any(greeting == msg_lower.strip() for greeting in greetings):
        return "greeting"
    
    # Crop problems - disease, pest, leaf issues
    crop_keywords = ["disease", "pest", "leaf", "yellow", "spots", "dying", "बीमारी", "रोग", "पत्ती", "कीट"]
    if any(kw in msg_lower for kw in crop_keywords):
        return "crop"
    
    # Market prices - mandi rates
    market_keywords = ["price", "mandi", "rate", "sell", "market", "भाव", "कीमत", "मंडी", "बाजार"]
    if any(kw in msg_lower for kw in market_keywords):
        return "market"
    
    # Finance - budget, loan, schemes, structure, model, planting
    finance_keywords = ["budget", "loan", "scheme", "money", "cost", "finance", "financial", 
                        "structure", "model", "planting", "investment", "expense",
                        "बजट", "लोन", "योजना", "खर्च", "वित्त"]
    if any(kw in msg_lower for kw in finance_keywords):
        return "finance"
    
    # Crop recommendation - which crop, what to plant, suggest crop
    recommendation_keywords = ["which crop", "what crop", "suggest crop", "recommend crop", 
                               "should i plant", "what to plant", "which to grow", "what to grow",
                               "कौन सी फसल", "क्या लगाएं", "क्या उगाएं", "फसल सुझाव"]
    if any(kw in msg_lower for kw in recommendation_keywords):
        print(f"[DEBUG] Detected crop recommendation query")
        return "general"
    
    # Default - friendly chat (general agent handles crop recommendations too)
    print(f"[DEBUG] No specific keywords matched, routing to general agent")
    return "general"

def handle_crop_query(user_message, user_id="unknown", language='hindi'):
    """Handle crop-related text queries with language support"""
    print(f"[DEBUG] ===== CROP AGENT =====")
    print(f"[DEBUG] Processing crop query: {user_message}, Language: {language}")
    
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
    
    result = ask_bedrock(user_message, system_prompt)
    
    # Add navigation text
    if INTERACTIVE_MESSAGES_AVAILABLE:
        result = add_navigation_text(result, language)
    
    print(f"[DEBUG] Crop agent response generated")
    return result

def get_mandi_prices(commodity, state="Maharashtra", limit=10):
    """Fetch real-time mandi prices from AgMarkNet API"""
    if not AGMARKNET_API_KEY:
        return None
    
    try:
        params = {
            "api-key": AGMARKNET_API_KEY,
            "format": "json",
            "limit": limit,
            "filters[commodity]": commodity,
            "filters[state]": state
        }
        
        url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        response = http.request("GET", url)
        if response.status == 200:
            data = json.loads(response.data)
            return data.get("records", [])
        return None
    except Exception as e:
        print(f"Error fetching mandi prices: {e}")
        return None

def get_cached_market_data(crop_name):
    """Get cached market data from DynamoDB"""
    try:
        response = market_data_table.get_item(Key={"crop_name": crop_name.lower()})
        if "Item" in response:
            return response["Item"]
        return None
    except Exception as e:
        print(f"Error fetching cached data: {e}")
        return None

def cache_market_data(crop_name, data):
    """Cache market data in DynamoDB"""
    try:
        market_data_table.put_item(
            Item={
                "crop_name": crop_name.lower(),
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "ttl": int((datetime.now() + timedelta(hours=6)).timestamp())
            }
        )
    except Exception as e:
        print(f"Error caching data: {e}")

def analyze_price_trend(prices):
    """Analyze price trend from historical data"""
    if not prices or len(prices) < 2:
        return {"trend": "insufficient_data"}
    
    recent_avg = sum([float(p.get("modal_price", 0)) for p in prices[:3]]) / min(3, len(prices))
    older_avg = sum([float(p.get("modal_price", 0)) for p in prices[-3:]]) / min(3, len(prices))
    
    change_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
    
    return {
        "trend": "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable",
        "recent_avg": round(recent_avg, 2),
        "older_avg": round(older_avg, 2),
        "change_percent": round(change_pct, 2)
    }

def handle_market_query(user_message, language='hindi'):
    """Handle market-related queries with AI state extraction and language support"""
    print(f"[DEBUG] ===== MARKET AGENT =====")
    print(f"[DEBUG] Processing market query: {user_message}, Language: {language}")
    
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
    
    # Extract crop name
    common_crops = ["wheat", "rice", "cotton", "soybean", "onion", "potato", "tomato", "sugarcane"]
    detected_crop = None
    message_lower = user_message.lower()
    
    print(f"[DEBUG] Searching for crop keywords in message...")
    for crop in common_crops:
        if crop in message_lower:
            detected_crop = crop
            print(f"[DEBUG] ✅ Detected crop: {crop}")
            break
    
    if not detected_crop:
        print(f"[DEBUG] No crop detected in message")
    
    if detected_crop and FAST_MARKET_DATA_AVAILABLE:
        # Extract state using AI (no hardcoding!)
        print(f"[DEBUG] Using AI to extract state for market query...")
        state_name = extract_state_with_ai(user_message, bedrock)
        
        print(f"[DEBUG] Using market data for {detected_crop} in {state_name}")
        # Use market data with AI-extracted state
        market_data = get_fast_market_prices(detected_crop, state_name)
        
        if market_data:
            print(f"[DEBUG] Market data retrieved successfully")
            print(f"[DEBUG] Average price: ₹{market_data.get('average_price')}, Trend: {market_data.get('trend')}")
            result = format_market_response_fast(detected_crop, market_data, language)
            
            # Add navigation text
            if INTERACTIVE_MESSAGES_AVAILABLE:
                result = add_navigation_text(result, language)
            
            return result
        else:
            print(f"[DEBUG] No market data found for {detected_crop}")
    
    # Fallback to AI for general market questions
    print(f"[DEBUG] Falling back to AI for market query")
    result = ask_bedrock(user_message, system_prompt)
    
    # Add navigation text
    if INTERACTIVE_MESSAGES_AVAILABLE:
        result = add_navigation_text(result, language)
    
    return result

def extract_crop_with_ai(user_message, bedrock_client, conversation_history=""):
    """Extract crop name from user message using keyword matching (no AI call to avoid throttling)"""
    print(f"[DEBUG] Extracting crop name using keyword matching...")
    print(f"[DEBUG] Message: {user_message}")
    
    # Common crop names and variations
    crop_keywords = {
        'rice': ['rice', 'paddy', 'धान', 'चावल'],
        'wheat': ['wheat', 'गेहूं'],
        'onion': ['onion', 'प्याज'],
        'potato': ['potato', 'आलू'],
        'tomato': ['tomato', 'टमाटर'],
        'cotton': ['cotton', 'कपास'],
        'sugarcane': ['sugarcane', 'sugar cane', 'गन्ना'],
        'soybean': ['soybean', 'soya', 'सोयाबीन'],
        'maize': ['maize', 'corn', 'मक्का'],
        'chilly': ['chilly', 'chilli', 'pepper', 'मिर्च'],
        'brinjal': ['brinjal', 'eggplant', 'बैंगन'],
        'cabbage': ['cabbage', 'पत्तागोभी'],
        'cauliflower': ['cauliflower', 'फूलगोभी'],
        'groundnut': ['groundnut', 'peanut', 'मूंगफली'],
        'turmeric': ['turmeric', 'हल्दी'],
        'ginger': ['ginger', 'अदरक'],
        'garlic': ['garlic', 'लहसुन'],
        'banana': ['banana', 'केला'],
        'mango': ['mango', 'आम'],
        'grapes': ['grapes', 'grape', 'अंगूर'],
        'pomegranate': ['pomegranate', 'अनार'],
        'papaya': ['papaya', 'पपीता'],
        'mushroom': ['mushroom', 'मशरूम'],
    }
    
    message_lower = user_message.lower()
    
    # Check for crop keywords
    for crop, keywords in crop_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                print(f"[INFO] ✅ Extracted crop: {crop}")
                return crop
    
    print(f"[WARNING] No crop found in message")
    return None


def generate_crop_budget_with_ai_combined(user_message, land_size, location, bedrock_client, conversation_history=""):
    """
    SINGLE AI CALL that:
    1. Extracts crop name from user message
    2. Fetches live market price from AgMarkNet
    3. Generates complete budget with feasibility analysis
    
    This avoids throttling by making only ONE Bedrock call instead of two.
    """
    print(f"[DEBUG] ===== COMBINED AI BUDGET GENERATION =====")
    print(f"[DEBUG] User message: {user_message}")
    print(f"[DEBUG] Land: {land_size} acre(s), Location: {location}")
    
    # Step 1: Extract state name for market data
    state_mapping = {
        'mumbai': 'Maharashtra', 'pune': 'Maharashtra', 'nagpur': 'Maharashtra', 'nashik': 'Maharashtra',
        'kolhapur': 'Maharashtra', 'aurangabad': 'Maharashtra', 'solapur': 'Maharashtra',
        'delhi': 'Delhi', 'bangalore': 'Karnataka', 'bengaluru': 'Karnataka', 'mysore': 'Karnataka',
        'hyderabad': 'Telangana', 'chennai': 'Tamil Nadu', 'coimbatore': 'Tamil Nadu',
        'kolkata': 'West Bengal', 'ahmedabad': 'Gujarat', 'surat': 'Gujarat', 'vadodara': 'Gujarat',
        'jaipur': 'Rajasthan', 'jodhpur': 'Rajasthan', 'udaipur': 'Rajasthan',
        'lucknow': 'Uttar Pradesh', 'kanpur': 'Uttar Pradesh', 'varanasi': 'Uttar Pradesh',
        'patna': 'Bihar', 'bhopal': 'Madhya Pradesh', 'indore': 'Madhya Pradesh',
        'chandigarh': 'Punjab', 'ludhiana': 'Punjab', 'amritsar': 'Punjab',
    }
    
    state_name = state_mapping.get(location.lower(), 'Maharashtra')
    print(f"[DEBUG] State mapped: {state_name}")
    
    # Step 2: Build comprehensive prompt that does EVERYTHING in one call
    prompt = f"""**CRITICAL INSTRUCTION - READ FIRST:**
If the farmer's message contains multiple crops (e.g., "I want to grow X in Y"), extract the LAST crop mentioned (Y), NOT the first one (X).

Examples:
- "I want to grow rice in tomatoes" → Extract: tomato (NOT rice)
- "I want to grow rice in soybean" → Extract: soybean (NOT rice)
- "I want to grow tomato" → Extract: tomato
- "give me sugarcane budget" → Extract: sugarcane

You are an expert agricultural economist with 20+ years of experience in Indian farming.

**TASK**: Analyze this farmer's request and generate a complete budget FOR 1 ACRE ONLY:

Farmer's Message: "{user_message}"
Location: {location}, {state_name}
Land Size: {land_size} acre(s)
Current Month: February 2026

**CRITICAL: Provide ALL costs and yields for 1 ACRE only. The system will scale to {land_size} acres automatically.**

**YOUR TASK (Complete in ONE response):**

1. **Extract the crop name** - If multiple crops mentioned, extract the LAST one
2. **Analyze feasibility** for that crop in {location}, {state_name}
3. **Generate realistic budget FOR 1 ACRE** with accurate costs and yields

**CRITICAL YIELD CONSTRAINTS (PER ACRE):**
- Tur Dal/Arhar: 4-8 quintals/acre (NOT 1,500!)
- Moong/Urad: 3-6 quintals/acre
- Chana/Gram: 8-15 quintals/acre
- Rice/Paddy: 20-35 quintals/acre
- Wheat: 25-45 quintals/acre
- Soybean: 10-20 quintals/acre
- Cotton: 10-20 quintals/acre
- Sugarcane: 30-45 tons/acre (300-450 quintals)
- Tomato: 100-250 quintals/acre
- Potato: 80-200 quintals/acre

**NEVER exceed these realistic ranges. If you provide unrealistic yields, the system will reject your response.**

**CRITICAL ACCURACY REQUIREMENTS:**

- Use REALISTIC yields for {state_name} region (see constraints above)
- Use CORRECT units (quintal for most crops, ton for sugarcane)
- Use CURRENT 2026 market rates for all inputs
- **VERIFY YOUR MATH**: Revenue MUST equal Yield × Price (use a calculator!)
- **VERIFY YOUR MATH**: Profit MUST equal Revenue - Total_Cost (use a calculator!)
- If profit is NEGATIVE, feasibility CANNOT be "HIGHLY_SUITABLE"
- Be CONSISTENT (same inputs = same outputs)
- **ALL VALUES MUST BE FOR 1 ACRE ONLY**

**FEASIBILITY RULES:**
- HIGHLY_SUITABLE: Good climate + Good profit (ROI > 30%)
- SUITABLE: Good climate + Moderate profit (ROI 10-30%)
- MODERATELY_SUITABLE: Fair climate OR Low/negative profit (ROI < 10%)
- NOT_RECOMMENDED: Poor climate AND Negative profit

**CRITICAL DATA RESEARCH INSTRUCTIONS:**
- Research REAL current data for the crop in the specified state
- Use government agricultural databases and MSP/FRP notifications
- Use recent mandi price trends from AgMarkNet
- Use state agricultural department statistics
- DO NOT use example values or estimates
- DO NOT guess - research actual data from reliable sources
- Verify yields are realistic for the specific region
- Ensure prices match current market conditions (February 2026)

**CRITICAL UNIT RULES:**
- Sugarcane: ALWAYS use TON (not quintal)
- All other crops: Use quintal
- If crop is sugarcane, Price_Unit MUST be "ton"
- If crop is sugarcane, Yield MUST be in tons (30-45 range)

**OUTPUT FORMAT (Use EXACT format with numbers only, no commas, FOR 1 ACRE):**

CROP: [crop name extracted from message - LAST crop if multiple mentioned]
FEASIBILITY: [HIGHLY_SUITABLE / SUITABLE / MODERATELY_SUITABLE / NOT_RECOMMENDED]
REASON: [One line explanation]
BEST_SEASON: [Season name]
CLIMATE_MATCH: [EXCELLENT / GOOD / FAIR / POOR]

Seeds: [number only - FOR 1 ACRE]
Fertilizer: [number only - FOR 1 ACRE]
Pesticides: [number only - FOR 1 ACRE]
Irrigation: [number only - FOR 1 ACRE]
Labor: [number only - FOR 1 ACRE]
Machinery: [number only - FOR 1 ACRE]
Total_Cost: [number only - FOR 1 ACRE]
Yield: [number only - FOR 1 ACRE - MUST be within realistic range above]
Price_Unit: [quintal OR ton - MUST be "ton" for sugarcane]
Price_Per_Unit: [number only - use CORRECT unit]
Revenue: [number only - MUST equal Yield × Price_Per_Unit - FOR 1 ACRE]
Profit: [number only - MUST equal Revenue - Total_Cost - FOR 1 ACRE, CAN BE NEGATIVE]

RISKS: [One line about main risks]
RECOMMENDATION: [One line practical advice]
DATA_SOURCES: [Government sources you researched]

**VERIFICATION CHECKLIST:**
- [ ] Crop name extracted correctly (LAST crop if multiple)
- [ ] ALL values are FOR 1 ACRE ONLY
- [ ] If crop is sugarcane, Price_Unit = "ton" and Yield is 60-110 tons/acre
- [ ] If crop is NOT sugarcane, Price_Unit = "quintal"
- [ ] Yield is within realistic range (e.g., Tur Dal: 4-8 quintal/acre, NOT 1,500)
- [ ] Revenue = Yield × Price_Per_Unit (math is correct)
- [ ] Profit = Revenue - Total_Cost (math is correct, can be negative)
- [ ] ROI is reasonable (20-120%, not 300%+)
- [ ] All costs are realistic for 2026 India
- [ ] Total_Cost = Seeds + Fertilizer + Pesticides + Irrigation + Labor + Machinery

**CRITICAL FOR SUGARCANE:**
- Sugarcane yield: 60-110 TONS per acre (NOT quintals)
- Sugarcane price: ₹3,500-4,500 per TON (FRP 2025-26)
- Sugarcane costs: ₹50,000-80,000 per acre
- DO NOT confuse tons with quintals (1 ton = 10 quintals)

Now generate the complete analysis FOR 1 ACRE:"""

    try:
        # Choose model based on API type
        if USE_ANTHROPIC_DIRECT:
            model_id = "claude-sonnet-4-6"
            print(f"[DEBUG] Calling Anthropic Claude API for COMBINED crop extraction + budget generation...")
            print(f"[DEBUG] Model: {model_id} (Claude Sonnet 4.6 - latest - direct API - best accuracy)")
        else:
            model_id = "us.amazon.nova-lite-v1:0"
            print(f"[DEBUG] Calling Bedrock for COMBINED crop extraction + budget generation...")
            print(f"[DEBUG] Model: {model_id} (optimized for speed)")
        
        # Add retry logic for throttling with exponential backoff
        import time
        max_retries = 4
        for attempt in range(max_retries):
            try:
                response = bedrock_client.converse(
                    modelId=model_id,
                    messages=[{"role": "user", "content": [{"text": prompt}]}],
                    inferenceConfig={"maxTokens": 3000, "temperature": 0.1}
                )
                break
            except Exception as e:
                if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 3  # 3, 6, 12, 24 seconds (exponential backoff)
                    print(f"[WARNING] Throttled, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    raise
        
        budget_text = response["output"]["message"]["content"][0]["text"].strip()
        print(f"[INFO] ✅ AI generated complete budget analysis")
        print(f"[DEBUG] Response length: {len(budget_text)} chars")

        # Parse the response
        parsed = parse_ai_budget_enhanced(budget_text, None, land_size)  # crop_name will be extracted from response
        parsed['real_market_price_used'] = False
        parsed['data_source'] = 'ai_research'
        print(f"[DEBUG] Budget parsed successfully")
        print(f"[DEBUG] Extracted crop: {parsed.get('crop', 'unknown')}")
        return parsed
    except Exception as e:
        print(f"[ERROR] Combined budget generation error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None


def extract_state_with_ai(user_message, bedrock_client):
    """Extract state name from user message using keyword matching (optimized for speed)"""
    print(f"[DEBUG] Extracting state/location using keyword matching...")
    
    message_lower = user_message.lower()
    
    # Check CITY_TO_STATE mapping first (fastest)
    for city, state in CITY_TO_STATE.items():
        if city in message_lower:
            print(f"[INFO] ✅ Extracted state from city: {city} → {state}")
            return state
    
    # Check for direct state mentions
    states = ["maharashtra", "punjab", "haryana", "uttar pradesh", "gujarat", "rajasthan",
              "madhya pradesh", "karnataka", "tamil nadu", "andhra pradesh", "telangana",
              "west bengal", "kerala", "bihar", "odisha"]
    
    for state in states:
        if state in message_lower:
            print(f"[INFO] ✅ Extracted state: {state.title()}")
            return state.title()
    
    # Default fallback
    print(f"[INFO] No location found, using default: Maharashtra")
    return "Maharashtra"


def fetch_real_agricultural_data_with_ai(crop_name, state_name, bedrock_client):
    """Use Claude Sonnet 4 to research and provide real agricultural data"""
    print(f"[DEBUG] ===== AI RESEARCH: FETCHING REAL AGRICULTURAL DATA =====")
    print(f"[DEBUG] Crop: {crop_name}, State: {state_name}")

    research_prompt = f"""You are an agricultural data researcher with access to Indian government agricultural databases, MSP notifications, and state agricultural department reports.

Research and provide REAL, VERIFIED data for {crop_name} cultivation in {state_name}, India (February 2026).

**Research Sources to Consider:**
1. Ministry of Agriculture & Farmers Welfare reports
2. MSP (Minimum Support Price) notifications for 2025-26
3. FRP (Fair & Remunerative Price) for sugarcane 2025-26
4. State Agricultural Department statistics
5. ICAR (Indian Council of Agricultural Research) data
6. Agricultural universities in {state_name}
7. Recent mandi price trends

**Provide ACCURATE data for:**

1. **Market Price** (Current, February 2026)
   - Use MSP if crop is covered under MSP
   - Use FRP for sugarcane
   - Use recent average mandi rates for others
   - Specify unit (quintal or ton)

2. **Realistic Yield** (per acre in {state_name})
   - Use state-specific average yields
   - Account for current farming practices
   - Be conservative (don't use best-case)

3. **Input Costs** (per acre, 2026 prices)
   - Seeds: Hybrid/certified seed costs
   - Fertilizer: NPK + micronutrients
   - Pesticides: Based on crop requirements
   - Irrigation: Electricity/diesel costs
   - Labor: Current wage rates in {state_name}
   - Machinery: Rental costs

4. **Cultivation Insights**
   - Best planting season
   - Climate suitability
   - Major growing regions
   - Key risks
   - Best practices

**CRITICAL: Use REAL data, not estimates. Cite sources.**

**FORMAT (numbers only, no commas):**

MARKET_PRICE: [number]
PRICE_UNIT: [quintal or ton]
YIELD_PER_ACRE: [number in quintals]
SEEDS_COST: [number]
FERTILIZER_COST: [number]
PESTICIDES_COST: [number]
IRRIGATION_COST: [number]
LABOR_COST: [number]
MACHINERY_COST: [number]
BEST_SEASON: [season]
CLIMATE_SUITABILITY: [EXCELLENT/GOOD/FAIR/POOR]
MAJOR_REGIONS: [regions]
RISKS: [one line]
RECOMMENDATION: [one line]
DATA_SOURCES: [cite sources]

Research {crop_name} in {state_name} now:"""

    try:
        print(f"[DEBUG] Calling Amazon Nova Pro for agricultural data research...")
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",  # Amazon Nova Pro
            messages=[{"role": "user", "content": [{"text": research_prompt}]}],
            inferenceConfig={"maxTokens": 2000, "temperature": 0.1}
        )
        data_text = response["output"]["message"]["content"][0]["text"].strip()
        print(f"[INFO] ✅ AI research completed")
        print(f"[DEBUG] Research data:\n{data_text[:500]}...")

        # Parse structured data
        import re
        data = {}

        patterns = {
            "market_price": r'MARKET_PRICE:\s*([\d,]+)',
            "price_unit": r'PRICE_UNIT:\s*(\w+)',
            "yield_per_acre": r'YIELD_PER_ACRE:\s*([\d,]+)',
            "seeds_cost": r'SEEDS_COST:\s*([\d,]+)',
            "fertilizer_cost": r'FERTILIZER_COST:\s*([\d,]+)',
            "pesticides_cost": r'PESTICIDES_COST:\s*([\d,]+)',
            "irrigation_cost": r'IRRIGATION_COST:\s*([\d,]+)',
            "labor_cost": r'LABOR_COST:\s*([\d,]+)',
            "machinery_cost": r'MACHINERY_COST:\s*([\d,]+)',
            "best_season": r'BEST_SEASON:\s*(.+?)(?:\n|$)',
            "climate_suitability": r'CLIMATE_SUITABILITY:\s*(\w+)',
            "major_regions": r'MAJOR_REGIONS:\s*(.+?)(?:\n|$)',
            "risks": r'RISKS:\s*(.+?)(?:\n|$)',
            "recommendation": r'RECOMMENDATION:\s*(.+?)(?:\n|$)',
            "data_sources": r'DATA_SOURCES:\s*(.+?)(?:\n\n|$)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, data_text, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                if key in ["market_price", "yield_per_acre", "seeds_cost", "fertilizer_cost",
                          "pesticides_cost", "irrigation_cost", "labor_cost", "machinery_cost"]:
                    data[key] = int(value.replace(",", ""))
                else:
                    data[key] = value
                print(f"[DEBUG] Extracted {key}: {data[key]}")

        if data:
            print(f"[INFO] ✅ Successfully parsed {len(data)} data fields")
            return data
        else:
            print(f"[WARNING] No data extracted from AI research")
            return None

    except Exception as e:
        print(f"[ERROR] AI research error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None



def generate_crop_budget_with_ai(crop_name, land_size, location, bedrock_client, state_name=None):
    """Generate crop budget using AI research + real-time market data"""
    if not state_name:
        state_name = location

    print(f"[DEBUG] ===== GENERATING INTELLIGENT AI-POWERED BUDGET =====")
    print(f"[DEBUG] Crop: {crop_name}, Land: {land_size} acre(s), Location: {location}, State: {state_name}")
    
    # Step 1: Get live market price from AgMarkNet first (faster, no Bedrock call)
    real_market_price = None
    price_source = "ai_research"
    
    print(f"[DEBUG] Step 1: Fetching live market price from AgMarkNet...")
    try:
        from market_data_sources import scrape_agmarknet_website
        scraped_data = scrape_agmarknet_website(crop_name, state_name)
        if scraped_data and scraped_data.get('average_price'):
            real_market_price = scraped_data['average_price']
            price_source = "agmarknet_live"
            print(f"[INFO] 🌐 Live market price: ₹{real_market_price}/quintal")
    except Exception as e:
        print(f"[DEBUG] AgMarkNet scraping failed: {e}")
    
    # Try API fallback
    if not real_market_price and AGMARKNET_API_KEY and AGMARKNET_API_KEY != "not_available":
        try:
            mandi_data = get_mandi_prices(crop_name, state_name)
            if mandi_data and len(mandi_data) > 0:
                real_market_price = int(float(mandi_data[0].get("modal_price", 0)))
                price_source = "agmarknet_api"
                print(f"[INFO] 📡 API market price: ₹{real_market_price}/quintal")
        except Exception as e:
            print(f"[DEBUG] AgMarkNet API failed: {e}")
    
    # Step 2: Single AI call for complete budget (no separate research call to avoid throttling)
    print(f"[DEBUG] Step 2: Generating budget with single AI call...")
    
    market_price_instruction = ""
    if real_market_price:
        market_price_instruction = f"\n**IMPORTANT: Use EXACTLY ₹{real_market_price} as the market price per quintal (from AgMarkNet real-time data).**\n"

    prompt = f"""You are an expert agricultural economist with 20+ years of experience in Indian farming. Generate a REALISTIC and ACCURATE budget for {crop_name} cultivation in {location}, {state_name}.

**Farm Details:**
- Crop: {crop_name}
- Location: {location}, {state_name}
- Land Size: {land_size} acre(s)
- Current Month: February 2026
{market_price_instruction}

**CRITICAL ACCURACY REQUIREMENTS:**

1. **Use REALISTIC yields for {state_name} region**
   - Research typical yields for {crop_name} in {state_name}
   - Account for local climate and soil conditions
   - Use conservative estimates (not best-case scenarios)

2. **Use CORRECT units and pricing**
   - Prices are per QUINTAL (100 kg) for most crops
   - Sugarcane is per TON (1000 kg), not quintal
   - Cotton is per quintal of seed cotton
   - Don't confuse quintal and ton

3. **Use CURRENT 2026 market rates**
   - Seeds: Realistic hybrid/certified seed costs
   - Fertilizer: NPK + micronutrients at current prices
   - Labor: Current daily wage rates in {state_name}
   - Irrigation: Electricity + water costs
   - Machinery: Tractor, harvester rental costs

4. **Calculate ACCURATE revenue**
   - Revenue = Yield × Price_Per_Quintal
   - Double-check your math
   - Use realistic yield (not inflated)
   - Use correct price unit

5. **Be CONSISTENT**
   - Same inputs should give same outputs
   - Don't vary wildly between requests
   - Use deterministic calculations

**CRITICAL DATA RESEARCH INSTRUCTIONS:**
- Research REAL current data for the crop in the specified state
- Use government agricultural databases and MSP/FRP notifications
- Use recent mandi price trends from AgMarkNet
- Use state agricultural department statistics
- DO NOT use example values or estimates
- DO NOT guess - research actual data from reliable sources
- Verify yields are realistic for the specific region
- Ensure prices match current market conditions (February 2026)


**Task 1: Feasibility Analysis**
Analyze if {crop_name} is suitable for {location}, {state_name} considering:
- Climate compatibility (temperature, rainfall, season)
- Soil requirements vs regional soil types
- Water availability needs
- Market demand in the region
- Risk factors specific to {state_name}

**Task 2: Budget Generation**
Generate a REALISTIC budget with ACCURATE numbers.

**CRITICAL: Use this EXACT format with numbers only (no commas, no extra text):**

FEASIBILITY: [HIGHLY_SUITABLE / SUITABLE / MODERATELY_SUITABLE / NOT_RECOMMENDED]
REASON: [One line explanation]
BEST_SEASON: [Season name]
CLIMATE_MATCH: [EXCELLENT / GOOD / FAIR / POOR]

Seeds: [number only]
Fertilizer: [number only]
Pesticides: [number only]
Irrigation: [number only]
Labor: [number only]
Machinery: [number only]
Total_Cost: [number only]
Yield: [number only - use REALISTIC yield for {state_name}]
Price_Per_Quintal: [number only - use CORRECT unit]
Revenue: [number only - MUST equal Yield × Price_Per_Quintal]
Profit: [number only - MUST equal Revenue - Total_Cost]

RISKS: [One line about main risks]
RECOMMENDATION: [One line practical advice]

**VERIFICATION CHECKLIST:**
- [ ] Yield is realistic for {state_name} region
- [ ] Price unit is correct (quintal vs ton)
- [ ] Revenue = Yield × Price_Per_Quintal (math is correct)
- [ ] Profit = Revenue - Total_Cost (math is correct)
- [ ] ROI is reasonable (20-100%, not 300%+)
- [ ] All costs are realistic for 2026 India

Now generate ACCURATE budget for {crop_name} in {location}, {state_name} for {land_size} acre(s):"""

    try:
        print(f"[DEBUG] Calling Bedrock for budget generation...")
        print(f"[DEBUG] Model: us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        print(f"[DEBUG] Using real market price from AgMarkNet: {real_market_price is not None}")
        
        # Add retry logic for throttling
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = bedrock_client.converse(
                    modelId="us.amazon.nova-pro-v1:0",  # Amazon Nova Pro
                    messages=[{"role": "user", "content": [{"text": prompt}]}],
                    inferenceConfig={"maxTokens": 3000, "temperature": 0.1}
                )
                break
            except Exception as e:
                if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                    print(f"[WARNING] Throttled, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    raise
        
        budget_text = response["output"]["message"]["content"][0]["text"].strip()
        print(f"[INFO] ✅ AI generated detailed budget for {crop_name} in {location}")
        print(f"[DEBUG] Budget text length: {len(budget_text)} chars")

        parsed = parse_ai_budget_enhanced(budget_text, crop_name, land_size)
        parsed['real_market_price_used'] = real_market_price is not None
        parsed['data_source'] = price_source
        print(f"[DEBUG] Budget parsed successfully")
        print(f"[DEBUG] Market price source: {price_source}")
        return parsed
    except Exception as e:
        print(f"[ERROR] Budget generation error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None
    
    # Get market price for AI prompt
    market_price_instruction = ""
    if real_market_price:
        market_price_instruction = f"\n**IMPORTANT: Use EXACTLY ₹{real_market_price} as the market price per quintal (from AgMarkNet real-time data).**\n"

    prompt = f"""You are an expert agricultural economist with 20+ years of experience in Indian farming. Generate a REALISTIC and ACCURATE budget for {crop_name} cultivation in {location}, {state_name}.

**Farm Details:**
- Crop: {crop_name}
- Location: {location}, {state_name}
- Land Size: {land_size} acre(s)
- Current Month: February 2026
{market_price_instruction}

**CRITICAL ACCURACY REQUIREMENTS:**

1. **Use REALISTIC yields for {state_name} region**
   - Research typical yields for {crop_name} in {state_name}
   - Account for local climate and soil conditions
   - Use conservative estimates (not best-case scenarios)

2. **Use CORRECT units and pricing**
   - Prices are per QUINTAL (100 kg) for most crops
   - Sugarcane is per TON (1000 kg), not quintal
   - Cotton is per quintal of seed cotton
   - Don't confuse quintal and ton

3. **Use CURRENT 2026 market rates**
   - Seeds: Realistic hybrid/certified seed costs
   - Fertilizer: NPK + micronutrients at current prices
   - Labor: Current daily wage rates in {state_name}
   - Irrigation: Electricity + water costs
   - Machinery: Tractor, harvester rental costs

4. **Calculate ACCURATE revenue**
   - Revenue = Yield × Price_Per_Quintal
   - Double-check your math
   - Use realistic yield (not inflated)
   - Use correct price unit

5. **Be CONSISTENT**
   - Same inputs should give same outputs
   - Don't vary wildly between requests
   - Use deterministic calculations

**CRITICAL DATA RESEARCH INSTRUCTIONS:**
- Research REAL current data for the crop in the specified state
- Use government agricultural databases and MSP/FRP notifications
- Use recent mandi price trends from AgMarkNet
- Use state agricultural department statistics
- DO NOT use example values or estimates
- DO NOT guess - research actual data from reliable sources
- Verify yields are realistic for the specific region
- Ensure prices match current market conditions (February 2026)


**Task 1: Feasibility Analysis**
Analyze if {crop_name} is suitable for {location}, {state_name} considering:
- Climate compatibility (temperature, rainfall, season)
- Soil requirements vs regional soil types
- Water availability needs
- Market demand in the region
- Risk factors specific to {state_name}

**Task 2: Budget Generation**
Generate a REALISTIC budget with ACCURATE numbers.

**CRITICAL: Use this EXACT format with numbers only (no commas, no extra text):**

FEASIBILITY: [HIGHLY_SUITABLE / SUITABLE / MODERATELY_SUITABLE / NOT_RECOMMENDED]
REASON: [One line explanation]
BEST_SEASON: [Season name]
CLIMATE_MATCH: [EXCELLENT / GOOD / FAIR / POOR]

Seeds: [number only]
Fertilizer: [number only]
Pesticides: [number only]
Irrigation: [number only]
Labor: [number only]
Machinery: [number only]
Total_Cost: [number only]
Yield: [number only - use REALISTIC yield for {state_name}]
Price_Per_Quintal: [number only - use CORRECT unit]
Revenue: [number only - MUST equal Yield × Price_Per_Quintal]
Profit: [number only - MUST equal Revenue - Total_Cost]

RISKS: [One line about main risks]
RECOMMENDATION: [One line practical advice]

**VERIFICATION CHECKLIST:**
- [ ] Yield is realistic for {state_name} region
- [ ] Price unit is correct (quintal vs ton)
- [ ] Revenue = Yield × Price_Per_Quintal (math is correct)
- [ ] Profit = Revenue - Total_Cost (math is correct)
- [ ] ROI is reasonable (20-100%, not 300%+)
- [ ] All costs are realistic for 2026 India

Now generate ACCURATE budget for {crop_name} in {location}, {state_name} for {land_size} acre(s):"""

    try:
        print(f"[DEBUG] Calling Bedrock for budget generation...")
        print(f"[DEBUG] Model: us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        print(f"[DEBUG] Using real market price from AgMarkNet: {real_market_price is not None}")
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",  # Amazon Nova Pro for superior accuracy
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 3000, "temperature": 0.1}  # Very low temp for consistency
        )
        budget_text = response["output"]["message"]["content"][0]["text"].strip()
        print(f"[INFO] ✅ AI generated detailed budget for {crop_name} in {location}")
        print(f"[DEBUG] Budget text length: {len(budget_text)} chars")
        print(f"[DEBUG] Budget text:\n{budget_text}")

        parsed = parse_ai_budget_enhanced(budget_text, crop_name, land_size)
        parsed['real_market_price_used'] = real_market_price is not None
        parsed['data_source'] = price_source
        print(f"[DEBUG] Budget parsed successfully")
        print(f"[DEBUG] Market price source: {price_source}")
        return parsed
    except Exception as e:
        print(f"[ERROR] Budget generation error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None


def parse_ai_budget_enhanced(budget_text, crop_name, land_size):
    """Parse AI-generated budget text with feasibility analysis"""
    import re

    print(f"[DEBUG] Parsing enhanced AI budget text...")

    budget = {
        "crop": crop_name,
        "land_size": land_size,
        "feasibility": "UNKNOWN",
        "reason": "",
        "best_season": "",
        "climate_match": "",
        "seeds": 0,
        "fertilizer": 0,
        "pesticides": 0,
        "irrigation": 0,
        "labor": 0,
        "machinery": 0,
        "total_cost": 0,
        "expected_yield": 0,
        "expected_price": 0,
        "expected_revenue": 0,
        "expected_profit": 0,
        "risks": "",
        "recommendation": ""
    }

    # Extract crop name if not provided (for combined function)
    if not crop_name:
        crop_match = re.search(r'CROP:\s*(.+?)(?:\n|$)', budget_text, re.IGNORECASE)
        if crop_match:
            budget["crop"] = crop_match.group(1).strip().lower()
            print(f"[DEBUG] Extracted crop from AI response: {budget['crop']}")

    # Extract feasibility info
    feasibility_match = re.search(r'FEASIBILITY:\s*([A-Z_]+)', budget_text, re.IGNORECASE)
    if feasibility_match:
        budget["feasibility"] = feasibility_match.group(1)
        print(f"[DEBUG] Extracted feasibility: {budget['feasibility']}")

    reason_match = re.search(r'REASON:\s*(.+?)(?:\n|$)', budget_text, re.IGNORECASE)
    if reason_match:
        budget["reason"] = reason_match.group(1).strip()
        print(f"[DEBUG] Extracted reason: {budget['reason']}")

    season_match = re.search(r'BEST_SEASON:\s*(.+?)(?:\n|$)', budget_text, re.IGNORECASE)
    if season_match:
        budget["best_season"] = season_match.group(1).strip()
        print(f"[DEBUG] Extracted season: {budget['best_season']}")

    climate_match = re.search(r'CLIMATE_MATCH:\s*([A-Z]+)', budget_text, re.IGNORECASE)
    if climate_match:
        budget["climate_match"] = climate_match.group(1)
        print(f"[DEBUG] Extracted climate match: {budget['climate_match']}")

    risks_match = re.search(r'RISKS:\s*(.+?)(?:\n|$)', budget_text, re.IGNORECASE)
    if risks_match:
        budget["risks"] = risks_match.group(1).strip()
        print(f"[DEBUG] Extracted risks: {budget['risks']}")

    recommendation_match = re.search(r'RECOMMENDATION:\s*(.+?)(?:\n|$)', budget_text, re.IGNORECASE)
    if recommendation_match:
        budget["recommendation"] = recommendation_match.group(1).strip()
        print(f"[DEBUG] Extracted recommendation: {budget['recommendation']}")
    
    # Extract data sources
    data_sources_match = re.search(r'DATA_SOURCES:\s*(.+?)(?:\n|$)', budget_text, re.IGNORECASE)
    if data_sources_match:
        budget["data_sources"] = data_sources_match.group(1).strip()
        print(f"[DEBUG] Extracted data sources: {budget['data_sources']}")

    # Extract financial numbers - more flexible patterns
    patterns = {
        "seeds": r'Seeds?[:\s]+₹?\s*([\d,]+)',
        "fertilizer": r'Fertilizer[:\s]+₹?\s*([\d,]+)',
        "pesticides": r'Pesticides?[:\s]+₹?\s*([\d,]+)',
        "irrigation": r'Irrigation[:\s]+₹?\s*([\d,]+)',
        "labor": r'Labor[:\s]+₹?\s*([\d,]+)',
        "machinery": r'Machinery[:\s]+₹?\s*([\d,]+)',
        "total_cost": r'Total[_\s]Cost[:\s]+₹?\s*([\d,]+)',
        "expected_yield": r'Yield[:\s]+([\d,]+)',
        "expected_price": r'Price[_\s]Per[_\s]Unit[:\s]+₹?\s*([\d,]+)',  # Changed to Price_Per_Unit
        "expected_revenue": r'Revenue[:\s]+₹?\s*([\d,]+)',
        "expected_profit": r'Profit[:\s]+₹?\s*([\d,]+)'
    }
    
    # Extract price unit (quintal or ton)
    price_unit_match = re.search(r'Price[_\s]Unit[:\s]+(quintal|ton)', budget_text, re.IGNORECASE)
    if price_unit_match:
        budget["price_unit"] = price_unit_match.group(1).lower()
        print(f"[DEBUG] Extracted price unit: {budget['price_unit']}")
    else:
        # Default to quintal if not specified
        budget["price_unit"] = "quintal"
        print(f"[DEBUG] Price unit not found, defaulting to quintal")

    for key, pattern in patterns.items():
        match = re.search(pattern, budget_text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(",", "")
            budget[key] = int(value)
            print(f"[DEBUG] Extracted {key}: {budget[key]}")
        else:
            print(f"[DEBUG] ⚠️  Could not extract {key} from budget text")

    print(f"[DEBUG] Budget parsing complete - Total Cost: ₹{budget['total_cost']}, Profit: ₹{budget['expected_profit']}")
    print(f"[DEBUG] Feasibility: {budget['feasibility']}, Climate: {budget['climate_match']}")
    
    # STEP 1: VALIDATION - Check yield and cost are realistic BEFORE scaling
    print(f"[VALIDATION] ===== STEP 1: PRE-SCALING VALIDATION =====")
    print(f"[VALIDATION] Checking yield realism for {budget.get('crop', 'unknown')} - {budget['expected_yield']} {budget.get('price_unit', 'quintal')}/acre")
    
    try:
        from crop_yield_database import (
            validate_yield, validate_roi, validate_cost, get_yield_range,
            calculate_additional_costs, enforce_mathematical_accuracy, sanity_check_budget
        )
        
        # Validate cost per acre (before scaling)
        is_valid_cost, corrected_cost, cost_message = validate_cost(budget.get('crop', ''), budget['total_cost'])
        print(f"[VALIDATION] Cost validation: {cost_message}")
        
        if not is_valid_cost:
            print(f"[CRITICAL] ⚠️  UNREALISTIC COST DETECTED! Correcting from ₹{budget['total_cost']} to ₹{corrected_cost}")
            # Proportionally adjust all cost components
            cost_ratio = corrected_cost / budget['total_cost'] if budget['total_cost'] > 0 else 1
            budget['seeds'] = int(budget['seeds'] * cost_ratio)
            budget['fertilizer'] = int(budget['fertilizer'] * cost_ratio)
            budget['pesticides'] = int(budget['pesticides'] * cost_ratio)
            budget['irrigation'] = int(budget['irrigation'] * cost_ratio)
            budget['labor'] = int(budget['labor'] * cost_ratio)
            budget['machinery'] = int(budget['machinery'] * cost_ratio)
            budget['total_cost'] = corrected_cost
            print(f"[VALIDATION] Corrected Total Cost: ₹{budget['total_cost']:,}")
        
        # Validate yield per acre (before scaling)
        is_valid, corrected_yield, message = validate_yield(budget.get('crop', ''), budget['expected_yield'])
        print(f"[VALIDATION] Yield validation: {message}")
        
        if not is_valid:
            print(f"[CRITICAL] ⚠️  UNREALISTIC YIELD DETECTED! Correcting from {budget['expected_yield']} to {corrected_yield}")
            budget['expected_yield'] = corrected_yield
            print(f"[VALIDATION] Corrected Yield: {corrected_yield}")
        
        # Validate ROI (before scaling)
        # First calculate revenue with corrected values
        budget['expected_revenue'] = budget['expected_yield'] * budget['expected_price']
        budget['expected_profit'] = budget['expected_revenue'] - budget['total_cost']
        
        if budget['total_cost'] > 0:
            roi = (budget['expected_profit'] / budget['total_cost']) * 100
            is_valid_roi, roi_message = validate_roi(budget.get('crop', ''), roi)
            print(f"[VALIDATION] ROI validation: {roi_message}")
            
            if not is_valid_roi:
                print(f"[CRITICAL] ⚠️  UNREALISTIC ROI DETECTED! {roi:.0f}%")
                # Get realistic yield range and use average
                yield_range = get_yield_range(budget.get('crop', ''))
                if yield_range:
                    avg_yield = (yield_range['min'] + yield_range['max']) // 2
                    print(f"[VALIDATION] Using average realistic yield: {avg_yield} {yield_range['unit']}/acre")
                    budget['expected_yield'] = avg_yield
                    budget['expected_revenue'] = avg_yield * budget['expected_price']
                    budget['expected_profit'] = budget['expected_revenue'] - budget['total_cost']
                    print(f"[VALIDATION] Corrected Revenue: ₹{budget['expected_revenue']:,}")
                    print(f"[VALIDATION] Corrected Profit: ₹{budget['expected_profit']:,}")
    except Exception as e:
        print(f"[WARNING] Validation error: {e}")
        import traceback
        print(f"[WARNING] Traceback: {traceback.format_exc()}")
    
    # STEP 2: ADD MISSING COST COMPONENTS (harvesting, transport, etc.)
    print(f"[VALIDATION] ===== STEP 2: ADDING MISSING COSTS =====")
    try:
        additional_costs = calculate_additional_costs(
            budget.get('crop', ''),
            budget['expected_yield'],
            budget['total_cost']
        )
        
        print(f"[VALIDATION] Additional costs calculated:")
        for key, value in additional_costs.items():
            if key != "total_additional" and value > 0:
                print(f"[VALIDATION]   {key}: ₹{value:,}")
                budget[key] = value
        
        # Add additional costs to total
        budget['total_cost'] += additional_costs['total_additional']
        print(f"[VALIDATION] Total cost after additional components: ₹{budget['total_cost']:,}")
        
        # Recalculate profit with new total cost
        budget['expected_profit'] = budget['expected_revenue'] - budget['total_cost']
        print(f"[VALIDATION] Profit after additional costs: ₹{budget['expected_profit']:,}")
        
    except Exception as e:
        print(f"[WARNING] Additional costs calculation error: {e}")
    
    # STEP 3: SCALE TO LAND SIZE
    print(f"[VALIDATION] ===== STEP 3: SCALING TO LAND SIZE =====")
    if land_size and land_size > 1:
        print(f"[SCALING] Multiplying costs and yields by land size: {land_size} acres")
        
        # Store per-acre values for reference
        budget['cost_per_acre'] = budget['total_cost']
        budget['yield_per_acre'] = budget['expected_yield']
        budget['profit_per_acre'] = budget['expected_profit']
        
        # Scale all costs
        budget['seeds'] *= land_size
        budget['fertilizer'] *= land_size
        budget['pesticides'] *= land_size
        budget['irrigation'] *= land_size
        budget['labor'] *= land_size
        budget['machinery'] *= land_size
        budget['harvesting'] = budget.get('harvesting', 0) * land_size
        budget['transport'] = budget.get('transport', 0) * land_size
        budget['electricity_diesel'] = budget.get('electricity_diesel', 0) * land_size
        budget['miscellaneous'] = budget.get('miscellaneous', 0) * land_size
        budget['interest'] = budget.get('interest', 0) * land_size
        budget['total_cost'] *= land_size
        
        # Scale yield (price per unit stays the same)
        budget['expected_yield'] *= land_size
        
        print(f"[SCALING] Scaled Total Cost: ₹{budget['total_cost']:,}")
        print(f"[SCALING] Scaled Yield: {budget['expected_yield']} {budget.get('price_unit', 'quintal')}")
    else:
        # Even for 1 acre, store per-acre values
        budget['cost_per_acre'] = budget['total_cost']
        budget['yield_per_acre'] = budget['expected_yield']
        budget['profit_per_acre'] = budget['expected_profit']
    
    # STEP 4: ENFORCE MATHEMATICAL ACCURACY
    print(f"[VALIDATION] ===== STEP 4: MATHEMATICAL ENFORCEMENT =====")
    try:
        budget = enforce_mathematical_accuracy(budget)
    except Exception as e:
        print(f"[ERROR] Mathematical enforcement error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
    
    # STEP 5: FINAL SANITY CHECK
    print(f"[VALIDATION] ===== STEP 5: FINAL SANITY CHECK =====")
    try:
        is_sane, issues = sanity_check_budget(budget)
        
        if not is_sane:
            print(f"[CRITICAL] ⚠️  SANITY CHECK FAILED!")
            print(f"[CRITICAL] Issues: {', '.join(issues)}")
            print(f"[CRITICAL] Using conservative estimates...")
            
            # Use conservative estimates
            yield_range = get_yield_range(budget.get('crop', ''))
            if yield_range:
                # Use minimum yield for conservative estimate
                conservative_yield_per_acre = yield_range['min']
                budget['expected_yield'] = conservative_yield_per_acre * land_size
                budget['yield_per_acre'] = conservative_yield_per_acre
                
                # Recalculate everything
                budget = enforce_mathematical_accuracy(budget)
                print(f"[CRITICAL] Applied conservative yield: {conservative_yield_per_acre} {yield_range['unit']}/acre")
    except Exception as e:
        print(f"[WARNING] Sanity check error: {e}")
    
    # Adjust feasibility based on profit
    if budget['expected_profit'] < 0:
        print(f"[WARNING] ⚠️  Negative profit detected! Adjusting feasibility from {budget['feasibility']}")
        if budget['feasibility'] == 'HIGHLY_SUITABLE':
            budget['feasibility'] = 'MODERATELY_SUITABLE'
            budget['reason'] = f"High costs make this crop financially challenging in current conditions. {budget.get('reason', '')}"
            print(f"[DEBUG] Adjusted feasibility to MODERATELY_SUITABLE due to negative profit")
        elif budget['feasibility'] == 'SUITABLE':
            budget['feasibility'] = 'MODERATELY_SUITABLE'
            print(f"[DEBUG] Adjusted feasibility to MODERATELY_SUITABLE due to negative profit")
    
    print(f"[FINAL] ===== BUDGET VALIDATION COMPLETE =====")
    print(f"[FINAL] Crop: {budget.get('crop', 'unknown')}")
    print(f"[FINAL] Land Size: {land_size} acres")
    print(f"[FINAL] Cost per acre: ₹{budget.get('cost_per_acre', 0):,}")
    print(f"[FINAL] Yield per acre: {budget.get('yield_per_acre', 0)} {budget.get('price_unit', 'quintal')}")
    print(f"[FINAL] Total Cost: ₹{budget['total_cost']:,}")
    print(f"[FINAL] Total Revenue: ₹{budget['expected_revenue']:,}")
    print(f"[FINAL] Total Profit: ₹{budget['expected_profit']:,}")
    print(f"[FINAL] ROI: {budget.get('roi', 0):.1f}%")
    print(f"[FINAL] ==========================================")
    
    return budget

def match_government_schemes(crop, land_size):
    """Match farmer with eligible schemes"""
    schemes = []
    
    schemes.append({
        "name": "PM-KISAN",
        "benefit": "₹6,000/वर्ष",
        "eligibility": "सभी भूमिधारक किसान"
    })
    
    schemes.append({
        "name": "फसल बीमा योजना (PMFBY)",
        "benefit": f"{crop} के लिए 2% प्रीमियम पर बीमा",
        "eligibility": "सभी किसान"
    })
    
    schemes.append({
        "name": "किसान क्रेडिट कार्ड (KCC)",
        "benefit": "₹3 लाख तक 7% ब्याज पर ऋण",
        "eligibility": "भूमि स्वामित्व वाले किसान"
    })
    
    if land_size <= 2:
        schemes.append({
            "name": "लघु सीमांत किसान योजना",
            "benefit": "कृषि उपकरण पर 50% सब्सिडी",
            "eligibility": "2 एकड़ तक की भूमि"
        })
    
    return schemes

def calculate_loan_eligibility(total_cost, farmer_income):
    """Calculate loan eligibility"""
    max_loan = int(total_cost * 0.8)
    interest_rate = 7.0
    months = 6
    monthly_rate = interest_rate / 12 / 100
    emi = int(max_loan * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1))
    
    return {
        "max_loan": max_loan,
        "interest_rate": interest_rate,
        "monthly_emi": emi,
        "total_repayment": emi * months,
        "total_interest": (emi * months) - max_loan
    }

def handle_finance_query(user_message, user_id="unknown", language='hindi'):
    """Handle finance-related queries with enhanced AI and memory"""
    print(f"[DEBUG] ===== FINANCE AGENT =====")
    print(f"[DEBUG] Processing finance query: {user_message}, Language: {language}")
    print(f"[DEBUG] User ID: {user_id}")

    if language == 'english':
        system_prompt = """You are an expert agricultural finance advisor for Indian farmers.
Provide accurate, practical financial advice for farming operations.
Reply in simple, clear English. Be specific and actionable.
IMPORTANT: Always use ₹ (Rupee symbol) for Indian currency, never use $.
CRITICAL: Respond ONLY in English. Do not use any Hindi words or phrases."""
    else:
        system_prompt = """आप भारतीय किसानों के लिए एक विशेषज्ञ कृषि वित्त सलाहकार हैं।
कृषि कार्यों के लिए सटीक, व्यावहारिक वित्तीय सलाह प्रदान करें।
सरल, स्पष्ट हिंदी में जवाब दें। विशिष्ट और कार्रवाई योग्य रहें।
महत्वपूर्ण: भारतीय मुद्रा के लिए हमेशा ₹ (रुपये का प्रतीक) का उपयोग करें।
अत्यंत महत्वपूर्ण: केवल हिंदी में जवाब दें। कोई अंग्रेजी शब्द या वाक्यांश का उपयोग न करें।"""

    # Get enhanced conversation history
    print(f"[DEBUG] Fetching conversation history...")
    history = get_conversation_history(user_id, limit=10)
    context = build_context_from_history(history)

    message_lower = user_message.lower()

    # Check for budget request
    budget_keywords = ["budget", "cost", "expense", "finance", "model", "planting", "structure", "grow", "cultivation"]
    has_budget_keyword = any(word in message_lower for word in budget_keywords)
    print(f"[DEBUG] Budget request detected: {has_budget_keyword}")

    if has_budget_keyword:
        print(f"[DEBUG] Processing budget request...")

        # Extract land size using regex
        land_size = 1
        import re
        size_match = re.search(r'(\d+)\s*(acre|एकड़|hectare)', message_lower)
        if size_match:
            land_size = int(size_match.group(1))
            print(f"[DEBUG] Land size extracted: {land_size} acre(s)")
        else:
            print(f"[DEBUG] No land size specified, using default: 1 acre")

        # Extract location using regex (prioritize last match to avoid month names)
        location = "Maharashtra"  # Default
        location_patterns = [
            r'farm\s+in\s+(\w+)',  # Most specific first
            r'location\s+is\s+(\w+)',
            r'at\s+(\w+)',
            r'from\s+(\w+)',
            r'in\s+(\w+)',  # Most generic last
        ]
        
        months = ["january", "february", "march", "april", "may", "june", 
                  "july", "august", "september", "october", "november", "december",
                  "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        
        # Find ALL matches and use the LAST valid one (to skip "in March" and get "in Kolhapur")
        all_matches = []
        for pattern in location_patterns:
            matches = re.finditer(pattern, message_lower, re.IGNORECASE)
            for match in matches:
                extracted = match.group(1).lower()
                if extracted not in months:
                    all_matches.append(extracted)
        
        if all_matches:
            # Use the LAST match (most likely the actual location)
            location = all_matches[-1].title()
            print(f"[DEBUG] ✅ Extracted city/location: {location} (from {len(all_matches)} candidates)")
        else:
            print(f"[DEBUG] No city extracted, using default: Maharashtra")
        
        print(f"[INFO] 📍 Location: {location}, Land: {land_size} acre(s)")
        print(f"[INFO] 📊 Generating budget with AI (single call)...")

        # Generate budget using enhanced AI - SINGLE CALL that extracts crop AND generates budget
        budget = generate_crop_budget_with_ai_combined(user_message, land_size, location, bedrock, context)

        if not budget:
            print(f"[ERROR] ❌ Budget generation failed")
            return "I'm having trouble generating a budget. Please try again or ask about a different crop."
        
        if not budget.get('crop'):
            print(f"[ERROR] ❌ No crop detected in message")
            return "Please specify which crop you want to grow. For example: 'I want to grow tomato' or 'give me rice budget'"

        crop_name = budget['crop']
        print(f"[INFO] ✅ Successfully generated budget for {crop_name}")

        print(f"[DEBUG] Formatting budget response with feasibility analysis...")
        
        # Feasibility indicator
        feasibility_emoji = {
            "HIGHLY_SUITABLE": "🟢",
            "SUITABLE": "🟢",
            "MODERATELY_SUITABLE": "🟡",
            "NOT_RECOMMENDED": "🔴"
        }
        emoji = feasibility_emoji.get(budget.get('feasibility', 'UNKNOWN'), "⚪")
        
        # Format enhanced response with feasibility
        message = f"{emoji} *{budget['crop'].title()} Cultivation Analysis*\n"
        message += f"📍 *Location*: {location}\n"
        message += f"🌾 *Land*: {budget['land_size']} acre\n\n"
        
        # Feasibility section
        if budget.get('feasibility') and budget['feasibility'] != 'UNKNOWN':
            message += f"*🎯 Feasibility*: {budget['feasibility'].replace('_', ' ').title()}\n"
            if budget.get('reason'):
                message += f"💬 {budget['reason']}\n"
            if budget.get('climate_match'):
                climate_emoji = "🌡️" if budget['climate_match'] in ['EXCELLENT', 'GOOD'] else "⚠️"
                message += f"{climate_emoji} Climate Match: {budget['climate_match'].title()}\n"
            if budget.get('best_season'):
                message += f"📅 Best Season: {budget['best_season']}\n"
            message += "\n"
        
        message += "*📊 Cost Breakdown*\n"
        message += f"• Seeds: ₹{budget['seeds']:,}\n"
        message += f"• Fertilizer: ₹{budget['fertilizer']:,}\n"
        message += f"• Pesticides: ₹{budget['pesticides']:,}\n"
        message += f"• Irrigation: ₹{budget['irrigation']:,}\n"
        message += f"• Labor: ₹{budget['labor']:,}\n"
        message += f"• Machinery: ₹{budget['machinery']:,}\n"
        message += f"*💵 Total Cost*: ₹{budget['total_cost']:,}\n\n"
        message += "*📈 Expected Returns*\n"
        message += f"• Yield: {budget['expected_yield']} {budget.get('price_unit', 'quintal')}\n"
        
        # Show market price with data source
        price_source_label = {
            "agmarknet_live": "🌐 Live",
            "agmarknet_api": "📡 API",
            "ai_research": "🔍 Research",
            "ai_estimate": "🤖 Estimate"
        }
        source = budget.get('data_source', 'ai_research')
        price_emoji = price_source_label.get(source, "🔍")
        
        message += f"• Market Price: ₹{budget['expected_price']}/{budget.get('price_unit', 'quintal')} {price_emoji}\n"
        
        message += f"• Revenue: ₹{budget['expected_revenue']:,}\n"
        message += f"*✨ Net Profit*: ₹{budget['expected_profit']:,}\n"
        
        if budget['total_cost'] > 0:
            roi = int((budget['expected_profit']/budget['total_cost'])*100)
            message += f"💡 *ROI*: {roi}%\n\n"
        
        # Add risks and recommendations
        if budget.get('risks'):
            message += f"⚠️  *Risks*: {budget['risks']}\n"
        if budget.get('recommendation'):
            message += f"💡 *Tip*: {budget['recommendation']}\n\n"
        else:
            message += "\n"
        
        # Add navigation text
        if INTERACTIVE_MESSAGES_AVAILABLE:
            message = add_navigation_text(message, language)
        
        print(f"[DEBUG] Budget response formatted successfully")
        return message

    # Check for schemes
    elif any(word in message_lower for word in ["scheme", "subsidy", "government"]):
        print(f"[DEBUG] Processing government schemes query")
        schemes = match_government_schemes("wheat", 1)

        message = "? *Government Schemes for Farmers*\n\n"
        for i, scheme in enumerate(schemes[:4], 1):
            message += f"{i}. *{scheme['name']}*\n"
            message += f"   💰 Benefit: {scheme['benefit']}\n"
            message += f"   ✅ Eligibility: {scheme['eligibility']}\n\n"
        message += "💡 Visit nearest Krishi Vigyan Kendra for more details"
        
        # Add navigation text
        if INTERACTIVE_MESSAGES_AVAILABLE:
            message = add_navigation_text(message, language)
        
        print(f"[DEBUG] Schemes response generated")
        return message

    # Check for loan
    elif any(word in message_lower for word in ["loan", "credit", "borrow"]):
        print(f"[DEBUG] Processing loan eligibility query")
        loan = calculate_loan_eligibility(20000, 50000)

        message = "🏦 *Kisan Credit Card (KCC) Eligibility*\n\n"
        message += f"💰 Max Loan: ₹{loan['max_loan']:,}\n"
        message += f"📊 Interest Rate: {loan['interest_rate']}% per annum\n"
        message += f"💳 Monthly EMI: ₹{loan['monthly_emi']:,}\n"
        message += f"💵 Total Repayment: ₹{loan['total_repayment']:,}\n"
        message += f"📈 Total Interest: ₹{loan['total_interest']:,}\n\n"
        message += "💡 Apply at your nearest bank branch with land documents"
        
        # Add navigation text
        if INTERACTIVE_MESSAGES_AVAILABLE:
            message = add_navigation_text(message, language)
        
        print(f"[DEBUG] Loan response generated")
        return message

    # Fallback to AI with enhanced context
    print(f"[DEBUG] Falling back to AI for general finance query")
    result = ask_bedrock(user_message, system_prompt, context)
    
    # Add navigation text
    if INTERACTIVE_MESSAGES_AVAILABLE:
        result = add_navigation_text(result, language)
    
    return result

def handle_general_query(user_message, language='hindi'):
    """Handle general queries - friendly conversation with language support (optimized)"""
    print(f"[DEBUG] ===== GENERAL AGENT =====")
    print(f"[DEBUG] Processing general query: {user_message}, Language: {language}")
    
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
    
    # OPTIMIZATION: Skip context for speed
    result = ask_bedrock(user_message, system_prompt, skip_context=True)
    
    # Add navigation text
    if INTERACTIVE_MESSAGES_AVAILABLE:
        result = add_navigation_text(result, language)
    
    print(f"[DEBUG] General agent response generated, length: {len(result)} chars")
    return result

# ─── WhatsApp ─────────────────────────────────────────────────────────────────

def send_whatsapp_message(to, message, interactive_payload=None):
    """
    Send WhatsApp message (text or interactive)
    
    Args:
        to: Recipient phone number
        message: Text message (used if interactive_payload is None)
        interactive_payload: Optional interactive message payload (buttons/lists)
    """
    print(f"[DEBUG] Sending WhatsApp message to: {to}")
    
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Use interactive message if available
    if interactive_payload and INTERACTIVE_MESSAGES_AVAILABLE:
        print(f"[DEBUG] Sending interactive message: {interactive_payload.get('interactive', {}).get('type')}")
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            **interactive_payload
        }
    else:
        print(f"[DEBUG] Sending text message, length: {len(message)} chars")
        print(f"[DEBUG] Message preview: {message[:100]}...")
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": message}
        }
    
    response = http.request("POST", url, body=json.dumps(data), headers=headers)
    print(f"[INFO] ✅ WhatsApp API response: {response.status}")
    if response.status != 200:
        print(f"[ERROR] WhatsApp API error response: {response.data}")


# ─── Onboarding ───────────────────────────────────────────────────────────────

def check_user_status(user_id):
    """
    Check user onboarding status
    Returns: (is_new, onboarding_state, profile)
    """
    if not ONBOARDING_AVAILABLE:
        print(f"⚠️ ONBOARDING NOT AVAILABLE - treating all users as existing")
        return False, "completed", None
    
    try:
        # Check if user has completed profile
        is_new = onboarding_manager.is_new_user(user_id)
        
        # Get onboarding state
        state, data = onboarding_manager.get_onboarding_state(user_id)
        
        # Get profile if exists
        profile = None if is_new else onboarding_manager.get_user_profile(user_id)
        
        # ✅ FIX: If state is not "completed", treat as needing onboarding
        # regardless of is_new flag
        if state != "completed":
            is_new = True
        
        print(f"🔍 User check: is_new={is_new}, state={state}, has_profile={profile is not None}")
        return is_new, state, profile
        
    except Exception as e:
        print(f"❌ Error checking user status: {e}")
        import traceback
        traceback.print_exc()
        return True, "new", None  # Default to new user on error

# ─── Lambda Handler ───────────────────────────────────────────────────────────

def lambda_handler(event, context):
    print(f"[DEBUG] ========================================")
    print(f"[DEBUG] LAMBDA INVOCATION STARTED")
    print(f"[DEBUG] ========================================")
    print(f"[DEBUG] Event: {json.dumps(event)}")
    print(f"[DEBUG] Lambda Memory: {context.memory_limit_in_mb} MB")
    print(f"[DEBUG] Lambda Timeout: {context.get_remaining_time_in_millis() / 1000} seconds remaining")
    print(f"🔧 ONBOARDING_AVAILABLE: {ONBOARDING_AVAILABLE}")
    print(f"🔧 LANGGRAPH_AVAILABLE: {LANGGRAPH_AVAILABLE}")
    
    # Webhook verification
    if event.get("queryStringParameters"):
        print(f"[DEBUG] Webhook verification request detected")
        params = event["queryStringParameters"]
        if params.get("hub.verify_token") == VERIFY_TOKEN:
            print(f"[INFO] ✅ Webhook verification successful")
            return {
                'statusCode': 200,
                'body': params.get("hub.challenge")
            }
    
    try:
        body = json.loads(event["body"])
        value = body["entry"][0]["changes"][0]["value"]
        
        print(f"[DEBUG] Webhook payload received")
        print(f"[DEBUG] Payload keys: {list(value.keys())}")
        
        # Check if this is a status update (sent/delivered/read) - ignore these
        if "statuses" in value:
            print("[INFO] ⏭️  Status update received, ignoring")
            return {'statusCode': 200, 'body': 'ok'}
        
        # Check if messages exist
        if "messages" not in value:
            print("[INFO] ⏭️  No messages in webhook, ignoring")
            return {'statusCode': 200, 'body': 'ok'}
        
        msg = value["messages"][0]
        from_number = msg["from"]
        msg_type = msg.get("type")
        
        print(f"[INFO] 📱 Message from: {from_number}")
        print(f"[INFO] 📝 Message type: {msg_type}")
        
        # ═══════════════════════════════════════════════════════════════
        # FEATURE 1: Handle Interactive Button/List Responses
        # ═══════════════════════════════════════════════════════════════
        if msg_type == "interactive":
            print(f"[INTERACTIVE] Button/List response received")
            interactive_response = msg.get("interactive", {})
            response_type = interactive_response.get("type")  # button_reply or list_reply
            
            if response_type == "button_reply":
                button_id = interactive_response.get("button_reply", {}).get("id")
                print(f"[INTERACTIVE] Button clicked: {button_id}")
                
                # Handle language selection
                if button_id == "lang_english":
                    set_user_language(from_number, 'english')
                    print(f"[LANGUAGE] User selected English")
                    
                    # Delete existing profile and onboarding state to restart
                    if ONBOARDING_AVAILABLE:
                        try:
                            # Delete from both tables
                            onboarding_manager.onboarding_table.delete_item(Key={"user_id": from_number})
                            onboarding_manager.profile_table.delete_item(Key={"user_id": from_number})
                            print(f"[ONBOARDING] Deleted profile and state for re-onboarding in English")
                        except Exception as e:
                            print(f"[ONBOARDING] Delete error: {e}")
                    
                    # Start onboarding (without language parameter)
                    if ONBOARDING_AVAILABLE:
                        response, _ = onboarding_manager.process_onboarding_message(from_number, "start")
                        send_whatsapp_message(from_number, response)
                    else:
                        send_whatsapp_message(from_number, None, create_main_menu('english'))
                    return {'statusCode': 200, 'body': 'ok'}
                
                elif button_id == "lang_hindi":
                    set_user_language(from_number, 'hindi')
                    print(f"[LANGUAGE] User selected Hindi")
                    
                    # Delete existing profile and onboarding state to restart
                    if ONBOARDING_AVAILABLE:
                        try:
                            # Delete from both tables
                            onboarding_manager.onboarding_table.delete_item(Key={"user_id": from_number})
                            onboarding_manager.profile_table.delete_item(Key={"user_id": from_number})
                            print(f"[ONBOARDING] Deleted profile and state for re-onboarding in Hindi")
                        except Exception as e:
                            print(f"[ONBOARDING] Delete error: {e}")
                    
                    # Start onboarding (without language parameter)
                    if ONBOARDING_AVAILABLE:
                        response, _ = onboarding_manager.process_onboarding_message(from_number, "start")
                        send_whatsapp_message(from_number, response)
                    else:
                        send_whatsapp_message(from_number, None, create_main_menu('hindi'))
                    return {'statusCode': 200, 'body': 'ok'}
                
                # Get user's language preference
                user_lang = get_user_language(from_number)
                
                # Handle navigation button actions
                if button_id == "nav_back":
                    print(f"[NAV] Back button clicked")
                    if NAVIGATION_AVAILABLE:
                        nav = NavigationController(from_number)
                        nav.go_back()
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                    return {'statusCode': 200, 'body': 'ok'}
                
                elif button_id == "nav_home":
                    print(f"[NAV] Home button clicked")
                    if NAVIGATION_AVAILABLE:
                        nav = NavigationController(from_number)
                        nav.go_home()
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                    return {'statusCode': 200, 'body': 'ok'}
                
                elif button_id == "nav_cancel":
                    print(f"[NAV] Cancel button clicked")
                    if NAVIGATION_AVAILABLE:
                        nav = NavigationController(from_number)
                        nav.cancel()
                    
                    if user_lang == 'english':
                        msg = "❌ Cancelled. Starting fresh!"
                    else:
                        msg = "❌ रद्द कर दिया। नए सिरे से शुरू कर रहे हैं!"
                    
                    send_whatsapp_message(from_number, msg)
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                    return {'statusCode': 200, 'body': 'ok'}
                
                # Handle button actions
                elif button_id == "main_menu":
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                    return {'statusCode': 200, 'body': 'ok'}
                elif button_id == "crop_health":
                    if user_lang == 'english':
                        send_whatsapp_message(from_number, "🌿 Crop Health Check\n\nPlease send a photo of your crop or describe the problem.")
                    else:
                        send_whatsapp_message(from_number, "🌿 फसल स्वास्थ्य जांच\n\nकृपया अपनी फसल की तस्वीर भेजें या समस्या का वर्णन करें।")
                    return {'statusCode': 200, 'body': 'ok'}
                elif button_id == "market_price":
                    send_whatsapp_message(from_number, None, create_crop_selection_list())
                    return {'statusCode': 200, 'body': 'ok'}
                elif button_id == "budget_plan":
                    if user_lang == 'english':
                        send_whatsapp_message(from_number, "💰 Budget Planning\n\nPlease tell me:\n• Which crop?\n• How much land (acres)?\n• Where?\n\nExample: 'I need tomato budget for 2 acres in Kolhapur'")
                    else:
                        send_whatsapp_message(from_number, "💰 बजट योजना\n\nकृपया बताएं:\n• कौन सी फसल?\n• कितनी जमीन (एकड़)?\n• कहाँ?\n\nउदाहरण: 'मुझे टमाटर के लिए 2 एकड़ कोल्हापुर में बजट चाहिए'")
                    return {'statusCode': 200, 'body': 'ok'}
                elif button_id == "help":
                    if user_lang == 'english':
                        help_msg = "❓ Help\n\nI can help you with:\n\n🌿 Crop Disease Detection - Send photo\n📊 Market Prices - Tell crop name\n💰 Budget Planning - Tell crop, land, location\n\nAsk me anything!"
                    else:
                        help_msg = "❓ मदद\n\nमैं आपकी मदद कर सकता हूं:\n\n🌿 फसल रोग पहचान - तस्वीर भेजें\n📊 बाजार भाव - फसल का नाम बताएं\n💰 बजट योजना - फसल, जमीन, स्थान बताएं\n\nकुछ भी पूछें!"
                    send_whatsapp_message(from_number, help_msg, create_back_button(user_lang))
                    return {'statusCode': 200, 'body': 'ok'}
                elif button_id == "sos":
                    user_lang = get_user_language(from_number)
                    if user_lang == 'english':
                        sos_msg = "🆘 Emergency Help\n\nPlease describe your problem. We'll help immediately.\n\nOr call:\n📞 Kisan Helpline: 1800-180-1551"
                    else:
                        sos_msg = "🆘 आपातकालीन सहायता\n\nकृपया अपनी समस्या का वर्णन करें। हम तुरंत मदद करेंगे।\n\nया कॉल करें:\n📞 किसान हेल्पलाइन: 1800-180-1551"
                    send_whatsapp_message(from_number, sos_msg)
                    return {'statusCode': 200, 'body': 'ok'}
            
            elif response_type == "list_reply":
                list_id = interactive_response.get("list_reply", {}).get("id")
                print(f"[INTERACTIVE] List item selected: {list_id}")
                
                # Get user's language preference
                user_lang = get_user_language(from_number)
                
                # Handle main menu selections
                if list_id == "crop_health":
                    if user_lang == 'english':
                        prompt_msg = "🌿 *Crop Health Check*\n\nPlease send a photo of your crop or describe the problem in detail."
                    else:
                        prompt_msg = "🌿 *फसल स्वास्थ्य जांच*\n\nकृपया अपनी फसल की तस्वीर भेजें या समस्या का विस्तार से वर्णन करें।"
                    
                    # Save this prompt to conversation history
                    save_conversation(from_number, "🔍 Crop Health", prompt_msg, "menu")
                    
                    # Set user state
                    try:
                        from user_state_manager import set_user_state
                        set_user_state(from_number, 'awaiting_crop_health', {'service': 'crop'})
                    except:
                        pass
                    
                    send_whatsapp_message(from_number, prompt_msg)
                    return {'statusCode': 200, 'body': 'ok'}
                
                elif list_id == "market_price":
                    # Don't show dropdown - ask user to type crop name
                    if user_lang == 'english':
                        prompt_msg = "📊 *Market Prices*\n\nWhich crop price do you want to check?\n\nJust type the crop name:\n• Tomato\n• Onion\n• Wheat\n• Rice\n• Any crop!\n\nWe support 300+ crops across India 🇮🇳"
                    else:
                        prompt_msg = "📊 *बाजार भाव*\n\nआप किस फसल का भाव जानना चाहते हैं?\n\nबस फसल का नाम लिखें:\n• टमाटर\n• प्याज\n• गेहूं\n• चावल\n• कोई भी फसल!\n\nहम भारत की 300+ फसलों का समर्थन करते हैं 🇮🇳"
                    
                    # Save to conversation history and set state
                    save_conversation(from_number, "📊 Market Price", prompt_msg, "menu")
                    
                    # Import state manager
                    try:
                        from user_state_manager import set_user_state
                        set_user_state(from_number, 'awaiting_market_query', {'service': 'market'})
                    except:
                        pass
                    
                    send_whatsapp_message(from_number, prompt_msg)
                    return {'statusCode': 200, 'body': 'ok'}
                
                elif list_id == "budget_plan":
                    if user_lang == 'english':
                        prompt_msg = "💰 *Budget Planning*\n\nPlease tell me:\n• Which crop?\n• How much land (acres)?\n• Location?\n\nExample: 'I need tomato budget for 2 acres in Kolhapur'"
                    else:
                        prompt_msg = "💰 *बजट योजना*\n\nकृपया बताएं:\n• कौन सी फसल?\n• कितनी जमीन (एकड़)?\n• स्थान?\n\nउदाहरण: 'मुझे टमाटर के लिए 2 एकड़ कोल्हापुर में बजट चाहिए'"
                    
                    # Save this prompt to conversation history so AI knows context
                    save_conversation(from_number, "💰 Budget Planning", prompt_msg, "menu")
                    
                    # Set user state to awaiting budget details
                    try:
                        from user_state_manager import set_user_state
                        set_user_state(from_number, 'awaiting_budget_details', {'service': 'finance'})
                    except:
                        pass
                    
                    send_whatsapp_message(from_number, prompt_msg)
                    return {'statusCode': 200, 'body': 'ok'}
                
                elif list_id == "weather":
                    # Get user's location (default to Maharashtra if no profile)
                    location = 'Maharashtra'
                    
                    if WEATHER_AVAILABLE:
                        try:
                            weather = get_weather_forecast(location)
                            weather_analysis = analyze_weather_for_farming(weather)
                            reply = format_weather_response(location, weather_analysis)
                            send_whatsapp_message(from_number, reply, create_back_button(user_lang))
                        except:
                            if user_lang == 'english':
                                send_whatsapp_message(from_number, "Weather service temporarily unavailable. Please try again later.")
                            else:
                                send_whatsapp_message(from_number, "मौसम सेवा अस्थायी रूप से अनुपलब्ध है। कृपया बाद में पुनः प्रयास करें।")
                    return {'statusCode': 200, 'body': 'ok'}
                
                elif list_id == "sos":
                    user_lang = get_user_language(from_number)
                    if user_lang == 'english':
                        sos_msg = "🆘 *Emergency Help*\n\nPlease describe your problem. We'll help immediately.\n\n*Call Now*:\n📞 Kisan Helpline: 1800-180-1551\n📞 Agriculture Dept: 1800-180-1551"
                    else:
                        sos_msg = "🆘 *आपातकालीन सहायता*\n\nकृपया अपनी समस्या का वर्णन करें। हम तुरंत मदद करेंगे।\n\n*अभी कॉल करें*:\n📞 किसान हेल्पलाइन: 1800-180-1551\n📞 कृषि विभाग: 1800-180-1551"
                    send_whatsapp_message(from_number, sos_msg)
                    return {'statusCode': 200, 'body': 'ok'}
                
                # Handle crop selection for market prices
                elif list_id in ["rice", "wheat", "maize", "tomato", "onion", "potato", "sugarcane", "cotton", "soybean"]:
                    # Trigger market query
                    user_message = f"What is the price of {list_id}?"
                    reply = handle_market_query(user_message)
                    send_whatsapp_message(from_number, reply, create_back_button(user_lang))
                    return {'statusCode': 200, 'body': 'ok'}
            
            # If we reach here, unknown button/list action
            user_lang = get_user_language(from_number)
            if user_lang == 'english':
                send_whatsapp_message(from_number, "I didn't understand. Please try again.", create_main_menu(user_lang))
            else:
                send_whatsapp_message(from_number, "मुझे समझ नहीं आया। कृपया फिर से कोशिश करें।", create_main_menu(user_lang))
            return {'statusCode': 200, 'body': 'ok'}
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: CHECK USER STATUS (ALWAYS FIRST)
        # ═══════════════════════════════════════════════════════════════
        is_new_user, onboarding_state, user_profile = check_user_status(from_number)
        
        print(f"👤 User Status: is_new={is_new_user}, state={onboarding_state}, has_profile={user_profile is not None}")
        print(f"🔍 DEBUG: is_new={is_new_user}, state='{onboarding_state}', profile={user_profile}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: HANDLE NEW USERS (NO PROFILE EXISTS)
        # ═══════════════════════════════════════════════════════════════
        if is_new_user:
            print(f"🆕 NEW USER DETECTED: {from_number} - Starting onboarding")
            
            if msg_type == "text":
                user_message = msg["text"]["body"]
                response, is_completed = onboarding_manager.process_onboarding_message(from_number, user_message)
                send_whatsapp_message(from_number, response)
                
                # If onboarding completed, add to knowledge graph
                if is_completed:
                    profile = onboarding_manager.get_user_profile(from_number)
                    if profile:
                        knowledge_graph.add_farmer_to_graph(profile)
                        print(f"✅ Onboarding completed! Added {profile.get('name')} to knowledge graph")
                
                return {'statusCode': 200, 'body': 'ok'}
            else:
                # New user sent non-text message (image/video/audio)
                send_whatsapp_message(
                    from_number,
                    "🙏 नमस्ते! KisaanMitra में आपका स्वागत है!\n\nपहले अपना रजिस्ट्रेशन पूरा करें।\nकृपया 'Hi' टाइप करें।"
                )
                return {'statusCode': 200, 'body': 'ok'}
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: HANDLE USERS IN ONBOARDING PROCESS
        # ═══════════════════════════════════════════════════════════════
        if onboarding_state and onboarding_state != "completed":
            print(f"📝 USER IN ONBOARDING: {from_number}, state: {onboarding_state}")
            
            if msg_type == "text":
                user_message = msg["text"]["body"]
                response, is_completed = onboarding_manager.process_onboarding_message(from_number, user_message)
                send_whatsapp_message(from_number, response)
                
                # If onboarding completed, add to knowledge graph
                if is_completed:
                    profile = onboarding_manager.get_user_profile(from_number)
                    if profile:
                        knowledge_graph.add_farmer_to_graph(profile)
                        print(f"✅ Onboarding completed! Added {profile.get('name')} to knowledge graph")
                
                return {'statusCode': 200, 'body': 'ok'}
            else:
                # User in onboarding sent non-text message
                send_whatsapp_message(
                    from_number,
                    "कृपया पहले अपना रजिस्ट्रेशन पूरा करें।\nआपके सवाल का जवाब दें।"
                )
                return {'statusCode': 200, 'body': 'ok'}
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: EXISTING USER WITH COMPLETED PROFILE - ROUTE TO AGENTS
        # ═══════════════════════════════════════════════════════════════
        print(f"✅ EXISTING USER: {from_number} ({user_profile.get('name') if user_profile else 'Unknown'}) - Routing to agents")
        
        if msg_type == "text":
            user_message = msg["text"]["body"]
            print(f"[INFO] 📨 User message: {user_message}")
            
            # ═══════════════════════════════════════════════════════════════
            # SPECIAL CASE: "Hi" shows menu for existing users, language selection for new
            # ═══════════════════════════════════════════════════════════════
            if user_message.strip().lower() in ['hi', 'hello', 'hey', 'start']:
                print(f"[GREETING] User said '{user_message}'")
                user_lang = get_user_language(from_number)
                
                # Show main menu for existing users
                if INTERACTIVE_MESSAGES_AVAILABLE:
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                else:
                    if user_lang == 'english':
                        send_whatsapp_message(from_number, "Hello! How can I help you today?")
                    else:
                        send_whatsapp_message(from_number, "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?")
                
                print(f"[INFO] ✅ Main menu sent to existing user")
                return {'statusCode': 200, 'body': 'ok'}
            
            # ═══════════════════════════════════════════════════════════════
            # NAVIGATION COMMANDS: back, home, cancel
            # ═══════════════════════════════════════════════════════════════
            user_message_lower = user_message.strip().lower()
            user_lang = get_user_language(from_number)
            
            if user_message_lower in ['back', 'पीछे']:
                print(f"[NAV] User requested: BACK")
                if NAVIGATION_AVAILABLE:
                    nav = NavigationController(from_number)
                    previous_screen = nav.go_back()
                    print(f"[NAV] Navigated back to: {previous_screen}")
                
                # Show main menu
                if INTERACTIVE_MESSAGES_AVAILABLE:
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                else:
                    if user_lang == 'english':
                        send_whatsapp_message(from_number, "Returning to main menu...")
                    else:
                        send_whatsapp_message(from_number, "मुख्य मेनू पर लौट रहे हैं...")
                
                return {'statusCode': 200, 'body': 'ok'}
            
            elif user_message_lower in ['home', 'menu', 'main menu', 'मुख्य मेनू', 'होम']:
                print(f"[NAV] User requested: HOME")
                if NAVIGATION_AVAILABLE:
                    nav = NavigationController(from_number)
                    nav.go_home()
                    print(f"[NAV] Returned to home")
                
                # Show main menu
                if INTERACTIVE_MESSAGES_AVAILABLE:
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                else:
                    if user_lang == 'english':
                        send_whatsapp_message(from_number, "Main menu")
                    else:
                        send_whatsapp_message(from_number, "मुख्य मेनू")
                
                return {'statusCode': 200, 'body': 'ok'}
            
            elif user_message_lower in ['cancel', 'stop', 'restart', 'रद्द करें', 'बंद करें']:
                print(f"[NAV] User requested: CANCEL")
                if NAVIGATION_AVAILABLE:
                    nav = NavigationController(from_number)
                    nav.cancel()
                    print(f"[NAV] Cancelled and cleared state")
                
                # Show confirmation and main menu
                if user_lang == 'english':
                    msg = "❌ Cancelled. Starting fresh!"
                else:
                    msg = "❌ रद्द कर दिया। नए सिरे से शुरू कर रहे हैं!"
                
                send_whatsapp_message(from_number, msg)
                
                if INTERACTIVE_MESSAGES_AVAILABLE:
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                
                return {'statusCode': 200, 'body': 'ok'}
            
            # SPECIAL CASE: "reset" command to restart onboarding
            if user_message.strip().lower() == 'reset':
                print(f"[RESET] User requested reset")
                
                # Delete existing profile and onboarding state
                if ONBOARDING_AVAILABLE:
                    try:
                        onboarding_manager.onboarding_table.delete_item(Key={"user_id": from_number})
                        onboarding_manager.profile_table.delete_item(Key={"user_id": from_number})
                        print(f"[ONBOARDING] Profile deleted for reset")
                    except Exception as e:
                        print(f"[ONBOARDING] Delete error: {e}")
                
                # Show language selection
                if INTERACTIVE_MESSAGES_AVAILABLE:
                    send_whatsapp_message(from_number, None, create_language_selection())
                else:
                    send_whatsapp_message(from_number, "Welcome! Send 'English' or 'Hindi' to choose language.")
                
                print(f"[INFO] ✅ Reset complete, language selection sent")
                return {'statusCode': 200, 'body': 'ok'}
            
            # ═══════════════════════════════════════════════════════════════
            # FEATURE 2: STATE-BASED ROUTING - Check user state first
            # ═══════════════════════════════════════════════════════════════
            skip_orchestrator = False
            try:
                from user_state_manager import get_user_state, clear_user_state, get_agent_from_state
                user_state = get_user_state(from_number)
                
                if user_state and user_state.get('state'):
                    # User has a pending state, route directly to appropriate agent
                    agent = get_agent_from_state(user_state['state'])
                    if agent:
                        print(f"[STATE ROUTING] User in state '{user_state['state']}', routing to {agent.upper()} agent")
                        # Clear state after routing
                        clear_user_state(from_number)
                        # Skip AI orchestrator, go directly to agent
                        skip_orchestrator = True
            except Exception as e:
                print(f"[STATE ERROR] Failed to check user state: {e}")
                user_state = None
            
            # ═══════════════════════════════════════════════════════════════
            # ULTRA-FAST ROUTING: Skip AI for 95% of queries (0.01s vs 2s)
            # ═══════════════════════════════════════════════════════════════
            print(f"[FAST ROUTE] Using keyword-based routing (no AI)")
            msg_lower = user_message.lower()
            agent = None
            
            # Budget/Finance keywords (highest priority)
            if any(kw in msg_lower for kw in ['budget', 'cost', 'finance', 'loan', 'scheme', 'expense', 'sheet', 'बजट', 'खर्च', 'योजना', 'लागत']):
                agent = "finance"
                print(f"[FAST ROUTE] ✅ Finance agent (keyword match)")
            
            # Market price keywords
            elif any(kw in msg_lower for kw in ['price', 'rate', 'market', 'mandi', 'bhav', 'sell', 'भाव', 'कीमत', 'मंडी', 'बाजार']):
                agent = "market"
                print(f"[FAST ROUTE] ✅ Market agent (keyword match)")
            
            # Crop health keywords
            elif any(kw in msg_lower for kw in ['disease', 'pest', 'sick', 'problem', 'yellow', 'spots', 'dying', 'रोग', 'बीमारी', 'कीट']):
                agent = "crop"
                print(f"[FAST ROUTE] ✅ Crop agent (keyword match)")
            
            # Default to general (crop recommendations, advice)
            else:
                agent = "general"
                print(f"[FAST ROUTE] ✅ General agent (default)")
            
            print(f"[DEBUG] Executing {agent} agent handler...")
            user_lang = get_user_language(from_number, user_message)  # Pass message for auto-detection
            
            if agent == "greeting":
                # For existing users, show main menu
                if INTERACTIVE_MESSAGES_AVAILABLE:
                    send_whatsapp_message(from_number, None, create_main_menu(user_lang))
                else:
                    if user_lang == 'english':
                        reply = "Hello! How can I help you today?"
                    else:
                        reply = "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?"
                    send_whatsapp_message(from_number, reply)
                print(f"[INFO] ✅ Greeting handled")
                return {'statusCode': 200, 'body': 'ok'}
            elif agent == "crop":
                reply = handle_crop_query(user_message, from_number, user_lang)
            elif agent == "market":
                reply = handle_market_query(user_message, user_lang)
            elif agent == "finance":
                reply = handle_finance_query(user_message, from_number, user_lang)
            else:
                # General agent - handles all other queries
                print(f"[DEBUG] Routing to GENERAL agent for query: {user_message}")
                reply = handle_general_query(user_message, user_lang)
            
            print(f"[DEBUG] Agent execution complete, reply length: {len(reply)} chars")
            print(f"[DEBUG] Reply preview: {reply[:200]}...")
            
            # ═══════════════════════════════════════════════════════════════
            # OPTIMIZATION: Reasoning layer DISABLED for performance
            # (was adding 14+ seconds per message)
            # ═══════════════════════════════════════════════════════════════
            # if AI_ORCHESTRATOR_AVAILABLE and agent in ["finance", "crop"]:
            #     print(f"[AI ORCHESTRATOR] Adding reasoning layer to response...")
            #     reply = orchestrator.generate_reasoning_response(user_message, reply, context)
            
            # Save conversation with response
            save_conversation(from_number, user_message, reply, agent)
            
            # Send reply without repetitive prompts
            send_whatsapp_message(from_number, reply)
            
            print(f"[INFO] ✅ Request completed successfully - Agent: {agent.upper()}")
            print(f"[INFO] ✅ Response sent to user")
            
        elif msg_type == "image":
            print(f"[DEBUG] ===== IMAGE ANALYSIS =====")
            media_id = msg["image"]["id"]
            print(f"[DEBUG] Image media ID: {media_id}")
            
            send_whatsapp_message(from_number, "🔍 Analyzing your crop image, please wait...")
            
            print(f"[DEBUG] Downloading image from WhatsApp...")
            image_bytes = download_whatsapp_image(media_id)
            print(f"[DEBUG] Image downloaded, size: {len(image_bytes)} bytes")
            
            # ═══════════════════════════════════════════════════════════════
            # FEATURE 4: Enhanced Disease Detection with Confidence Scores
            # ═══════════════════════════════════════════════════════════════
            if ENHANCED_DISEASE_DETECTION_AVAILABLE:
                print(f"[ENHANCED DETECTION] Using advanced disease detection with confidence scoring...")
                
                # Detect disease with confidence - pass bedrock client (works for both Anthropic and Bedrock)
                diagnosis = detect_disease_with_confidence(image_bytes, bedrock)
                
                # Format response
                reply = format_disease_response(diagnosis)
                
                # Save to history for tracking
                save_disease_detection(from_number, diagnosis, conversation_table)
                
                print(f"[ENHANCED DETECTION] Disease: {diagnosis['primary_disease']}, Confidence: {diagnosis['confidence']}")
            else:
                # Fallback to original Kindwise API
                print(f"[DEBUG] Analyzing image with Kindwise API...")
                result = analyze_crop_image(image_bytes)
                print(f"[DEBUG] Image analysis complete")
                
                print(f"[DEBUG] Formatting crop analysis result...")
                reply = format_crop_result(result)
            
            send_whatsapp_message(from_number, reply)
            
            print(f"[INFO] ✅ Image analysis completed successfully")
            
        elif msg_type == "audio" or msg_type == "voice":
            print(f"[VOICE] Voice/audio message received")
            user_lang = get_user_language(from_number)
            
            if user_lang == 'english':
                send_whatsapp_message(from_number, "Please send your question as text or send a crop photo for disease detection.")
            else:
                send_whatsapp_message(from_number, "कृपया अपना सवाल टेक्स्ट में लिखें या फसल की तस्वीर भेजें।")
            
            print(f"[INFO] ✅ Voice message handled")
            
        else:
            print(f"[DEBUG] Unsupported message type: {msg_type}")
            send_whatsapp_message(from_number, "Please send a text message or crop image for disease detection.")
    
    except Exception as e:
        print(f"[ERROR] ❌ Lambda execution error: {e}")
        import traceback
        print(f"[ERROR] Full traceback:")
        traceback.print_exc()
    
    print(f"[DEBUG] ========================================")
    print(f"[DEBUG] LAMBDA INVOCATION COMPLETED")
    print(f"[DEBUG] ========================================")
    return {'statusCode': 200, 'body': 'ok'}
