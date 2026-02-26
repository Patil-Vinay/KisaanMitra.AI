import json
import urllib3
import os
import boto3
import base64

http = urllib3.PoolManager()

VERIFY_TOKEN = "mySecret_123"
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = "1049535664900621"
CROP_HEALTH_API_KEY = os.environ.get("CROP_HEALTH_API_KEY")

bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")

# Conversation memory table
CONVERSATION_TABLE = os.environ.get("CONVERSATION_TABLE", "kisaanmitra-conversations")

# Enhanced system prompt with agricultural context
CROP_SYSTEM_PROMPT = """You are a Crop Health Expert for Indian farmers. Your expertise:
- Crop disease diagnosis and treatment
- Fertilizer and pesticide recommendations
- Soil health and weather-based advice
- Season-specific best practices
- Local farming techniques

Respond in Hindi (Devanagari script). Keep answers practical, concise, and actionable.
Focus on solutions farmers can implement immediately."""


def get_conversation_history(user_id, limit=5):
    """Retrieve conversation history from DynamoDB"""
    
    try:
        table = dynamodb.Table(CONVERSATION_TABLE)
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


def save_conversation(user_id, role, message):
    """Save conversation to DynamoDB"""
    
    try:
        table = dynamodb.Table(CONVERSATION_TABLE)
        table.put_item(
            Item={
                "user_id": user_id,
                "timestamp": str(int(boto3.client('sts').get_caller_identity()['Account'])),
                "role": role,
                "message": message
            }
        )
    except Exception as e:
        print(f"Error saving conversation: {e}")


def ask_bedrock_with_context(prompt, user_id=None, language="hi"):
    """Query Bedrock with system prompt and conversation history"""
    
    messages = []
    
    # Add conversation history if available
    if user_id:
        history = get_conversation_history(user_id)
        for msg in history[-3:]:  # Last 3 messages for context
            messages.append({
                "role": msg["role"],
                "content": [{"text": msg["message"]}]
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
    
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=messages,
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": 400, "temperature": 0.7}
    )
    
    reply = response["output"]["message"]["content"][0]["text"]
    
    # Save conversation
    if user_id:
        save_conversation(user_id, "user", prompt)
        save_conversation(user_id, "assistant", reply)
    
    return reply


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


def analyze_crop_image(image_bytes, latitude=None, longitude=None):
    """Analyze crop image using Kindwise API"""
    
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
    
    print("Crop API status:", response.status)
    result = json.loads(response.data)
    return result


def format_crop_result(result, language="hi"):
    """Format crop health result with language support"""
    
    suggestions = result.get("result", {}).get("disease", {}).get("suggestions", [])
    
    if not suggestions:
        suggestions = result.get("suggestions", [])
    
    if not suggestions:
        return "मैंने आपकी फसल की तस्वीर का विश्लेषण किया लेकिन कोई विशिष्ट बीमारी नहीं मिली। कृपया स्पष्ट तस्वीर के साथ पुनः प्रयास करें।" if language == "hi" else "I analyzed your crop image but could not detect any specific disease."
    
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
    response = http.request(
        "POST",
        url,
        body=json.dumps(data),
        headers=headers
    )
    print("WhatsApp API response:", response.data)


def detect_language(text):
    """Simple language detection"""
    
    # Check for Devanagari script
    if any('\u0900' <= char <= '\u097F' for char in text):
        return "hi"
    return "en"


def extract_location_from_message(text):
    """Extract location coordinates if mentioned"""
    
    # Placeholder - in production, use NER or geocoding
    # For now, return None to use default
    return None


def lambda_handler(event, context):
    """Enhanced Lambda handler with conversation memory and language support"""
    
    print("Event received:", event)

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
            language = detect_language(user_message)
            
            print(f"User message ({language}):", user_message)
            
            reply = ask_bedrock_with_context(user_message, user_id=from_number, language=language)
            print("Bedrock reply:", reply)
            
            send_whatsapp_message(from_number, reply)

        elif msg_type == "image":
            media_id = msg["image"]["id"]
            caption = msg["image"].get("caption", "")
            
            print("Image media ID:", media_id)
            
            # Check if caption has location info
            location = extract_location_from_message(caption) if caption else None
            
            send_whatsapp_message(from_number, "🔍 आपकी फसल की तस्वीर का विश्लेषण कर रहे हैं, कृपया प्रतीक्षा करें...")

            image_bytes = download_whatsapp_image(media_id)
            
            # Use location from caption or default to Pune
            lat = location[0] if location else 18.5204
            lng = location[1] if location else 73.8567
            
            result = analyze_crop_image(image_bytes, latitude=lat, longitude=lng)
            
            language = detect_language(caption) if caption else "hi"
            reply = format_crop_result(result, language=language)
            
            send_whatsapp_message(from_number, reply)

        else:
            send_whatsapp_message(from_number, "कृपया टेक्स्ट संदेश या फसल की तस्वीर भेजें।")

    except Exception as e:
        print("Error:", e)

    return {
        'statusCode': 200,
        'body': 'ok'
    }
