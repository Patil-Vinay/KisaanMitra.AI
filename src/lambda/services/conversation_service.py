"""
Conversation Service - Handles conversation history and context
"""
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
conversation_table = dynamodb.Table("kisaanmitra-conversations")


class ConversationService:
    """Manages conversation history and context building"""
    
    @staticmethod
    def get_history(user_id, limit=3):
        """Get recent conversation history from DynamoDB"""
        try:
            print(f"[CONVERSATION] Fetching history for user: {user_id}, limit: {limit}")
            response = conversation_table.query(
                KeyConditionExpression="user_id = :uid",
                ExpressionAttributeValues={":uid": user_id},
                ScanIndexForward=False,
                Limit=limit
            )
            items = response.get("Items", [])
            print(f"[CONVERSATION] Retrieved {len(items)} items")
            return items
        except Exception as e:
            print(f"[ERROR] Error fetching conversation history: {e}")
            return []
    
    @staticmethod
    def save(user_id, message, response, agent_type):
        """Save conversation to DynamoDB"""
        try:
            print(f"[CONVERSATION] Saving - User: {user_id}, Agent: {agent_type}")
            conversation_table.put_item(Item={
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "response": response,
                "agent": agent_type
            })
            print(f"[CONVERSATION] Saved successfully")
        except Exception as e:
            print(f"[ERROR] Error saving conversation: {e}")
    
    @staticmethod
    def build_context(history):
        """Build context string from conversation history"""
        if not history or len(history) == 0:
            return ""
        
        print(f"[CONVERSATION] Building context from {len(history)} items")
        context = "Previous conversation:\n"
        for item in reversed(history[-2:]):  # Only last 2 messages
            msg = item.get('message', '')
            resp = item.get('response', '')[:200]  # Truncate
            context += f"User: {msg}\nBot: {resp}...\n"
        
        return context
