#!/bin/bash

# Add OpenWeather API key to Lambda function
# Usage: ./add_weather_key.sh YOUR_API_KEY

WEATHER_KEY=$1

if [ -z "$WEATHER_KEY" ]; then
    echo "❌ Error: No API key provided"
    echo ""
    echo "Usage: ./add_weather_key.sh YOUR_API_KEY"
    echo ""
    echo "Get your free API key from: https://openweathermap.org/api"
    exit 1
fi

echo "🔧 Adding OpenWeather API key to Lambda..."

# Get current environment variables
CURRENT_ENV=$(aws lambda get-function-configuration \
    --function-name whatsapp-llama-bot \
    --region ap-south-1 \
    --query 'Environment.Variables' \
    --output json)

# Add the weather key
UPDATED_ENV=$(echo $CURRENT_ENV | jq ". + {OPENWEATHER_API_KEY: \"$WEATHER_KEY\"}")

# Update Lambda
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --region ap-south-1 \
    --environment "Variables=$UPDATED_ENV" \
    > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Weather API key added successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Wait 1-2 minutes for Lambda to update"
    echo "2. Send a crop query via WhatsApp: 'When should I plant wheat?'"
    echo "3. Check logs: aws logs tail /aws/lambda/whatsapp-llama-bot --follow"
    echo ""
    echo "You should see real weather data instead of mock data!"
else
    echo "❌ Failed to add API key"
    echo "Please check your AWS credentials and try again"
    exit 1
fi
