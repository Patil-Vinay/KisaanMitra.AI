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

# Import onboarding and knowledge graph
import sys
sys.path.append('/opt/python')  # Lambda layer path
try:
    from onboarding.farmer_onboarding import onboarding_manager
    from knowledge_graph.village_graph import knowledge_graph
    ONBOARDING_AVAILABLE = True
except ImportError:
    print("Onboarding module not available")
    ONBOARDING_AVAILABLE = False

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

# Conversation memory cache (in-memory for Lambda)
conversation_memory = {}

# ─── Conversation Memory ────────────────────────────────────────────────────

def get_conversation_history(user_id, limit=10):
    """Get recent conversation history from DynamoDB with enhanced context"""
    try:
        response = conversation_table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
            ScanIndexForward=False,
            Limit=limit
        )
        return response.get("Items", [])
    except Exception as e:
        print(f"Error fetching conversation history: {e}")
        return []

def save_conversation(user_id, message, response, agent_type):
    """Save conversation to DynamoDB"""
    try:
        conversation_table.put_item(Item={
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "response": response,
            "agent": agent_type
        })
    except Exception as e:
        print(f"Error saving conversation: {e}")

def build_context_from_history(history):
    """Build enhanced context string from conversation history"""
    if not history:
        return ""
    
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
    return context

# ─── Bedrock with Cross-Region Inference ────────────────────────────────────

def ask_bedrock(prompt, system_prompt=None, conversation_context=""):
    """Call Bedrock using cross-region inference profile with context"""
    try:
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
        
        response = bedrock.converse(**kwargs)
        return response["output"]["message"]["content"][0]["text"]
    except Exception as e:
        print(f"Bedrock error: {e}")
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
    
    if LANGGRAPH_AVAILABLE:
        try:
            # Use AI-powered routing with LangGraph
            agent = route_message_with_ai(user_message, user_id, bedrock)
            print(f"LangGraph AI routing: {agent}")
            return agent
        except Exception as e:
            print(f"LangGraph routing failed: {e}, using fallback")
    
    # Fallback to keyword-based routing
    return fallback_keyword_routing(user_message)


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
    greetings = [
        "Hello! I'm Kisaan Mitra, your farming assistant. How can I help you today?",
        "Hi there! I'm here to help with your farming questions. What's on your mind?",
        "Hey! I'm Kisaan Mitra. I can help with crop problems, market prices, or farming advice. What do you need?",
    ]
    import random
    return random.choice(greetings)

def handle_crop_query(user_message):
    """Handle crop-related text queries"""
    system_prompt = """You are a helpful farming assistant. 
Help farmers with crop diseases, pests, and treatments.
Reply in simple English. Keep it short (2-3 sentences) and practical."""
    
    return ask_bedrock(user_message, system_prompt)

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
    """Handle market-related queries with FAST static data"""
    system_prompt = """You are a market expert helping farmers.
Provide market prices and trends in simple English.
Keep it short (2-3 sentences) and practical."""
    
    # Extract crop name
    common_crops = ["wheat", "rice", "cotton", "soybean", "onion", "potato", "tomato", "sugarcane"]
    detected_crop = None
    message_lower = user_message.lower()
    
    for crop in common_crops:
        if crop in message_lower:
            detected_crop = crop
            break
    
    if detected_crop and FAST_MARKET_DATA_AVAILABLE:
        # Use FAST static market data (instant response)
        market_data = get_fast_market_prices(detected_crop)
        
        if market_data:
            return format_market_response_fast(detected_crop, market_data)
    
    # Fallback to AI for general market questions
    return ask_bedrock(user_message, system_prompt)

def extract_crop_with_ai(user_message, bedrock_client, conversation_history=""):
    """Use AI to extract crop name from user message with conversation context"""
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
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",  # Using Pro for better accuracy
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 50, "temperature": 0.2}  # Lower temp for precision
        )
        crop_name = response["output"]["message"]["content"][0]["text"].strip().lower()
        print(f"AI extracted crop: {crop_name}")
        return crop_name if crop_name != "unknown" else None
    except Exception as e:
        print(f"Crop extraction error: {e}")
        return None


def generate_crop_budget_with_ai(crop_name, land_size, location, bedrock_client):
    """Generate highly accurate crop budget using advanced AI with Indian agricultural expertise"""
    prompt = f"""You are an expert agricultural economist specializing in Indian farming. Generate a comprehensive, realistic budget for {crop_name} cultivation in India.

**Farm Details:**
- Crop: {crop_name}
- Location: {location}
- Land Size: {land_size} acre(s)

**Instructions:**
1. Provide realistic costs based on current Indian agricultural market rates for {location} region
2. Consider regional variations in costs and yields
3. Include all major cost categories
4. Provide realistic yield expectations for {crop_name} in {location}
5. Use current market prices for {crop_name}
6. Calculate accurate profit margins

**Required Format (use exact labels):**
Seeds: ₹[amount]
Fertilizer: ₹[amount]
Pesticides: ₹[amount]
Irrigation: ₹[amount]
Labor: ₹[amount]
Machinery: ₹[amount]
Total Cost: ₹[sum of all above]
Yield: [number] quintal
Price: ₹[amount]/quintal
Revenue: ₹[yield × price]
Profit: ₹[revenue - total cost]

**Important:**
- All amounts in Indian Rupees (₹)
- Be realistic and accurate for {crop_name} in {location}
- Consider seasonal variations
- Account for {land_size} acre(s) of land
- Provide practical, achievable numbers

Generate the budget now:"""
    
    try:
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",  # Pro model for superior accuracy
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 2000, "temperature": 0.4}  # Higher tokens for detailed response
        )
        budget_text = response["output"]["message"]["content"][0]["text"].strip()
        print(f"AI generated detailed budget for {crop_name} in {location}")
        return parse_ai_budget(budget_text, crop_name, land_size)
    except Exception as e:
        print(f"Budget generation error: {e}")
        return None


def parse_ai_budget(budget_text, crop_name, land_size):
    """Parse AI-generated budget text into structured format"""
    import re
    
    budget = {
        "crop": crop_name,
        "land_size": land_size,
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
        "expected_profit": 0
    }
    
    # Extract numbers from budget text
    patterns = {
        "seeds": r"Seeds?[:\s]+₹?([\d,]+)",
        "fertilizer": r"Fertilizer[:\s]+₹?([\d,]+)",
        "pesticides": r"Pesticides?[:\s]+₹?([\d,]+)",
        "irrigation": r"Irrigation[:\s]+₹?([\d,]+)",
        "labor": r"Labor[:\s]+₹?([\d,]+)",
        "machinery": r"Machinery[:\s]+₹?([\d,]+)",
        "total_cost": r"Total Cost[:\s]+₹?([\d,]+)",
        "expected_yield": r"Yield[:\s]+([\d,]+)",
        "expected_price": r"Price[:\s]+₹?([\d,]+)",
        "expected_revenue": r"Revenue[:\s]+₹?([\d,]+)",
        "expected_profit": r"Profit[:\s]+₹?([\d,]+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, budget_text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(",", "")
            budget[key] = int(value)
    
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
    system_prompt = """You are an expert agricultural finance advisor for Indian farmers.
Provide accurate, practical financial advice for farming operations.
Reply in simple, clear English. Be specific and actionable.
IMPORTANT: Always use ₹ (Rupee symbol) for Indian currency, never use $."""
    
    # Get enhanced conversation history
    history = get_conversation_history(user_id, limit=10)
    context = build_context_from_history(history)
    
    message_lower = user_message.lower()
    
    # Check for budget request
    if any(word in message_lower for word in ["budget", "cost", "expense", "finance", "model", "planting", "structure", "grow", "cultivation"]):
        
        # Extract crop using AI with conversation context
        crop_name = extract_crop_with_ai(user_message, bedrock, context)
        
        if not crop_name:
            return "Please specify which crop you want to grow. For example: 'I want to grow tomato' or 'give me chilly budget'"
        
        # Extract land size
        land_size = 1
        import re
        size_match = re.search(r'(\d+)\s*(acre|एकड़|hectare)', message_lower)
        if size_match:
            land_size = int(size_match.group(1))
        
        # Extract location with better detection
        location = "Maharashtra"
        location_patterns = [
            r'in\s+(\w+)',
            r'from\s+(\w+)',
            r'at\s+(\w+)',
            r'(\w+)\s+region',
            r'(\w+)\s+area'
        ]
        for pattern in location_patterns:
            location_match = re.search(pattern, message_lower, re.IGNORECASE)
            if location_match:
                location = location_match.group(1).title()
                break
        
        print(f"Generating budget for {crop_name}, {land_size} acre(s) in {location}")
        
        # Generate budget using enhanced AI
        budget = generate_crop_budget_with_ai(crop_name, land_size, location, bedrock)
        
        if not budget:
            return f"I'm having trouble generating a budget for {crop_name}. Please try again or ask about a different crop."
        
        # Format enhanced response
        message = f"💰 *{budget['crop'].title()} Budget Plan*\n"
        message += f"📍 *Location*: {location}\n"
        message += f"🌾 *Land*: {budget['land_size']} acre\n\n"
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
        message += f"• Market Price: ₹{budget['expected_price']}/quintal\n"
        message += f"• Revenue: ₹{budget['expected_revenue']:,}\n"
        message += f"*✨ Net Profit*: ₹{budget['expected_profit']:,}\n\n"
        message += f"💡 *ROI*: {int((budget['expected_profit']/budget['total_cost'])*100)}%\n\n"
        message += "� Need loan or scheme info? Just ask!"
        return message
    
    # Check for schemes
    elif any(word in message_lower for word in ["scheme", "subsidy", "government"]):
        schemes = match_government_schemes("wheat", 1)
        
        message = "� *Government Schemes for Farmers*\n\n"
        for i, scheme in enumerate(schemes[:4], 1):
            message += f"{i}. *{scheme['name']}*\n"
            message += f"   💰 Benefit: {scheme['benefit']}\n"
            message += f"   ✅ Eligibility: {scheme['eligibility']}\n\n"
        message += "💡 Visit nearest Krishi Vigyan Kendra for more details"
        return message
    
    # Check for loan
    elif any(word in message_lower for word in ["loan", "credit", "borrow"]):
        loan = calculate_loan_eligibility(20000, 50000)
        
        message = "🏦 *Kisan Credit Card (KCC) Eligibility*\n\n"
        message += f"💰 Max Loan: ₹{loan['max_loan']:,}\n"
        message += f"📊 Interest Rate: {loan['interest_rate']}% per annum\n"
        message += f"💳 Monthly EMI: ₹{loan['monthly_emi']:,}\n"
        message += f"💵 Total Repayment: ₹{loan['total_repayment']:,}\n"
        message += f"📈 Total Interest: ₹{loan['total_interest']:,}\n\n"
        message += "💡 Apply at your nearest bank branch with land documents"
        return message
    
    # Fallback to AI with enhanced context
    return ask_bedrock(user_message, system_prompt, context)

def handle_general_query(user_message):
    """Handle general queries - friendly conversation"""
    system_prompt = """You are Kisaan Mitra, a friendly farming assistant.
Have a natural conversation in simple English.
Be helpful and warm. Keep responses short (2-3 sentences).
If they ask about farming problems, guide them to be specific."""
    
    return ask_bedrock(user_message, system_prompt)

# ─── WhatsApp ─────────────────────────────────────────────────────────────────

def send_whatsapp_message(to, message):
    """Send WhatsApp message"""
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
    print(f"WhatsApp response: {response.status}")


def check_user_status(user_id):
    """
    Check user onboarding status
    Returns: (is_new, onboarding_state, profile)
    """
    if not ONBOARDING_AVAILABLE:
        return False, "completed", None
    
    try:
        # Check if user has completed profile
        is_new = onboarding_manager.is_new_user(user_id)
        
        # Get onboarding state
        state, data = onboarding_manager.get_onboarding_state(user_id)
        
        # Get profile if exists
        profile = None if is_new else onboarding_manager.get_user_profile(user_id)
        
        return is_new, state, profile
        
    except Exception as e:
        print(f"Error checking user status: {e}")
        return True, "new", None  # Default to new user on error

# ─── Lambda Handler ───────────────────────────────────────────────────────────

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    # Webhook verification
    if event.get("queryStringParameters"):
        params = event["queryStringParameters"]
        if params.get("hub.verify_token") == VERIFY_TOKEN:
            return {
                'statusCode': 200,
                'body': params.get("hub.challenge")
            }
    
    try:
        body = json.loads(event["body"])
        value = body["entry"][0]["changes"][0]["value"]
        
        # Check if this is a status update (sent/delivered/read) - ignore these
        if "statuses" in value:
            print("Status update received, ignoring")
            return {'statusCode': 200, 'body': 'ok'}
        
        # Check if messages exist
        if "messages" not in value:
            print("No messages in webhook, ignoring")
            return {'statusCode': 200, 'body': 'ok'}
        
        msg = value["messages"][0]
        from_number = msg["from"]
        msg_type = msg.get("type")
        
        print(f"📱 Message from {from_number}, type: {msg_type}")
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: CHECK USER STATUS (ALWAYS FIRST)
        # ═══════════════════════════════════════════════════════════════
        is_new_user, onboarding_state, user_profile = check_user_status(from_number)
        
        print(f"👤 User Status: is_new={is_new_user}, state={onboarding_state}, has_profile={user_profile is not None}")
        
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
            print(f"User message: {user_message}")
            
            # Route to appropriate agent using LangGraph AI
            agent = route_message(user_message, from_number)
            print(f"Routing to {agent} agent")
            
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
            
            # Save conversation with response
            save_conversation(from_number, user_message, reply, agent)
            
            send_whatsapp_message(from_number, reply)
            
        elif msg_type == "image":
            media_id = msg["image"]["id"]
            print(f"Image media ID: {media_id}")
            
            send_whatsapp_message(from_number, "🔍 Analyzing your crop image, please wait...")
            
            image_bytes = download_whatsapp_image(media_id)
            result = analyze_crop_image(image_bytes)
            reply = format_crop_result(result)
            
            send_whatsapp_message(from_number, reply)
            
        else:
            send_whatsapp_message(from_number, "Please send a text message or crop image for disease detection.")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    return {'statusCode': 200, 'body': 'ok'}
