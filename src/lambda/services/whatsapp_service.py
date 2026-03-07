"""
WhatsApp Service - Handles WhatsApp API interactions
"""
import json
import urllib3
import os
import time
from urllib3.exceptions import MaxRetryError, TimeoutError

# Create a connection pool with proper configuration
http = urllib3.PoolManager(
    num_pools=10,
    maxsize=10,
    retries=urllib3.Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
    ),
    timeout=urllib3.Timeout(connect=5.0, read=10.0)
)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# Validate required environment variables
if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
    print("[ERROR] Missing required WhatsApp environment variables")


class WhatsAppService:
    """Manages WhatsApp message sending and media downloads"""
    
    @staticmethod
    def send_message(to, message=None, interactive_payload=None, max_retries=3):
        """Send WhatsApp message (text or interactive) with retry logic"""
        if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
            print("[ERROR] WhatsApp credentials not configured")
            return False
            
        if not to:
            print("[ERROR] No recipient specified")
            return False
            
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
            if not message:
                print("[ERROR] No message content provided")
                return False
            print(f"[WHATSAPP] Sending text message, length: {len(message)} chars")
            data = {
                "messaging_product": "whatsapp",
                "to": to,
                "text": {"body": message}
            }
        
        for attempt in range(max_retries):
            try:
                response = http.request("POST", url, body=json.dumps(data), headers=headers)
                print(f"[WHATSAPP] API response: {response.status}")
                
                if response.status == 200:
                    return True
                elif response.status == 429:  # Rate limited
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 1  # 1, 2, 4 seconds
                        print(f"[WHATSAPP] Rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                else:
                    print(f"[ERROR] WhatsApp API error: {response.status} - {response.data}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    
            except (MaxRetryError, TimeoutError) as e:
                print(f"[ERROR] WhatsApp network error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            except Exception as e:
                print(f"[ERROR] WhatsApp unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        print(f"[ERROR] Failed to send message after {max_retries} attempts")
        return False
    
    @staticmethod
    def download_image(media_id, max_retries=3):
        """Download image from WhatsApp with retry logic"""
        if not WHATSAPP_TOKEN:
            raise Exception("WhatsApp token not configured")
            
        if not media_id:
            raise Exception("No media ID provided")
            
        print(f"[WHATSAPP] Downloading image: {media_id}")
        
        for attempt in range(max_retries):
            try:
                # Get media info
                url = f"https://graph.facebook.com/v18.0/{media_id}"
                headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
                
                response = http.request("GET", url, headers=headers)
                if response.status != 200:
                    raise Exception(f"Failed to get media info: {response.status}")
                    
                media_info = json.loads(response.data)
                media_url = media_info.get("url")
                
                if not media_url:
                    raise Exception("Could not get media URL from response")
                
                # Download the actual image
                response = http.request("GET", media_url, headers=headers)
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")
                    
                image_data = response.data
                if not image_data:
                    raise Exception("Empty image data received")
                    
                print(f"[WHATSAPP] Image downloaded, size: {len(image_data)} bytes")
                return image_data
                
            except Exception as e:
                print(f"[ERROR] Image download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise Exception(f"Failed to download image after {max_retries} attempts: {e}")
