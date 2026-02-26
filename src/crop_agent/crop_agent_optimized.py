"""
Optimized Crop Agent with improved error handling, caching, and code quality
"""
import json
import urllib3
import os
import boto3
import base64
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import time

# Initialize clients once (reuse across invocations)
http = urllib3.PoolManager(
    timeout=urllib3.Timeout(connect=5.0, read=10.0),
    maxsize=10,
    retries=urllib3.Retry(total=3, backoff_factor=0.3)
)

# Lazy initialization for AWS clients
_bedrock_client = None
_dynamodb_resource = None
_s3_client = None

def get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client("bedrock-runtime", region_name="ap-south-1")
    return _bedrock_client

def get_dynamodb_resource():
    global _dynamodb_resource
    if _dynamodb_resource is None:
        _dynamodb_resource = boto3.resource("dynamodb", region_name="ap-south-1")
    return _dynamodb_resource

def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3", region_name="ap-south-1")
    return _s3_client

# Configuration
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mySecret_123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1049535664900621")
CROP_HEALTH_API_KEY = os.environ.get("CROP_HEALTH_API_KEY")
CONVERSATION_TABLE = os.environ.get("CONVERSATION_TABLE", "kisaanmitra-conversations")
S3_BUCKET = os.environ.get("S3_BUCKET", "kisaanmitra-images")

# System prompt
CROP_SYSTEM_PROMPT = """You are a Crop Health Expert for Indian farmers. Your expertise:
- Crop disease diagnosis and treatment
- Fertilizer and pesticide recommendations
- Soil health and weather-based advice
- Season-specific best practices
- Local farming techniques

Respond in Hindi (Devanagari script). Keep answers practical, concise, and actionable.
Focus on solutions farmers can implement immediately."""

# Language messages
MESSAGES = {
    "hi": {
        "analyzing": "🔍 आपकी फसल की तस्वीर का विश्लेषण कर रहे हैं, कृपया प्रतीक्षा करें...",
        "no_disease": "मैंने आपकी फसल की तस्वीर का विश्लेषण किया लेकिन कोई विशिष्ट बीमारी नहीं मिली। कृपया स्पष्ट तस्वीर के साथ पुनः प्रयास करें।",
        "unsupported": "कृपया टेक्स्ट संदेश या फसल की तस्वीर भेजें।",
        "error": "क्षमा करें, कुछ गलत हो गया। कृपया पुनः प्रयास करें।"
    },
    "en": {
        "analyzing": "🔍 Analyzing your crop image, please wait...",
        "no_disease": "I analyzed your crop image but could not detect any specific disease. Please try with a clearer image.",
        "unsupported": "Please send a text message or crop image.",
        "error": "Sorry, something went wrong. Please try again."
    }
}


def get_conversation_history(user_id: str, limit: int = 3) -> List[Dict]:
    """Retrieve conversation history from DynamoDB with error handling"""
    try:
        table = get_dynamodb_resource().Table(CONVERSATION_TABLE)
        response = table.query(
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
            ScanIndexForward=False,
            Limit=limit
        )
        messages = response.get("Items", [])
        return sorted(messages, key=lambda x: x.get("timestamp", ""))
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []


def save_conversation(user_id: str, role: str, message: str) -> bool:
    """Save conversation to DynamoDB with proper timestamp"""
    try:
        table = get_dynamodb_resource().Table(CONVERSATION_TABLE)
        table.put_item(
            Item={
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "message": message[:1000]  # Limit message size
            }
        )
        return True
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return False


def ask_bedrock_with_context(prompt: str, user_id: Optional[str] = None, language: str = "hi") -> str:
    """Query Bedrock with system prompt and conversation history"""
    try:
        messages = []
        
        # Add conversation history if available
        if user_id:
            history = get_conversation_history(user_id, limit=3)
            for msg in history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": [{"text": msg.get("message", "")}]
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": [{"text": prompt}]
        })
        
        # Language-specific system prompt
        system_prompt = CROP_SYSTEM_PROMPT
        if language == "mr":
            system_prompt += "\n\nRespond in Marathi (Devanagari script)."
        
        response = get_bedrock_client().converse(
            modelId="amazon.nova-micro-v1:0",
            messages=messages,
            system=[{"text": system_prompt}],
            inferenceConfig={"maxTokens": 400, "temperature": 0.7}
        )
        
        reply = response["output"]["message"]["content"][0]["text"]
        
        # Save conversation asynchronously (don't block on failure)
        if user_id:
            save_conversation(user_id, "user", prompt)
            save_conversation(user_id, "assistant", reply)
        
        return reply
    except Exception as e:
        print(f"Bedrock error: {e}")
        return MESSAGES[language]["error"]


def download_whatsapp_image(media_id: str) -> Optional[bytes]:
    """Download image from WhatsApp with retry logic"""
    try:
        # Get media URL
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        
        response = http.request("GET", url, headers=headers)
        if response.status != 200:
            print(f"Failed to get media URL: {response.status}")
            return None
        
        media_info = json.loads(response.data)
        media_url = media_info.get("url")
        
        if not media_url:
            print("No media URL in response")
            return None
        
        # Download image
        response = http.request("GET", media_url, headers=headers)
        if response.status != 200:
            print(f"Failed to download image: {response.status}")
            return None
        
        return response.data
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


def analyze_crop_image(image_bytes: bytes, latitude: Optional[float] = None, 
                      longitude: Optional[float] = None) -> Optional[Dict]:
    """Analyze crop image using Kindwise API with error handling"""
    try:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        payload = {
            "images": [image_base64],
            "similar_images": True
        }
        
        if latitude and longitude:
            payload["latitude"] = latitude
            payload["longitude"] = longitude
        
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
        
        if response.status != 201:
            print(f"Crop API error: {response.status}")
            return None
        
        result = json.loads(response.data)
        return result
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None


def store_image_s3(image_bytes: bytes, user_id: str, media_id: str) -> bool:
    """Store image in S3 for future reference"""
    try:
        key = f"{user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{media_id}.jpg"
        get_s3_client().put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=image_bytes,
            ContentType="image/jpeg"
        )
        return True
    except Exception as e:
        print(f"Error storing image: {e}")
        return False


def format_crop_result(result: Dict, language: str = "hi") -> str:
    """Format crop health result with language support"""
    suggestions = result.get("result", {}).get("disease", {}).get("suggestions", [])
    
    if not suggestions:
        suggestions = result.get("suggestions", [])
    
    if not suggestions:
        return MESSAGES[language]["no_disease"]
    
    if language == "hi":
        message = "*🌾 फसल रोग विश्लेषण*\n\n"
        for i, suggestion in enumerate(suggestions[:3], 1):
            name = suggestion.get("name", "Unknown")
            probability = suggestion.get("probability", 0)
            message += f"{i}. *{name}*\n"
            message += f"   विश्वास: {probability:.1%}\n\n"
        message += "💡 सर्वोत्तम परिणामों के लिए स्थानीय कृषि विशेषज्ञ से परामर्श लें।"
    else:
        message = "*🌾 Crop Disease Analysis*\n\n"
        for i, suggestion in enumerate(suggestions[:3], 1):
            name = suggestion.get("name", "Unknown")
            probability = suggestion.get("probability", 0)
            message += f"{i}. *{name}*\n"
            message += f"   Confidence: {probability:.1%}\n\n"
        message += "💡 For best results, consult a local agricultural expert."
    
    return message


def send_whatsapp_message(to: str, message: str) -> bool:
    """Send WhatsApp message with error handling"""
    try:
        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": message[:4096]}  # WhatsApp limit
        }
        response = http.request(
            "POST",
            url,
            body=json.dumps(data),
            headers=headers
        )
        return response.status == 200
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False


def detect_language(text: str) -> str:
    """Detect language from text"""
    if any('\u0900' <= char <= '\u097F' for char in text):
        return "hi"
    return "en"


def lambda_handler(event, context):
    """Optimized Lambda handler with better error handling"""
    print(f"Event: {json.dumps(event)}")
    start_time = time.time()
    
    # Webhook verification
    if event.get("queryStringParameters"):
        params = event["queryStringParameters"]
        if params.get("hub.verify_token") == VERIFY_TOKEN:
            return {
                'statusCode': 200,
                'body': params.get("hub.challenge", "")
            }
    
    try:
        body = json.loads(event.get("body", "{}"))
        
        # Extract message details
        msg = body["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        msg_type = msg.get("type")
        
        print(f"Message from {from_number}, type: {msg_type}")
        
        if msg_type == "text":
            user_message = msg["text"]["body"]
            language = detect_language(user_message)
            
            reply = ask_bedrock_with_context(user_message, user_id=from_number, language=language)
            send_whatsapp_message(from_number, reply)
        
        elif msg_type == "image":
            media_id = msg["image"]["id"]
            caption = msg["image"].get("caption", "")
            language = detect_language(caption) if caption else "hi"
            
            # Send analyzing message
            send_whatsapp_message(from_number, MESSAGES[language]["analyzing"])
            
            # Download and analyze image
            image_bytes = download_whatsapp_image(media_id)
            if not image_bytes:
                send_whatsapp_message(from_number, MESSAGES[language]["error"])
                return {'statusCode': 200, 'body': 'ok'}
            
            # Store image in S3 (async, don't block)
            store_image_s3(image_bytes, from_number, media_id)
            
            # Analyze image
            result = analyze_crop_image(image_bytes, latitude=18.5204, longitude=73.8567)
            if not result:
                send_whatsapp_message(from_number, MESSAGES[language]["error"])
                return {'statusCode': 200, 'body': 'ok'}
            
            # Format and send result
            reply = format_crop_result(result, language=language)
            send_whatsapp_message(from_number, reply)
        
        else:
            language = "hi"
            send_whatsapp_message(from_number, MESSAGES[language]["unsupported"])
        
        # Log execution time
        execution_time = time.time() - start_time
        print(f"Execution time: {execution_time:.2f}s")
        
        return {'statusCode': 200, 'body': 'ok'}
    
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {'statusCode': 200, 'body': 'ok'}  # Always return 200 to WhatsApp
