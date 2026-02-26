import json
import urllib3
import os
import boto3
from datetime import datetime, timedelta

http = urllib3.PoolManager()

# AWS Clients
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")

# Configuration
MARKET_DATA_TABLE = os.environ.get("MARKET_DATA_TABLE", "kisaanmitra-market-data")
AGMARKNET_API = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
AGMARKNET_API_KEY = os.environ.get("AGMARKNET_API_KEY")

SYSTEM_PROMPT = """You are a Market Intelligence Agent for Indian farmers. Your role:
- Analyze market trends and price forecasts
- Recommend optimal harvest timing
- Suggest best crops based on demand
- Provide mandi price information
- Give actionable market insights in Hindi

Keep responses concise, practical, and farmer-friendly. Use simple Hindi."""


def ask_bedrock_market(user_message, context=None):
    """Query Bedrock with market-specific system prompt and context"""
    
    messages = []
    
    # Add context if available
    if context:
        context_text = f"Market Context:\n{json.dumps(context, indent=2, ensure_ascii=False)}\n\nFarmer Query: {user_message}"
        messages.append({
            "role": "user",
            "content": [{"text": context_text}]
        })
    else:
        messages.append({
            "role": "user",
            "content": [{"text": user_message}]
        })
    
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=messages,
        system=[{"text": SYSTEM_PROMPT}],
        inferenceConfig={"maxTokens": 500, "temperature": 0.7}
    )
    
    return response["output"]["message"]["content"][0]["text"]


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
        
        url = f"{AGMARKNET_API}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
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
        table = dynamodb.Table(MARKET_DATA_TABLE)
        response = table.get_item(Key={"crop_name": crop_name.lower()})
        
        if "Item" in response:
            return response["Item"]
        
        return None
    except Exception as e:
        print(f"Error fetching cached data: {e}")
        return None


def cache_market_data(crop_name, data):
    """Cache market data in DynamoDB"""
    
    try:
        table = dynamodb.Table(MARKET_DATA_TABLE)
        table.put_item(
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
    
    # Calculate average prices
    recent_avg = sum([float(p.get("modal_price", 0)) for p in prices[:3]]) / min(3, len(prices))
    older_avg = sum([float(p.get("modal_price", 0)) for p in prices[-3:]]) / min(3, len(prices))
    
    change_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
    
    return {
        "trend": "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable",
        "recent_avg": round(recent_avg, 2),
        "older_avg": round(older_avg, 2),
        "change_percent": round(change_pct, 2)
    }


def get_crop_recommendation(location, season=None):
    """Get crop recommendation based on location and season"""
    
    # Simplified recommendation logic
    # In production, this would use ML models and historical data
    
    if not season:
        month = datetime.now().month
        if month in [6, 7, 8, 9]:
            season = "kharif"
        elif month in [10, 11, 12, 1]:
            season = "rabi"
        else:
            season = "summer"
    
    recommendations = {
        "kharif": ["rice", "cotton", "soybean", "maize", "sugarcane"],
        "rabi": ["wheat", "gram", "mustard", "potato", "onion"],
        "summer": ["watermelon", "cucumber", "bitter_gourd", "okra"]
    }
    
    return recommendations.get(season, [])


def format_market_response(crop_name, market_data, trend_analysis):
    """Format market data into WhatsApp-friendly message"""
    
    message = f"*📊 {crop_name.title()} - Market Analysis*\n\n"
    
    if trend_analysis:
        trend_emoji = "📈" if trend_analysis["trend"] == "increasing" else "📉" if trend_analysis["trend"] == "decreasing" else "➡️"
        message += f"{trend_emoji} *Trend*: {trend_analysis['trend'].title()}\n"
        message += f"💰 *Current Avg*: ₹{trend_analysis['recent_avg']}/quintal\n"
        
        if trend_analysis["trend"] != "insufficient_data":
            message += f"📊 *Change*: {trend_analysis['change_percent']:+.1f}%\n"
    
    if market_data and len(market_data) > 0:
        message += f"\n*🏪 Top Mandis*:\n"
        for i, record in enumerate(market_data[:3], 1):
            mandi = record.get("market", "Unknown")
            price = record.get("modal_price", "N/A")
            message += f"{i}. {mandi}: ₹{price}\n"
    
    message += f"\n💡 *Tip*: Check multiple mandis before selling"
    
    return message


def handle_market_query(user_message, user_location=None):
    """Main handler for market-related queries"""
    
    # Extract crop name from message (simplified)
    # In production, use NER or better NLP
    common_crops = ["wheat", "rice", "cotton", "soybean", "onion", "potato", "tomato", "sugarcane"]
    detected_crop = None
    
    message_lower = user_message.lower()
    for crop in common_crops:
        if crop in message_lower:
            detected_crop = crop
            break
    
    context = {}
    
    # If crop detected, fetch market data
    if detected_crop:
        # Check cache first
        cached_data = get_cached_market_data(detected_crop)
        
        if cached_data:
            market_data = cached_data.get("data")
        else:
            # Fetch fresh data
            market_data = get_mandi_prices(detected_crop)
            if market_data:
                cache_market_data(detected_crop, market_data)
        
        if market_data:
            trend = analyze_price_trend(market_data)
            context["market_data"] = {
                "crop": detected_crop,
                "trend": trend,
                "recent_prices": market_data[:5]
            }
    
    # Get AI response with context
    ai_response = ask_bedrock_market(user_message, context)
    
    return ai_response


def lambda_handler(event, context):
    """Lambda handler for market agent"""
    
    print("Market Agent Event:", event)
    
    try:
        body = json.loads(event.get("body", "{}"))
        
        query_type = body.get("type", "general")
        user_message = body.get("message", "")
        user_location = body.get("location")
        
        if query_type == "price_check":
            crop_name = body.get("crop")
            market_data = get_mandi_prices(crop_name)
            trend = analyze_price_trend(market_data) if market_data else None
            response = format_market_response(crop_name, market_data, trend)
        
        elif query_type == "crop_recommendation":
            season = body.get("season")
            crops = get_crop_recommendation(user_location, season)
            response = f"*🌾 Recommended Crops*:\n" + "\n".join([f"• {c.title()}" for c in crops])
        
        else:
            response = handle_market_query(user_message, user_location)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "response": response
            })
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }
