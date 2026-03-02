"""
Language Service - Handles user language preferences
"""
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
conversation_table = dynamodb.Table("kisaanmitra-conversations")


class LanguageService:
    """Manages user language preferences"""
    
    @staticmethod
    def get_user_language(user_id, message_text=""):
        """Get user's language preference with auto-detection"""
        # Auto-detect English if message contains only English characters
        if message_text:
            has_hindi = any('\u0900' <= char <= '\u097F' for char in message_text)
            is_english_greeting = message_text.lower().strip() in [
                'hi', 'hii', 'hiii', 'hello', 'hey', 'helo'
            ]
            
            if not has_hindi and (is_english_greeting or len(message_text.split()) > 2):
                print(f"[LANGUAGE] Auto-detected English from message: {message_text[:50]}")
                LanguageService.set_user_language(user_id, 'english')
                return 'english'
        
        # Fetch from DynamoDB
        try:
            response = conversation_table.get_item(
                Key={'user_id': user_id, 'timestamp': 'language_preference'}
            )
            if 'Item' in response:
                return response['Item'].get('language', 'hindi')
        except Exception as e:
            print(f"[ERROR] Failed to get language preference: {e}")
        
        return 'hindi'  # Default
    
    @staticmethod
    def set_user_language(user_id, language):
        """Set user's language preference"""
        try:
            conversation_table.put_item(Item={
                'user_id': user_id,
                'timestamp': 'language_preference',
                'language': language
            })
            print(f"[LANGUAGE] Set {user_id} language to: {language}")
        except Exception as e:
            print(f"[ERROR] Failed to save language preference: {e}")
