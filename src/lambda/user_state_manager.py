"""
User State Management
Tracks what the user is currently doing to improve routing accuracy
"""

import boto3
import time
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
state_table = dynamodb.Table('kisaanmitra-user-state')

def set_user_state(user_id, state, context=None):
    """
    Set user's current interaction state
    
    States:
    - awaiting_budget_details: User clicked Budget Planning, waiting for crop/land/location
    - awaiting_market_query: User clicked Market Price, waiting for crop name
    - awaiting_crop_health: User clicked Crop Health, waiting for image/description
    - None: No specific state, use AI orchestrator
    """
    try:
        item = {
            'user_id': user_id,
            'state': state,
            'timestamp': datetime.utcnow().isoformat(),
            'ttl': int(time.time()) + 3600  # Expire after 1 hour
        }
        
        if context:
            item['context'] = context
        
        state_table.put_item(Item=item)
        print(f"[STATE] Set user {user_id} state to: {state}")
        return True
    except Exception as e:
        print(f"[STATE ERROR] Failed to set state: {e}")
        return False

def get_user_state(user_id):
    """Get user's current state"""
    try:
        response = state_table.get_item(Key={'user_id': user_id})
        item = response.get('Item')
        
        if item:
            print(f"[STATE] User {user_id} state: {item.get('state')}")
            return item
        else:
            print(f"[STATE] No state found for user {user_id}")
            return None
    except Exception as e:
        print(f"[STATE ERROR] Failed to get state: {e}")
        return None

def clear_user_state(user_id):
    """Clear user's state"""
    try:
        state_table.delete_item(Key={'user_id': user_id})
        print(f"[STATE] Cleared state for user {user_id}")
        return True
    except Exception as e:
        print(f"[STATE ERROR] Failed to clear state: {e}")
        return False

def get_agent_from_state(state):
    """Map state to agent"""
    state_to_agent = {
        'awaiting_budget_details': 'finance',
        'awaiting_market_query': 'market',
        'awaiting_crop_health': 'crop'
    }
    return state_to_agent.get(state)
