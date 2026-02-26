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


def ask_bedrock(prompt):
    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={"maxTokens": 300}
    )
    return response["output"]["message"]["content"][0]["text"]

# Crop Health API

def download_whatsapp_image(media_id):
    
    # Step 1: Get media URL
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    
    response = http.request("GET", url, headers=headers)
    media_info = json.loads(response.data)
    media_url = media_info.get("url")
    
    if not media_url:
        raise Exception("Could not get media URL")
    
    response = http.request("GET", media_url, headers=headers)
    return response.data  # Raw image bytes

def analyze_crop_image(image_bytes, latitude=None, longitude=None):
    
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
    print("Crop API result:", json.dumps(result, indent=2))
    return result

def format_crop_result(result):
    """Format the crop health result into a readable WhatsApp message"""
    
    suggestions = result.get("result", {}).get("disease", {}).get("suggestions", [])
    
    if not suggestions:
        suggestions = result.get("suggestions", [])
    
    if not suggestions:
        return "I analyzed your crop image but could not detect any specific disease. Please try with a clearer image."
    
    message = "*Crop Disease Analysis Results*\n\n"
    
    for i, suggestion in enumerate(suggestions[:3], 1):
        name = suggestion.get("name", "Unknown")
        probability = suggestion.get("probability", 0)
        message += f"{i}. *{name}*\n"
        message += f"   Confidence: {probability:.1%}\n\n"
    
    message += "💡 For best results, consult a local agricultural expert."
    return message

# WhatsApp

def send_whatsapp_message(to, message):
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

# Lambda Handler

def lambda_handler(event, context):
    print("Event received:", event)

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

        print(f"Message type: {msg_type}")

        if msg_type == "text":
            user_message = msg["text"]["body"]
            print("User message:", user_message)
            reply = ask_bedrock(user_message)
            print("Bedrock reply:", reply)
            send_whatsapp_message(from_number, reply)

        elif msg_type == "image":
            media_id = msg["image"]["id"]
            print("Image media ID:", media_id)

            send_whatsapp_message(from_number, "🔍 Analyzing your crop image, please wait...")

            image_bytes = download_whatsapp_image(media_id)
            result = analyze_crop_image(
                image_bytes,
                latitude=18.5204, #we have to Make this dynamic later
                longitude=73.8567
            )
            reply = format_crop_result(result)
            send_whatsapp_message(from_number, reply)

        else:
            send_whatsapp_message(from_number, "Please send a text message or a crop image for disease detection.")

    except Exception as e:
        print("Error:", e)

    return {
        'statusCode': 200,
        'body': 'ok'
    }