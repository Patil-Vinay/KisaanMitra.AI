import json
import urllib3
import os
import boto3
import base64
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

http = urllib3.PoolManager()

# Environment variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mySecret_123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
CROP_HEALTH_API_KEY = os.environ.get("CROP_HEALTH_API_KEY")
AGMARKNET_API_KEY = os.environ.get("AGMARKNET_API_KEY")

# AWS clients
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")  # Cross-region inference
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
s3 = boto3.client("s3", region_name="ap-south-1")

# Tables
conversation_table = dynamodb.Table("kisaanmitra-conversations")
market_data_table = dynamodb.Table("kisaanmitra-market-data")
finance_table = dynamodb.Table("kisaanmitra-finance")

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

def get_conversation_history(user_id, limit=10):
    """Get recent conversation history from DynamoDB with enhanced context"""
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
    """Build enhanced context string from conversation history"""
    if not history:
        print("[DEBUG] No conversation history available")
        return ""
    
    print(f"[DEBUG] Building context from {len(history)} history items")
    context = "Previous conversation context:\n"
    for item in reversed(history[-5:]):  # Last 5 messages for better context
        msg = item.get('message', '')
        resp = item.get('response', '')
        agent = item.get('agent', 'general')
        
        context += f"User: {msg}\n"
        # Include more of the response for better context
        context += f"Assistant ({agent}): {resp[:200]}...\n"
    
    context += "\nBased on this conversation history, provide contextually relevant responses.\n"
    context += "Current query:\n"
    print(f"[DEBUG] Context built successfully, length: {len(context)} chars")
    return context

# ─── Bedrock with Cross-Region Inference ────────────────────────────────────

def ask_bedrock(prompt, system_prompt=None, conversation_context=""):
    """Call Bedrock using cross-region inference profile with context"""
    try:
        print(f"[DEBUG] Calling Bedrock - Model: us.amazon.nova-pro-v1:0")
        print(f"[DEBUG] Prompt length: {len(prompt)} chars")
        print(f"[DEBUG] Context length: {len(conversation_context)} chars")
        print(f"[DEBUG] System prompt: {system_prompt[:100] if system_prompt else 'None'}...")
        
        # Add conversation context if available
        full_prompt = conversation_context + prompt if conversation_context else prompt
        
        messages = [{"role": "user", "content": [{"text": full_prompt}]}]
        
        kwargs = {
            "modelId": "us.amazon.nova-pro-v1:0",  # Upgraded to Nova Pro for better accuracy
            "messages": messages,
            "inferenceConfig": {"maxTokens": 1500, "temperature": 0.7}  # Increased tokens for detailed responses
        }
        
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]
        
        print(f"[DEBUG] Sending request to Bedrock...")
        response = bedrock.converse(**kwargs)
        result = response["output"]["message"]["content"][0]["text"]
        print(f"[DEBUG] Bedrock response received, length: {len(result)} chars")
        return result
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
    crop_keywords = ["disease", "pest", "leaf", "yellow", "spots", "dying", "बीमारी", "रोग", "पत्ती"]
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
    
    # Default - friendly chat
    return "general"

def handle_greeting():
    """Handle greetings with a friendly response"""
    print(f"[DEBUG] ===== GREETING AGENT =====")
    greetings = [
        "Hello! I'm Kisaan Mitra, your farming assistant. How can I help you today?",
        "Hi there! I'm here to help with your farming questions. What's on your mind?",
        "Hey! I'm Kisaan Mitra. I can help with crop problems, market prices, or farming advice. What do you need?",
    ]
    import random
    selected = random.choice(greetings)
    print(f"[DEBUG] Selected greeting: {selected[:50]}...")
    return selected

def handle_crop_query(user_message):
    """Handle crop-related text queries"""
    print(f"[DEBUG] ===== CROP AGENT =====")
    print(f"[DEBUG] Processing crop query: {user_message}")
    system_prompt = """You are a helpful farming assistant. 
Help farmers with crop diseases, pests, and treatments.
Reply in simple English. Keep it short (2-3 sentences) and practical."""
    
    result = ask_bedrock(user_message, system_prompt)
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

def handle_market_query(user_message):
    """Handle market-related queries with AI state extraction"""
    print(f"[DEBUG] ===== MARKET AGENT =====")
    print(f"[DEBUG] Processing market query: {user_message}")
    
    system_prompt = """You are a market expert helping farmers.
Provide market prices and trends in simple English.
Keep it short (2-3 sentences) and practical."""
    
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
            return format_market_response_fast(detected_crop, market_data)
        else:
            print(f"[DEBUG] No market data found for {detected_crop}")
    
    # Fallback to AI for general market questions
    print(f"[DEBUG] Falling back to AI for market query")
    return ask_bedrock(user_message, system_prompt)

def extract_crop_with_ai(user_message, bedrock_client, conversation_history=""):
    """Use AI to extract crop name from user message with conversation context"""
    print(f"[DEBUG] Extracting crop name using AI...")
    print(f"[DEBUG] Message: {user_message}")
    print(f"[DEBUG] Has conversation context: {len(conversation_history) > 0}")
    
    prompt = f"""You are an expert agricultural assistant. Extract the crop name from the farmer's message.

{conversation_history}

Current message: "{user_message}"

Instructions:
- Extract ONLY the crop name mentioned
- If multiple crops mentioned, extract the primary one
- Return lowercase crop name
- Handle common variations (e.g., "chilli" → "chilly", "brinjal" → "eggplant")
- If no crop mentioned, return "unknown"

Examples:
"I want to grow soybean" → soybean
"give me onion budget" → onion
"chilly farming cost" → chilly
"mushroom cultivation" → mushroom
"what about tomatoes?" → tomato
"brinjal" → brinjal

Reply with ONLY the crop name:"""
    
    try:
        print(f"[DEBUG] Calling Bedrock for crop extraction...")
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",  # Using Pro for better accuracy
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 50, "temperature": 0.2}  # Lower temp for precision
        )
        crop_name = response["output"]["message"]["content"][0]["text"].strip().lower()
        print(f"[INFO] ✅ AI extracted crop: {crop_name}")
        return crop_name if crop_name != "unknown" else None
    except Exception as e:
        print(f"[ERROR] Crop extraction error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None


def extract_state_with_ai(user_message, bedrock_client):
    """Use AI to extract state name from user message"""
    print(f"[DEBUG] Extracting state/location using AI...")
    
    prompt = f"""Extract the Indian state or city name from this farmer's message: "{user_message}"

Instructions:
- Extract the state name if mentioned (e.g., "Maharashtra", "Punjab", "Gujarat")
- If city mentioned, return the state it belongs to (e.g., "Mumbai" → "Maharashtra", "Amritsar" → "Punjab")
- Return proper case state name (e.g., "Maharashtra" not "maharashtra")
- If no location mentioned, return "Maharashtra" (default)
- Return ONLY the state name, nothing else

Examples:
"Give me wheat budget in Mumbai" → Maharashtra
"Onion price in Amritsar" → Punjab
"Cotton farming in Gujarat" → Gujarat
"Tomato budget for 1 acre in Kolhapur" → Maharashtra
"Rice cultivation in Ludhiana" → Punjab
"What is wheat price?" → Maharashtra

Reply with ONLY the state name:"""
    
    try:
        print(f"[DEBUG] Calling Bedrock for state extraction...")
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 30, "temperature": 0.1}  # Very low temp for precision
        )
        state_name = response["output"]["message"]["content"][0]["text"].strip()
        print(f"[INFO] ✅ AI extracted state: {state_name}")
        return state_name
    except Exception as e:
        print(f"[ERROR] State extraction error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return "Maharashtra"  # Default fallback


def generate_crop_budget_with_ai(crop_name, land_size, location, bedrock_client, state_name=None):
    """Generate highly accurate crop budget with feasibility analysis using Claude Sonnet 4"""
    if not state_name:
        state_name = location

    print(f"[DEBUG] Generating AI budget for crop: {crop_name}, land: {land_size} acre(s), location: {location}, state: {state_name}")

    # Try to get real market price from AgMarkNet for revenue calculation
    real_market_price = None
    price_source = "ai_estimate"

    # Try scraping first (faster) - use state name for API
    print(f"[DEBUG] Attempting to fetch real market price via scraping...")
    try:
        from market_data_sources import scrape_agmarknet_website
        scraped_data = scrape_agmarknet_website(crop_name, state_name)
        if scraped_data and scraped_data.get('average_price'):
            real_market_price = scraped_data['average_price']
            price_source = "agmarknet_scrape"
            print(f"[INFO] ✅ Real market price from AgMarkNet scraping: ₹{real_market_price}/quintal")
    except Exception as e:
        print(f"[DEBUG] Scraping failed: {e}")

    # Try API if scraping failed
    if not real_market_price and AGMARKNET_API_KEY and AGMARKNET_API_KEY != "not_available":
        print(f"[DEBUG] Attempting to fetch real market price from AgMarkNet API...")
        try:
            mandi_data = get_mandi_prices(crop_name, state_name)
            if mandi_data and len(mandi_data) > 0:
                real_market_price = int(float(mandi_data[0].get("modal_price", 0)))
                price_source = "agmarknet_api"
                print(f"[INFO] ✅ Real market price from AgMarkNet API: ₹{real_market_price}/quintal")
        except Exception as e:
            print(f"[DEBUG] Could not fetch AgMarkNet API price: {e}")

    if not real_market_price:
        print(f"[DEBUG] No real market price available, AI will estimate")

    market_price_instruction = ""
    if real_market_price:
        market_price_instruction = f"\n**IMPORTANT: Use EXACTLY ₹{real_market_price} as the market price per quintal (from AgMarkNet real-time data).**\n"

    prompt = f"""You are an expert agricultural economist specializing in Indian farming. Analyze the feasibility and generate a detailed budget for {crop_name} cultivation.

**Farm Details:**
- Crop: {crop_name}
- Location: {location}
- Land Size: {land_size} acre(s)
{market_price_instruction}
**Task 1: Feasibility Analysis**
First, analyze if {crop_name} is suitable for {location} region considering:
- Climate compatibility (temperature, rainfall, season)
- Soil requirements vs regional soil types
- Water availability needs
- Market demand in the region
- Risk factors specific to {location}

**Task 2: Budget Generation**
Generate a realistic budget with current 2026 Indian market rates.

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
Yield: [number only]
Price_Per_Quintal: [number only]
Revenue: [number only]
Profit: [number only]

RISKS: [One line about main risks]
RECOMMENDATION: [One line practical advice]

**Example for reference:**
FEASIBILITY: SUITABLE
REASON: Good climate match for mushroom cultivation in March
BEST_SEASON: Winter to Spring
CLIMATE_MATCH: GOOD

Seeds: 15000
Fertilizer: 25000
Pesticides: 8000
Irrigation: 12000
Labor: 35000
Machinery: 10000
Total_Cost: 105000
Yield: 80
Price_Per_Quintal: 4000
Revenue: 320000
Profit: 215000

RISKS: Temperature control critical for mushroom cultivation
RECOMMENDATION: Use controlled environment for better yields

Now generate for {crop_name} in {location} for {land_size} acre(s):"""

    try:
        print(f"[DEBUG] Calling Bedrock for budget generation...")
        print(f"[DEBUG] Model: us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        print(f"[DEBUG] Using real market price from AgMarkNet: {real_market_price is not None}")
        response = bedrock_client.converse(
            modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Claude Sonnet 4 for superior accuracy
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 3000, "temperature": 0.3}
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
        "expected_price": r'Price[_\s]Per[_\s]Quintal[:\s]+₹?\s*([\d,]+)',
        "expected_revenue": r'Revenue[:\s]+₹?\s*([\d,]+)',
        "expected_profit": r'Profit[:\s]+₹?\s*([\d,]+)'
    }

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

def handle_finance_query(user_message, user_id="unknown"):
    """Handle finance-related queries with enhanced AI and memory"""
    print(f"[DEBUG] ===== FINANCE AGENT =====")
    print(f"[DEBUG] Processing finance query: {user_message}")
    print(f"[DEBUG] User ID: {user_id}")

    system_prompt = """You are an expert agricultural finance advisor for Indian farmers.
Provide accurate, practical financial advice for farming operations.
Reply in simple, clear English. Be specific and actionable.
IMPORTANT: Always use ₹ (Rupee symbol) for Indian currency, never use $."""

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

        # Extract crop using AI with conversation context
        crop_name = extract_crop_with_ai(user_message, bedrock, context)

        if not crop_name:
            print(f"[DEBUG] ❌ No crop detected, asking user to specify")
            return "Please specify which crop you want to grow. For example: 'I want to grow tomato' or 'give me chilly budget'"

        # Extract land size
        land_size = 1
        import re
        size_match = re.search(r'(\d+)\s*(acre|एकड़|hectare)', message_lower)
        if size_match:
            land_size = int(size_match.group(1))
            print(f"[DEBUG] Land size extracted: {land_size} acre(s)")
        else:
            print(f"[DEBUG] No land size specified, using default: 1 acre")

        # Extract location and state using AI (no hardcoding!)
        print(f"[DEBUG] Using AI to extract location and state...")
        state_name = extract_state_with_ai(user_message, bedrock)
        
        # For display purposes, try to extract city name
        location = state_name  # Default to state name
        
        # Try to find city name in message
        location_patterns = [
            r'in\s+(\w+)',
            r'from\s+(\w+)',
            r'at\s+(\w+)',
            r'location\s+is\s+(\w+)',
            r'farm\s+in\s+(\w+)'
        ]
        
        months = ["january", "february", "march", "april", "may", "june", 
                  "july", "august", "september", "october", "november", "december",
                  "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, message_lower, re.IGNORECASE)
            if location_match:
                extracted = location_match.group(1).lower()
                # Skip month names
                if extracted not in months:
                    location = extracted.title()
                    print(f"[DEBUG] ✅ Extracted city/location: {location}")
                    break
        
        print(f"[INFO] 📍 Final location: {location}, State for API: {state_name}")
        print(f"[INFO] 📊 Generating budget for {crop_name}, {land_size} acre(s) in {location}")

        # Generate budget using enhanced AI (pass both city and state)
        budget = generate_crop_budget_with_ai(crop_name, land_size, location, bedrock, state_name)

        if not budget:
            print(f"[ERROR] ❌ Budget generation failed for {crop_name}")
            return f"I'm having trouble generating a budget for {crop_name}. Please try again or ask about a different crop."

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
        message += f"• Yield: {budget['expected_yield']} quintal\n"
        
        # Show market price with data source
        price_source_label = {
            "agmarknet_scrape": "AgMarkNet (Scraped)",
            "agmarknet_api": "AgMarkNet API",
            "ai_estimate": "AI Estimate"
        }
        price_source_emoji = {
            "agmarknet_scrape": "🌐",
            "agmarknet_api": "📡",
            "ai_estimate": "🤖"
        }
        source = budget.get('data_source', 'ai_estimate')
        price_label = price_source_label.get(source, "AI Estimate")
        price_emoji = price_source_emoji.get(source, "🤖")
        
        message += f"• Market Price: ₹{budget['expected_price']}/quintal {price_emoji}\n"
        
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
        
        # Data source transparency
        message += f"📌 *Data Sources*:\n"
        message += f"• Costs: AI Estimates\n"
        message += f"• Price: {price_label}\n"
        message += f"• Analysis: AI (Claude Sonnet 4)\n\n"
        message += "💬 Verify with local suppliers\n"
        message += "? Need loan or scheme info? Just ask!"
        print(f"[DEBUG] Budget response formatted successfully with data source labels")
        return message
        if budget.get('recommendation'):
            message += f"💡 *Tip*: {budget['recommendation']}\n\n"
        else:
            message += "\n"
        
        message += "? Need loan or scheme info? Just ask!"
        print(f"[DEBUG] Budget response formatted successfully with feasibility analysis")
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
        print(f"[DEBUG] Loan response generated")
        return message

    # Fallback to AI with enhanced context
    print(f"[DEBUG] Falling back to AI for general finance query")
    return ask_bedrock(user_message, system_prompt, context)

def handle_general_query(user_message):
    """Handle general queries - friendly conversation"""
    print(f"[DEBUG] ===== GENERAL AGENT =====")
    print(f"[DEBUG] Processing general query: {user_message}")
    system_prompt = """You are Kisaan Mitra, a friendly farming assistant.
Have a natural conversation in simple English.
Be helpful and warm. Keep responses short (2-3 sentences).
If they ask about farming problems, guide them to be specific."""
    
    result = ask_bedrock(user_message, system_prompt)
    print(f"[DEBUG] General agent response generated")
    return result

# ─── WhatsApp ─────────────────────────────────────────────────────────────────

def send_whatsapp_message(to, message):
    """Send WhatsApp message"""
    print(f"[DEBUG] Sending WhatsApp message to: {to}")
    print(f"[DEBUG] Message length: {len(message)} chars")
    print(f"[DEBUG] Message preview: {message[:100]}...")
    
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = http.request("POST", url, body=json.dumps(data), headers=headers)
    print(f"[INFO] ✅ WhatsApp API response: {response.status}")
    if response.status != 200:
        print(f"[ERROR] WhatsApp API error response: {response.data}")

# ─── Lambda Handler ───────────────────────────────────────────────────────────

def lambda_handler(event, context):
    print(f"[DEBUG] ========================================")
    print(f"[DEBUG] LAMBDA INVOCATION STARTED")
    print(f"[DEBUG] ========================================")
    print(f"[DEBUG] Event: {json.dumps(event)}")
    print(f"[DEBUG] Lambda Memory: {context.memory_limit_in_mb} MB")
    print(f"[DEBUG] Lambda Timeout: {context.get_remaining_time_in_millis() / 1000} seconds remaining")
    
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
        
        if msg_type == "text":
            user_message = msg["text"]["body"]
            print(f"[INFO] 📨 User message: {user_message}")
            
            # Route to appropriate agent using LangGraph AI
            print(f"[DEBUG] Starting agent routing...")
            agent = route_message(user_message, from_number)
            print(f"[INFO] 🎯 SELECTED AGENT: {agent.upper()}")
            
            print(f"[DEBUG] Executing {agent} agent handler...")
            if agent == "greeting":
                reply = handle_greeting()
            elif agent == "crop":
                reply = handle_crop_query(user_message)
            elif agent == "market":
                reply = handle_market_query(user_message)
            elif agent == "finance":
                reply = handle_finance_query(user_message, from_number)
            else:
                reply = handle_general_query(user_message)
            
            print(f"[DEBUG] Agent execution complete, reply length: {len(reply)} chars")
            
            # Save conversation with response
            save_conversation(from_number, user_message, reply, agent)
            
            send_whatsapp_message(from_number, reply)
            print(f"[INFO] ✅ Request completed successfully")
            
        elif msg_type == "image":
            print(f"[DEBUG] ===== IMAGE ANALYSIS =====")
            media_id = msg["image"]["id"]
            print(f"[DEBUG] Image media ID: {media_id}")
            
            send_whatsapp_message(from_number, "🔍 Analyzing your crop image, please wait...")
            
            print(f"[DEBUG] Downloading image from WhatsApp...")
            image_bytes = download_whatsapp_image(media_id)
            print(f"[DEBUG] Image downloaded, size: {len(image_bytes)} bytes")
            
            print(f"[DEBUG] Analyzing image with Kindwise API...")
            result = analyze_crop_image(image_bytes)
            print(f"[DEBUG] Image analysis complete")
            
            print(f"[DEBUG] Formatting crop analysis result...")
            reply = format_crop_result(result)
            
            send_whatsapp_message(from_number, reply)
            print(f"[INFO] ✅ Image analysis completed successfully")
            
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
