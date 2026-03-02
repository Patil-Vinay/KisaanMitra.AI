"""
WhatsApp Service - Handles WhatsApp API interactions
"""
import json
import urllib3
import os

http = urllib3.PoolManager()

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")


class WhatsAppService:
    """Manages WhatsApp message sending and media downloads"""
    
    @staticmethod
    def send_message(to, message=None, interactive_payload=None):
        """Send WhatsApp message (text or interactive)"""
        print(f"[WHATSAPP] Sending message to: {to}")
        
        url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        if interactive_payload:
            print(f"[WHATSAPP] Sending interactive message")
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                **interactive_payload
            }
        else:
            print(f"[WHATSAPP] Sending text message, length: {len(message)} chars")
            data = {
                "messaging_product": "whatsapp",
                "to": to,
                "text": {"body": message}
            }
        
        response = http.request("POST", url, body=json.dumps(data), headers=headers)
        print(f"[WHATSAPP] API response: {response.status}")
        if response.status != 200:
            print(f"[ERROR] WhatsApp API error: {response.data}")
        
        return response.status == 200
    
    @staticmethod
    def download_image(media_id):
        """Download image from WhatsApp"""
        print(f"[WHATSAPP] Downloading image: {media_id}")
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        
        response = http.request("GET", url, headers=headers)
        media_info = json.loads(response.data)
        media_url = media_info.get("url")
        
        if not media_url:
            raise Exception("Could not get media URL")
        
        response = http.request("GET", media_url, headers=headers)
        print(f"[WHATSAPP] Image downloaded, size: {len(response.data)} bytes")
        return response.data
