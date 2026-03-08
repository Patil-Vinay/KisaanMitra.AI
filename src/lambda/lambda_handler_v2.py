"""
KisaanMitra WhatsApp Lambda Handler - Microservice Architecture
Simplified, modular, and maintainable
"""
import json
import os
import sys

sys.path.append('/opt/python')

# Import services
from services.language_service import LanguageService
from services.conversation_service import ConversationService
from services.whatsapp_service import WhatsAppService
from services.ai_service import AIService

# Import agents
from agents.crop_agent import CropAgent
from agents.market_agent import MarketAgent
from agents.finance_agent import FinanceAgent
from agents.general_agent import GeneralAgent

# Import optional features
try:
    from whatsapp_interactive import (
        create_main_menu, create_back_button, create_language_selection
    )
    INTERACTIVE_AVAILABLE = True
except:
    INTERACTIVE_AVAILABLE = False

try:
    from navigation_controller import NavigationController
    NAVIGATION_AVAILABLE = True
except:
    NAVIGATION_AVAILABLE = False

try:
    from farmer_onboarding import onboarding_manager
    ONBOARDING_AVAILABLE = True
except:
    ONBOARDING_AVAILABLE = False

try:
    from enhanced_disease_detection import (
        detect_disease_with_confidence, format_disease_response, save_disease_detection
    )
    ENHANCED_DISEASE_AVAILABLE = True
except:
    ENHANCED_DISEASE_AVAILABLE = False

try:
    from disease_tracker import hyperlocal_tracker
    HYPERLOCAL_AVAILABLE = True
except:
    HYPERLOCAL_AVAILABLE = False

# Environment variables
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mySecret_123")

print(f"[INIT] KisaanMitra Lambda Handler v2.0 - Microservice Architecture")
print(f"[INIT] Interactive: {INTERACTIVE_AVAILABLE}, Onboarding: {ONBOARDING_AVAILABLE}")
print(f"[INIT] Disease Detection: {ENHANCED_DISEASE_AVAILABLE}, Hyperlocal: {HYPERLOCAL_AVAILABLE}")


def lambda_handler(event, context):
    """Main Lambda handler - optimized with monitoring and memory management"""
    import gc  # Garbage collection for memory optimization

    print(f"[LAMBDA] ========================================")
    print(f"[LAMBDA] INVOCATION STARTED")
    print(f"[LAMBDA] Memory limit: {context.memory_limit_in_mb}MB")
    print(f"[LAMBDA] Remaining time: {context.get_remaining_time_in_millis()}ms")
    print(f"[LAMBDA] ========================================")

    # Import monitoring if available
    try:
        from services.cache_service import CacheService
        cache_stats = CacheService.get_stats()
        print(f"[LAMBDA] Cache stats: {cache_stats}")
    except:
        pass

    # Webhook verification
    if event.get("queryStringParameters"):
        params = event["queryStringParameters"]
        if params and params.get("hub.verify_token") == VERIFY_TOKEN:
            print(f"[LAMBDA] Webhook verification successful")
            return {'statusCode': 200, 'body': params.get("hub.challenge", "")}

    try:
        # Enhanced input validation
        if not event.get("body"):
            print(f"[ERROR] No body in event")
            return {'statusCode': 400, 'body': 'No body provided'}

        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in body: {e}")
            return {'statusCode': 400, 'body': 'Invalid JSON'}

        # Validate WhatsApp webhook structure with better error handling
        if not body.get("entry") or not isinstance(body["entry"], list) or not body["entry"]:
            print(f"[ERROR] Invalid webhook structure - no entry")
            return {'statusCode': 200, 'body': 'ok'}  # Return 200 to avoid webhook retries

        entry = body["entry"][0]
        if not entry.get("changes") or not isinstance(entry["changes"], list) or not entry["changes"]:
            print(f"[ERROR] Invalid webhook structure - no changes")
            return {'statusCode': 200, 'body': 'ok'}

        change = entry["changes"][0]
        value = change.get("value", {})

        # Ignore status-only updates (but allow contacts with messages)
        if "statuses" in value and "messages" not in value:
            return {'statusCode': 200, 'body': 'ok'}

        if "messages" not in value or not isinstance(value["messages"], list) or not value["messages"]:
            return {'statusCode': 200, 'body': 'ok'}

        msg = value["messages"][0]
        from_number = msg.get("from")
        msg_type = msg.get("type")

        # Enhanced field validation
        if not from_number or not msg_type:
            print(f"[ERROR] Missing required fields: from={from_number}, type={msg_type}")
            return {'statusCode': 200, 'body': 'ok'}

        # Rate limiting per user
        try:
            from services.cache_service import RateLimiter
            user_rate_key = RateLimiter.get_user_key(from_number, "message")
            if not RateLimiter.is_allowed(user_rate_key, max_requests=20, window_seconds=60):
                print(f"[RATE LIMIT] User {from_number} rate limited")
                WhatsAppService.send_message(
                    from_number,
                    "You're sending messages too quickly. Please wait a moment before trying again."
                )
                return {'statusCode': 200, 'body': 'ok'}
        except:
            pass  # Continue without rate limiting if service unavailable

        print(f"[LAMBDA] Message from: {from_number}, Type: {msg_type}")

        # Memory check before processing
        remaining_time = context.get_remaining_time_in_millis()
        if remaining_time < 5000:  # Less than 5 seconds remaining
            print(f"[WARNING] Low remaining time: {remaining_time}ms")
            WhatsAppService.send_message(from_number, "Processing timeout. Please try again.")
            return {'statusCode': 200, 'body': 'timeout'}

        # Handle interactive button/list responses
        if msg_type == "interactive":
            result = handle_interactive_response(msg, from_number)
            gc.collect()  # Memory cleanup
            return result

        # Check user onboarding status
        is_new_user, onboarding_state = check_user_status(from_number)

        # Handle new users or users in onboarding
        if is_new_user or (onboarding_state and onboarding_state != "completed"):
            result = handle_onboarding(msg, from_number, msg_type)
            gc.collect()  # Memory cleanup
            return result

        # Handle existing users
        if msg_type == "text":
            result = handle_text_message(msg, from_number)
        elif msg_type == "image":
            result = handle_image_message(msg, from_number)
        else:
            result = handle_unsupported_message(from_number, msg_type)

        # Final memory cleanup
        gc.collect()

        # Log final stats
        final_time = context.get_remaining_time_in_millis()
        processing_time = remaining_time - final_time
        print(f"[LAMBDA] Processing completed in {processing_time}ms")

        return result

    except KeyError as e:
        print(f"[ERROR] Missing required key in webhook data: {e}")
        return {'statusCode': 200, 'body': 'ok'}  # Return 200 to avoid retries
    except Exception as e:
        print(f"[ERROR] Lambda error: {e}")
        import traceback
        traceback.print_exc()

        # Enhanced error reporting
        try:
            if 'from_number' in locals() and from_number:
                WhatsAppService.send_message(
                    from_number,
                    "Sorry, I encountered an error. Please try again in a moment."
                )
        except:
            pass  # Don't let error handling cause more errors

        # Memory cleanup on error
        gc.collect()

        return {'statusCode': 500, 'body': 'error'}


def check_user_status(user_id):
    """Check if user needs onboarding"""
    if not ONBOARDING_AVAILABLE:
        return False, "completed"
    
    try:
        is_new = onboarding_manager.is_new_user(user_id)
        state, _ = onboarding_manager.get_onboarding_state(user_id)
        
        if state != "completed":
            is_new = True
        
        print(f"[STATUS] User {user_id}: is_new={is_new}, state={state}")
        return is_new, state
    except Exception as e:
        print(f"[ERROR] Status check failed: {e}")
        return True, "new"


def handle_onboarding(msg, from_number, msg_type):
    """Handle onboarding flow"""
    print(f"[ONBOARDING] Processing for {from_number}")
    
    if msg_type != "text":
        WhatsAppService.send_message(
            from_number,
            "🙏 नमस्ते! KisaanMitra में आपका स्वागत है!\n\nपहले अपना रजिस्ट्रेशन पूरा करें।\nकृपया 'Hi' टाइप करें।"
        )
        return {'statusCode': 200, 'body': 'ok'}
    
    user_message = msg["text"]["body"]
    
    if ONBOARDING_AVAILABLE:
        try:
            response, is_completed = onboarding_manager.process_onboarding_message(from_number, user_message)
            WhatsAppService.send_message(from_number, response)
            
            if is_completed:
                print(f"[ONBOARDING] Completed for {from_number}")
        except Exception as e:
            print(f"[ERROR] Onboarding error: {e}")
            WhatsAppService.send_message(from_number, "Sorry, there was an error. Please try again.")
    else:
        WhatsAppService.send_message(from_number, "Onboarding not available. Please contact support.")
    
    return {'statusCode': 200, 'body': 'ok'}


def handle_text_message(msg, from_number):
    """Handle text messages from existing users"""
    user_message = msg["text"]["body"]
    user_lang = LanguageService.get_user_language(from_number, user_message)
    
    print(f"[TEXT] Message: {user_message}, Language: {user_lang}")
    
    # Handle greetings
    if user_message.strip().lower() in ['hi', 'hello', 'hey', 'start']:
        if INTERACTIVE_AVAILABLE:
            WhatsAppService.send_message(from_number, None, create_main_menu(user_lang))
        else:
            greeting = "Hello! How can I help you today?" if user_lang == 'english' else "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?"
            WhatsAppService.send_message(from_number, greeting)
        return {'statusCode': 200, 'body': 'ok'}
    
    # Handle navigation commands
    if handle_navigation_command(user_message, from_number, user_lang):
        return {'statusCode': 200, 'body': 'ok'}
    
    # Route to appropriate agent
    agent = AIService.route_message(user_message)
    print(f"[ROUTING] Selected agent: {agent.upper()}")
    
    # Execute agent
    if agent == "crop":
        reply, should_add_nav = CropAgent.handle(user_message, from_number, user_lang)
    elif agent == "market":
        reply, should_add_nav = MarketAgent.handle(user_message, from_number, user_lang)
    elif agent == "finance":
        reply, should_add_nav = FinanceAgent.handle(user_message, from_number, user_lang)
    else:  # general or greeting
        reply, should_add_nav = GeneralAgent.handle(user_message, from_number, user_lang)
    
    # Save conversation
    ConversationService.save(from_number, user_message, reply, agent)
    
    # Send response
    WhatsAppService.send_message(from_number, reply)
    
    # Send navigation buttons
    if should_add_nav and INTERACTIVE_AVAILABLE:
        WhatsAppService.send_message(from_number, None, create_back_button(user_lang))
    
    print(f"[TEXT] Response sent successfully")
    return {'statusCode': 200, 'body': 'ok'}


def handle_image_message(msg, from_number):
    """Handle image messages (crop disease detection)"""
    print(f"[IMAGE] Processing image from {from_number}")
    
    media_id = msg["image"]["id"]
    user_lang = LanguageService.get_user_language(from_number)
    
    WhatsAppService.send_message(from_number, "🔍 Analyzing your crop image, please wait...")
    
    try:
        # Download image
        image_bytes = WhatsAppService.download_image(media_id)
        
        # Analyze with enhanced detection
        if ENHANCED_DISEASE_AVAILABLE:
            bedrock_for_images = AIService.get_image_client()
            diagnosis = detect_disease_with_confidence(image_bytes, bedrock_for_images)
            reply = format_disease_response(diagnosis, language=user_lang)
            
            # Save detection
            import boto3
            dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
            conversation_table = dynamodb.Table("kisaanmitra-conversations")
            save_disease_detection(from_number, diagnosis, conversation_table)
            
            # Report to hyperlocal system and send alerts
            if HYPERLOCAL_AVAILABLE and ONBOARDING_AVAILABLE and diagnosis.get('primary_disease') != 'Healthy':
                try:
                    print(f"[HYPERLOCAL] Starting alert process for disease: {diagnosis.get('primary_disease')}")
                    profile = onboarding_manager.get_user_profile(from_number)
                    print(f"[HYPERLOCAL] User profile retrieved: {profile is not None}")
                    if profile:
                        village = profile.get('village')
                        district = profile.get('district')
                        crop = profile.get('current_crops', 'unknown')
                        disease_name = diagnosis.get('primary_disease')
                        severity = diagnosis.get('severity', 'medium')
                        reporter_name = profile.get('name', 'A farmer')
                        
                        # Report disease and get farmers to alert
                        report_id, farmers_to_alert = hyperlocal_tracker.report_disease(
                            user_id=from_number,
                            village=village,
                            district=district,
                            crop=crop,
                            disease_name=disease_name,
                            severity=severity,
                            symptoms=diagnosis.get('symptoms', ''),
                            send_alerts=True
                        )
                        
                        # Send alerts to nearby farmers
                        if farmers_to_alert:
                            print(f"[ALERT] Sending disease alerts to {len(farmers_to_alert)} farmers")
                            
                            # Format the alert message
                            alert_message = hyperlocal_tracker.format_disease_alert_notification(
                                disease_name, severity, village, reporter_name, crop, user_lang
                            )
                            
                            # Send notifications to each farmer
                            alerts_sent = 0
                            for farmer in farmers_to_alert:
                                try:
                                    farmer_id = farmer.get('user_id') or farmer.get('phone')
                                    if not farmer_id:
                                        continue
                                    
                                    # Get farmer's language preference
                                    farmer_lang = LanguageService.get_user_language(farmer_id)
                                    
                                    # Re-format message in farmer's language if different
                                    if farmer_lang != user_lang:
                                        alert_message = hyperlocal_tracker.format_disease_alert_notification(
                                            disease_name, severity, village, reporter_name, crop, farmer_lang
                                        )
                                    
                                    # Send the alert
                                    WhatsAppService.send_message(farmer_id, alert_message)
                                    alerts_sent += 1
                                    print(f"[ALERT] ✅ Sent alert to {farmer.get('name', farmer_id)}")
                                    
                                    # Small delay to avoid rate limiting
                                    import time
                                    time.sleep(0.1)
                                    
                                except Exception as e:
                                    print(f"[ALERT ERROR] Failed to send alert to {farmer.get('name', 'unknown')}: {e}")
                            
                            # Update the report with alerts sent count
                            hyperlocal_tracker.update_alerts_sent_count(report_id, alerts_sent)
                            
                            print(f"[ALERT] ✅ Sent {alerts_sent}/{len(farmers_to_alert)} disease alerts successfully")
                            
                            # Add confirmation to reply
                            if user_lang == 'hindi':
                                reply += f"\n\n📢 {len(farmers_to_alert)} किसानों को चेतावनी भेजी गई।"
                            else:
                                reply += f"\n\n📢 Alert sent to {len(farmers_to_alert)} nearby farmers."
                except Exception as e:
                    print(f"[IMAGE] Hyperlocal error: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            # Fallback to basic analysis
            reply = "Image analysis not available. Please try again later."
        
        # Send response
        WhatsAppService.send_message(from_number, reply)
        
        # Send navigation buttons
        if INTERACTIVE_AVAILABLE:
            WhatsAppService.send_message(from_number, None, create_back_button(user_lang))
        
        print(f"[IMAGE] Analysis complete")
        return {'statusCode': 200, 'body': 'ok'}
    
    except Exception as e:
        print(f"[ERROR] Image processing error: {e}")
        WhatsAppService.send_message(from_number, "Sorry, I couldn't analyze the image. Please try again.")
        return {'statusCode': 200, 'body': 'ok'}


def handle_interactive_response(msg, from_number):
    """Handle interactive button/list responses"""
    print(f"[INTERACTIVE] Processing button/list response")
    
    interactive_response = msg.get("interactive", {})
    response_type = interactive_response.get("type")
    user_lang = LanguageService.get_user_language(from_number)
    
    if response_type == "button_reply":
        button_id = interactive_response.get("button_reply", {}).get("id")
        print(f"[INTERACTIVE] Button clicked: {button_id}")
        
        # Handle language selection
        if button_id in ["lang_english", "lang_hindi"]:
            lang = 'english' if button_id == "lang_english" else 'hindi'
            LanguageService.set_user_language(from_number, lang)
            
            if ONBOARDING_AVAILABLE:
                # Restart onboarding in selected language
                onboarding_manager.onboarding_table.delete_item(Key={"user_id": from_number})
                onboarding_manager.profile_table.delete_item(Key={"user_id": from_number})
                response, _ = onboarding_manager.process_onboarding_message(from_number, "start")
                WhatsAppService.send_message(from_number, response)
            else:
                WhatsAppService.send_message(from_number, None, create_main_menu(lang))
            
            return {'statusCode': 200, 'body': 'ok'}
        
        # Handle navigation buttons
        if button_id in ["nav_back", "nav_home", "nav_cancel"]:
            if NAVIGATION_AVAILABLE:
                nav = NavigationController(from_number)
                if button_id == "nav_back":
                    nav.go_back()
                elif button_id == "nav_home":
                    nav.go_home()
                else:
                    nav.cancel()
            
            WhatsAppService.send_message(from_number, None, create_main_menu(user_lang))
            return {'statusCode': 200, 'body': 'ok'}
    
    elif response_type == "list_reply":
        list_id = interactive_response.get("list_reply", {}).get("id")
        print(f"[INTERACTIVE] List item selected: {list_id}")
        
        # Handle main menu selections
        if list_id == "crop_health":
            prompt = "🌿 *Crop Health Check*\n\nPlease send a photo of your crop or describe the problem in detail." if user_lang == 'english' else "🌿 *फसल स्वास्थ्य जांच*\n\nकृपया अपनी फसल की तस्वीर भेजें या समस्या का विस्तार से वर्णन करें।"
            WhatsAppService.send_message(from_number, prompt)
        elif list_id == "market_price":
            # Call MarketAgent to provide actual market intelligence with live rates and forecasting
            from agents.market_agent import MarketAgent
            
            # Get user profile to determine default crop or provide general market intelligence
            profile = None
            if ONBOARDING_AVAILABLE:
                try:
                    from farmer_onboarding import onboarding_manager
                    profile = onboarding_manager.get_user_profile(from_number)
                except:
                    pass
            
            # Provide market intelligence for common crops or user's profile crop
            if profile and profile.get('crops'):
                # Use first crop from profile
                crop_name = profile['crops'][0] if isinstance(profile['crops'], list) else profile['crops']
                market_query = f"What is the current price of {crop_name}?"
            else:
                # Provide market intelligence for tomato (most common crop)
                market_query = "What is the current price of tomato?"
            
            reply, should_add_nav = MarketAgent.handle(market_query, from_number, user_lang)
            WhatsAppService.send_message(from_number, reply)
            if should_add_nav and INTERACTIVE_AVAILABLE:
                WhatsAppService.send_message(from_number, None, create_back_button(user_lang))
        elif list_id == "budget_plan":
            prompt = "💰 *Budget Planning*\n\nPlease tell me:\n• Which crop?\n• How much land (acres)?\n• Location?" if user_lang == 'english' else "💰 *बजट योजना*\n\nकृपया बताएं:\n• कौन सी फसल?\n• कितनी जमीन (एकड़)?\n• स्थान?"
            WhatsAppService.send_message(from_number, prompt)
        elif list_id == "weather":
            # Call GeneralAgent to handle weather with KG profile
            reply, should_add_nav = GeneralAgent.handle("weather", from_number, user_lang)
            WhatsAppService.send_message(from_number, reply)
            if should_add_nav and INTERACTIVE_AVAILABLE:
                WhatsAppService.send_message(from_number, None, create_back_button(user_lang))
        
        return {'statusCode': 200, 'body': 'ok'}
    
    return {'statusCode': 200, 'body': 'ok'}


def handle_navigation_command(user_message, from_number, user_lang):
    """Handle navigation commands (back, home, cancel)"""
    user_message_lower = user_message.strip().lower()
    
    if user_message_lower in ['back', 'पीछे', 'home', 'menu', 'main menu', 'मुख्य मेनू', 'होम', 'cancel', 'stop', 'restart', 'रद्द करें', 'बंद करें']:
        print(f"[NAV] Navigation command: {user_message_lower}")
        
        if NAVIGATION_AVAILABLE:
            nav = NavigationController(from_number)
            if user_message_lower in ['back', 'पीछे']:
                nav.go_back()
            elif user_message_lower in ['home', 'menu', 'main menu', 'मुख्य मेनू', 'होम']:
                nav.go_home()
            else:
                nav.cancel()
        
        if INTERACTIVE_AVAILABLE:
            WhatsAppService.send_message(from_number, None, create_main_menu(user_lang))
        
        return True
    
    return False


def handle_unsupported_message(from_number, msg_type):
    """Handle unsupported message types"""
    print(f"[UNSUPPORTED] Message type: {msg_type}")
    user_lang = LanguageService.get_user_language(from_number)
    
    message = "Sorry, I only support text messages and crop images. Please send your question as text." if user_lang == 'english' else "क्षमा करें, मैं केवल टेक्स्ट संदेश और फसल की तस्वीरें समर्थन करता हूं। कृपया अपना सवाल टेक्स्ट में भेजें।"
    WhatsAppService.send_message(from_number, message)
    
    return {'statusCode': 200, 'body': 'ok'}
