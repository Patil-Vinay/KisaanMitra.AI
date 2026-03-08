"""
KisaanMitra Web Demo Handler - API Gateway Compatible
Allows evaluators to test via web interface
"""
import json
import os
import sys
import base64

sys.path.append('/opt/python')

# Import services
from services.language_service import LanguageService
from services.conversation_service import ConversationService
from services.ai_service import AIService

# Import agents
from agents.crop_agent import CropAgent
from agents.market_agent import MarketAgent
from agents.finance_agent import FinanceAgent
from agents.general_agent import GeneralAgent

# Import optional features
try:
    from farmer_onboarding import onboarding_manager
    ONBOARDING_AVAILABLE = True
except:
    ONBOARDING_AVAILABLE = False

try:
    from enhanced_disease_detection import detect_disease_with_confidence, format_disease_response
    ENHANCED_DISEASE_AVAILABLE = True
except:
    ENHANCED_DISEASE_AVAILABLE = False

print(f"[INIT] KisaanMitra Web Demo Handler")
print(f"[INIT] Onboarding: {ONBOARDING_AVAILABLE}, Disease Detection: {ENHANCED_DISEASE_AVAILABLE}")


def lambda_handler(event, context):
    """Handle web demo requests via API Gateway"""
    
    print(f"[WEB DEMO] Request received")
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'OK'})
        }
    
    try:
        # Parse request body
        if not event.get('body'):
            print(f"[ERROR] No body in event: {event}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'No body provided'})
            }
        
        print(f"[DEBUG] Raw body: {event['body'][:200]}")
        body = json.loads(event['body'])
        print(f"[DEBUG] Parsed body keys: {body.keys()}")
        user_id = body.get('user_id', 'web_demo_user')
        message_type = body.get('type', 'text')
        language = body.get('language', 'english')
        
        print(f"[WEB DEMO] User: {user_id}, Type: {message_type}, Language: {language}")
        
        # Handle text messages
        if message_type == 'text':
            user_message = body.get('message', '')
            if not user_message:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'No message provided'})
                }
            
            response = handle_text_message_web(user_message, user_id, language)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'response': response,
                    'user_id': user_id,
                    'language': language
                })
            }
        
        # Handle image messages (disease detection)
        elif message_type == 'image':
            image_data = body.get('image')  # Base64 encoded
            if not image_data:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'No image provided'})
                }
            
            response = handle_image_message_web(image_data, user_id, language)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'response': response,
                    'user_id': user_id,
                    'language': language
                })
            }
        
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': f'Unsupported message type: {message_type}'})
            }
    
    except Exception as e:
        print(f"[ERROR] Web demo error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }


def handle_text_message_web(user_message, user_id, language):
    """Handle text messages from web interface"""
    
    print(f"[WEB TEXT] Message: {user_message}")
    
    # For web demo, skip onboarding and handle queries directly
    # This allows evaluators to test functionality immediately
    print(f"[WEB DEMO] Skipping onboarding for web users - direct query handling")
    
    # Handle greetings
    if user_message.strip().lower() in ['hi', 'hello', 'hey', 'start', 'namaste']:
        return """🌾 *Welcome to KisaanMitra!*

I'm your AI farming assistant. I can help you with:

🌱 *Crop Advice* - Growing tips, pest control
📊 *Market Intelligence* - Live prices, forecasts
💰 *Finance Planning* - Budget, ROI, schemes
🌤️ *Weather Updates* - Hyperlocal forecasts
🔬 *Disease Detection* - Upload crop images

What would you like to know?"""
    
    # Route to appropriate agent
    agent = AIService.route_message(user_message)
    print(f"[WEB ROUTING] Selected agent: {agent.upper()}")
    
    # Execute agent
    if agent == "crop":
        reply, _ = CropAgent.handle(user_message, user_id, language)
    elif agent == "market":
        reply, _ = MarketAgent.handle(user_message, user_id, language)
    elif agent == "finance":
        reply, _ = FinanceAgent.handle(user_message, user_id, language)
    else:
        reply, _ = GeneralAgent.handle(user_message, user_id, language)
    
    # Save conversation
    try:
        ConversationService.save(user_id, user_message, reply, agent)
    except:
        pass
    
    return reply


def handle_image_message_web(image_data, user_id, language):
    """Handle image messages (disease detection) from web interface"""
    
    print(f"[WEB IMAGE] Processing disease detection")
    
    if not ENHANCED_DISEASE_AVAILABLE:
        return "❌ Disease detection is not available in this demo."
    
    try:
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # Get Bedrock client for image analysis
        # Note: We pass None to let the function create its own optimized client
        result = detect_disease_with_confidence(image_bytes, bedrock_client=None)
        
        if result:
            response = format_disease_response(result, language)
            return response
        else:
            if language == 'english':
                return "❌ Could not analyze the image. Please ensure it's a clear photo of a crop leaf or plant."
            else:
                return "❌ छवि का विश्लेषण नहीं कर सका। कृपया सुनिश्चित करें कि यह फसल की पत्ती या पौधे की स्पष्ट तस्वीर है।"
    
    except Exception as e:
        print(f"[ERROR] Image processing error: {e}")
        import traceback
        traceback.print_exc()
        
        if language == 'english':
            return "❌ Error processing image. Please try again with a different image."
        else:
            return "❌ छवि प्रोसेसिंग में त्रुटि। कृपया किसी अन्य छवि के साथ पुनः प्रयास करें।"
