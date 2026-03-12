"""Single Lambda entry point for the WhatsApp webhook and the web demo."""
import json

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
}


def _method(event):
    # REST API puts it in httpMethod, HTTP API / function URLs in requestContext
    return (event.get('httpMethod')
            or event.get('requestContext', {}).get('http', {}).get('method', '')).upper()


def lambda_handler(event, context):
    try:
        params = event.get('queryStringParameters') or {}

        # Meta verifies the webhook with a GET carrying hub.* params
        if 'hub.verify_token' in params or 'hub.challenge' in params:
            from lambda_handler_v2 import lambda_handler as whatsapp_handler
            return whatsapp_handler(event, context)

        # browser CORS preflight from the web demo
        if _method(event) == 'OPTIONS':
            from lambda_handler_web import lambda_handler as web_handler
            return web_handler(event, context)

        body = json.loads(event.get('body') or '{}')

        if body.get('object') == 'whatsapp_business_account':
            from lambda_handler_v2 import lambda_handler as whatsapp_handler
            return whatsapp_handler(event, context)

        if 'user_id' in body and 'type' in body:
            from lambda_handler_web import lambda_handler as web_handler
            return web_handler(event, context)

        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Unknown request type'})
        }

    except Exception as e:
        print(f"[ERROR] Routing error: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Internal server error'})
        }
