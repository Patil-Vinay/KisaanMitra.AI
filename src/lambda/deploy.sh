#!/bin/bash
# Packages the bot and updates the whatsapp-llama-bot Lambda.
# Run from src/lambda.
set -e

FUNCTION=whatsapp-llama-bot
REGION=ap-south-1
ZIP=whatsapp_deployment.zip

cd "$(dirname "$0")"
rm -f $ZIP

echo "Creating package..."
zip -r -q $ZIP \
    lambda_handler_unified.py \
    lambda_handler_v2.py \
    lambda_handler_web.py \
    services/ \
    agents/ \
    anthropic_client.py \
    whatsapp_interactive.py \
    navigation_controller.py \
    weather_service.py \
    market_data_sources.py \
    price_forecasting.py \
    forecast_reply.py \
    enhanced_disease_detection.py \
    -x "*.pyc" -x "*__pycache__*"

# onboarding and hyperlocal modules sit at the zip root
zip -j -q $ZIP ../onboarding/farmer_onboarding.py ../hyperlocal/disease_tracker.py

echo "Uploading..."
aws lambda update-function-code \
    --function-name $FUNCTION \
    --zip-file fileb://$ZIP \
    --region $REGION > /dev/null
aws lambda wait function-updated --function-name $FUNCTION --region $REGION

# one handler serves both the WhatsApp webhook and the web demo
aws lambda update-function-configuration \
    --function-name $FUNCTION \
    --handler lambda_handler_unified.lambda_handler \
    --region $REGION > /dev/null
aws lambda wait function-updated --function-name $FUNCTION --region $REGION

echo "Done. Logs: aws logs tail /aws/lambda/$FUNCTION --follow --region $REGION"
