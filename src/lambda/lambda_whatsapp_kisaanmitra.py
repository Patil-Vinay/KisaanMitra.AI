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

# Conversation memory cache (in-memory for Lambda)
conversation_memory = {}

# ─── Conversation Memory ────────────────────────────────────────────────────

def get_conversation_history(user_id, limit=5):
    """Get recent conversation history from DynamoDB"""
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
    """Build context string from conversation history"""
    if not history:
        return ""
    
    context = "Previous conversation:\n"
    for item in reversed(history[-3:]):  # Last 3 messages
        context += f"User: {item.get('message', '')}\n"
        context += f"Bot: {item.get('response', '')[:100]}...\n"
    context += "\nCurrent conversation:\n"
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

def extract_crop_with_ai(user_message, bedrock_client):
    """Use AI to extract crop name from user message"""
    prompt = f"""Extract the crop name from this farmer's message. Reply with ONLY the crop name in lowercase, nothing else.

Examples:
"I want to grow soybean" → soybean
"give me onion budget" → onion
"chilly farming cost" → chilly
"mushroom cultivation" → mushroom
"tomato price" → tomato

User message: "{user_message}"

Reply with ONLY the crop name:"""
    
    try:
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 50, "temperature": 0.3}
        )
        crop_name = response["output"]["message"]["content"][0]["text"].strip().lower()
        print(f"AI extracted crop: {crop_name}")
        return crop_name
    except Exception as e:
        print(f"Crop extraction error: {e}")
        return None


def generate_crop_budget_with_ai(crop_name, land_size, location, bedrock_client):
    """Generate realistic crop budget using AI for ANY crop"""
    prompt = f"""You are an agricultural finance expert in India. Generate a realistic budget breakdown for {crop_name} cultivation.

Location: {location}
Land Size: {land_size} acre(s)

Provide a detailed budget with these exact categories (use realistic Indian market prices):
1. Seeds/Planting Material cost
2. Fertilizer cost
3. Pesticides cost
4. Irrigation cost
5. Labor cost
6. Machinery/Equipment cost
7. Expected yield (in quintal or kg)
8. Expected market price per unit
9. Expected revenue
10. Expected profit

Format your response EXACTLY like this (use ₹ symbol):
Seeds: ₹X
Fertilizer: ₹X
Pesticides: ₹X
Irrigation: ₹X
Labor: ₹X
Machinery: ₹X
Total Cost: ₹X
Yield: X quintal
Price: ₹X/quintal
Revenue: ₹X
Profit: ₹X

Be realistic based on current Indian agricultural costs. Consider {location} region specifics."""
    
    try:
        response = bedrock_client.converse(
            modelId="us.amazon.nova-pro-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1000, "temperature": 0.5}
        )
        budget_text = response["output"]["message"]["content"][0]["text"].strip()
        print(f"AI generated budget for {crop_name}")
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
    """Handle finance-related queries with AI-powered crop detection and budget generation"""
    system_prompt = """You are a finance advisor for farmers in India.
Help with budgets, loans, and government schemes.
Reply in simple English. Keep it short (2-3 sentences) and clear.
IMPORTANT: Always use ₹ (Rupee symbol) for Indian currency, never use $."""
    
    # Get conversation history for context
    history = get_conversation_history(user_id)
    context = build_context_from_history(history)
    
    message_lower = user_message.lower()
    
    # Check for budget request
    if any(word in message_lower for word in ["budget", "cost", "expense", "finance", "model", "planting", "structure", "grow", "cultivation"]):
        
        # Extract crop using AI (works for ANY crop)
        crop_name = extract_crop_with_ai(user_message, bedrock)
        
        if not crop_name:
            return "Please specify which crop you want to grow. For example: 'I want to grow tomato' or 'give me chilly budget'"
        
        # Extract land size
        land_size = 1
        import re
        size_match = re.search(r'(\d+)\s*(acre|एकड़)', message_lower)
        if size_match:
            land_size = int(size_match.group(1))
        
        # Extract location
        location = "Maharashtra"
        location_match = re.search(r'in\s+(\w+)', message_lower, re.IGNORECASE)
        if location_match:
            location = location_match.group(1)
        
        # Generate budget using AI (works for ANY crop)
        budget = generate_crop_budget_with_ai(crop_name, land_size, location, bedrock)
        
        if not budget:
            return f"I'm having trouble generating a budget for {crop_name}. Please try again or ask about a different crop."
        
        # Format response
        message = f"💰 *{budget['crop'].title()} Budget Plan*\n"
        message += f"*Land*: {budget['land_size']} acre\n"
        message += f"*Location*: {location}\n\n"
        message += "*📊 Cost Breakdown*\n"
        message += f"Seeds: ₹{budget['seeds']:,}\n"
        message += f"Fertilizer: ₹{budget['fertilizer']:,}\n"
        message += f"Pesticides: ₹{budget['pesticides']:,}\n"
        message += f"Irrigation: ₹{budget['irrigation']:,}\n"
        message += f"Labor: ₹{budget['labor']:,}\n"
        message += f"Machinery: ₹{budget['machinery']:,}\n"
        message += f"*Total Cost*: ₹{budget['total_cost']:,}\n\n"
        message += "*💵 Expected Returns*\n"
        message += f"Yield: {budget['expected_yield']} quintal\n"
        message += f"Price: ₹{budget['expected_price']}/quintal\n"
        message += f"Revenue: ₹{budget['expected_revenue']:,}\n"
        message += f"*Profit*: ₹{budget['expected_profit']:,}\n\n"
        message += "💡 Note: Prices may vary by region and season\n"
        message += "Need loan or scheme info? Just ask!"
        return message
    
    # Check for schemes
    elif any(word in message_lower for word in ["scheme", "subsidy", "government"]):
        schemes = match_government_schemes("wheat", 1)
        
        message = "🎁 *Government Schemes*\n\n"
        for i, scheme in enumerate(schemes[:4], 1):
            message += f"{i}. *{scheme['name']}*\n"
            message += f"   Benefit: {scheme['benefit']}\n"
            message += f"   Eligibility: {scheme['eligibility']}\n\n"
        message += "💡 Visit nearest agriculture office for more details"
        return message
    
    # Check for loan
    elif any(word in message_lower for word in ["loan", "credit", "borrow"]):
        loan = calculate_loan_eligibility(20000, 50000)
        
        message = "🏦 *Loan Eligibility*\n\n"
        message += f"Max Loan: ₹{loan['max_loan']:,}\n"
        message += f"Interest Rate: {loan['interest_rate']}%\n"
        message += f"Monthly EMI: ₹{loan['monthly_emi']:,}\n"
        message += f"Total Repayment: ₹{loan['total_repayment']:,}\n\n"
        message += "💡 Apply for Kisan Credit Card at your bank"
        return message
    
    # Fallback to AI with context
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
        msg = body["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        msg_type = msg.get("type")
        
        print(f"Message from {from_number}, type: {msg_type}")
        
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
