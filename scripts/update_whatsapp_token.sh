#!/bin/bash
# Update WhatsApp Access Token in Lambda

echo "=========================================="
echo "UPDATE WHATSAPP TOKEN"
echo "=========================================="
echo ""
echo "Get your new token from:"
echo "https://developers.facebook.com/apps"
echo "WhatsApp > API Setup > Temporary access token"
echo ""
read -p "Enter new WhatsApp token: " NEW_TOKEN

if [ -z "$NEW_TOKEN" ]; then
    echo "❌ No token provided"
    exit 1
fi

echo ""
echo "Updating Lambda function..."

aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --environment "Variables={
    WHATSAPP_TOKEN=$NEW_TOKEN,
    PHONE_NUMBER_ID=1049535664900621,
    VERIFY_TOKEN=mySecret_123,
    USE_ANTHROPIC_DIRECT=true,
    ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY,
    OPENWEATHER_API_KEY=YOUR_OPENWEATHER_API_KEY,
    AGMARKNET_API_KEY=YOUR_AGMARKNET_API_KEY,
    CROP_HEALTH_API_KEY=YOUR_CROP_HEALTH_API_KEY,
    S3_BUCKET=kisaanmitra-images,
    CONVERSATION_TABLE=kisaanmitra-conversations,
    PRICE_FORECAST_TABLE=kisaanmitra-price-forecasts
  }" \
  --region ap-south-1

echo ""
echo "✅ Token updated!"
echo ""
echo "Test by sending 'Hi' to your WhatsApp number"
echo ""
