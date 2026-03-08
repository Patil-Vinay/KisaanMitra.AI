"""
Conversation Service - Handles conversation history and context
"""
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
conversation_table = dynamodb.Table("kisaanmitra-conversations")


class ConversationService:
    """Manages conversation history and context building with optimized database operations"""

    # Connection pool for DynamoDB
    _dynamodb_resource = None
    _conversation_table = None

    @classmethod
    def _get_table(cls):
        """Get DynamoDB table with connection pooling"""
        if cls._conversation_table is None:
            if cls._dynamodb_resource is None:
                cls._dynamodb_resource = boto3.resource(
                    "dynamodb",
                    region_name="ap-south-1",
                    config=boto3.session.Config(
                        retries={'max_attempts': 3, 'mode': 'adaptive'},
                        max_pool_connections=10
                    )
                )
            cls._conversation_table = cls._dynamodb_resource.Table("kisaanmitra-conversations")
        return cls._conversation_table

    @staticmethod
    def get_history(user_id, limit=3):
        """Get recent conversation history with optimized query"""
        if not user_id or not user_id.strip():
            return []

        try:
            print(f"[CONVERSATION] Fetching history for user: {user_id}, limit: {limit}")

            table = ConversationService._get_table()

            # Optimized query with projection to reduce data transfer
            response = table.query(
                KeyConditionExpression="user_id = :uid",
                ExpressionAttributeValues={":uid": user_id},
                ProjectionExpression="user_id, #ts, message, #resp, agent",
                ExpressionAttributeNames={
                    "#ts": "timestamp",
                    "#resp": "response"
                },
                ScanIndexForward=False,
                Limit=limit
            )

            items = response.get("Items", [])
            print(f"[CONVERSATION] Retrieved {len(items)} items")
            return items

        except Exception as e:
            print(f"[ERROR] Error fetching conversation history: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return []

    @staticmethod
    def save(user_id, message, response, agent_type):
        """Save conversation with optimized write and input validation"""
        if not user_id or not user_id.strip():
            print(f"[ERROR] Invalid user_id for conversation save")
            return False

        if not message or not response:
            print(f"[ERROR] Missing message or response for conversation save")
            return False

        try:
            print(f"[CONVERSATION] Saving - User: {user_id}, Agent: {agent_type}")

            # Truncate long messages to prevent DynamoDB item size limits (400KB)
            truncated_message = message[:1000] if len(message) > 1000 else message
            truncated_response = response[:2000] if len(response) > 2000 else response

            table = ConversationService._get_table()

            # Use batch write for better performance if needed
            table.put_item(
                Item={
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": truncated_message,
                    "response": truncated_response,
                    "agent": agent_type or "unknown"
                },
                # Conditional write to prevent overwrites
                ConditionExpression="attribute_not_exists(user_id) OR attribute_not_exists(#ts)",
                ExpressionAttributeNames={"#ts": "timestamp"}
            )

            print(f"[CONVERSATION] Saved successfully")
            return True

        except Exception as e:
            print(f"[ERROR] Error saving conversation: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def build_context(history):
        """Build optimized context string from conversation history"""
        if not history or len(history) == 0:
            return ""

        print(f"[CONVERSATION] Building context from {len(history)} items")

        # Limit context size to prevent token overflow
        context_parts = []
        total_length = 0
        max_context_length = 1000  # Reasonable limit

        # Process most recent conversations first
        for item in reversed(history[-2:]):  # Only last 2 messages
            msg = item.get('message', '')
            resp = item.get('response', '')

            # Truncate individual messages
            if len(msg) > 200:
                msg = msg[:200] + "..."
            if len(resp) > 200:
                resp = resp[:200] + "..."

            context_part = f"User: {msg}\nBot: {resp}\n"

            if total_length + len(context_part) > max_context_length:
                break

            context_parts.append(context_part)
            total_length += len(context_part)

        if context_parts:
            return "Previous conversation:\n" + "".join(context_parts)
        else:
            return ""

    @staticmethod
    def cleanup_old_conversations(user_id, keep_days=30):
        """Clean up old conversations to manage storage costs"""
        try:
            from datetime import timedelta

            cutoff_date = (datetime.utcnow() - timedelta(days=keep_days)).isoformat()

            table = ConversationService._get_table()

            # Query old items
            response = table.query(
                KeyConditionExpression="user_id = :uid AND #ts < :cutoff",
                ExpressionAttributeValues={
                    ":uid": user_id,
                    ":cutoff": cutoff_date
                },
                ExpressionAttributeNames={"#ts": "timestamp"},
                ProjectionExpression="user_id, #ts"
            )

            old_items = response.get("Items", [])

            # Batch delete old items
            if old_items:
                with table.batch_writer() as batch:
                    for item in old_items:
                        batch.delete_item(
                            Key={
                                'user_id': item['user_id'],
                                'timestamp': item['timestamp']
                            }
                        )

                print(f"[CONVERSATION] Cleaned up {len(old_items)} old conversations for {user_id}")

        except Exception as e:
            print(f"[ERROR] Error cleaning up conversations: {e}")
