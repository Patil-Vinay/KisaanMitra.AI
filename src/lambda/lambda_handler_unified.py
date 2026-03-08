"""
KisaanMitra Unified Handler - Handles both WhatsApp and Web requests
"""
import json
import os

# Check if this is a WhatsApp webhook or Web API request
def lambda_handler(event, context):
    """Route to appropriate handler based on request type"""
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Check if this is a WhatsApp webhook
        if 'object' in body and body.get('object') == 'whatsapp_business_account':
            # Import and use WhatsApp handler
            from lambda_handler_v2 import lambda_handler as whatsapp_handler
            return whatsapp_handler(event, context)
        
        # Check if this is a web API request
        elif 'user_id' in body and 'type' in body:
            # Import and use Web handler
            from lambda_handler_web import lambda_handler as web_handler
            return web_handler(event, context)
        
        # Unknown request type
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Unknown request type',
                    'hint': 'Expected WhatsApp webhook or Web API request'
                })
            }
    
    except Exception as e:
        print(f"[ERROR] Routing error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }
