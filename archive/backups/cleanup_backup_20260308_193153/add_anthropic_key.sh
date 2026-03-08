#!/bin/bash

# Add Anthropic API Key to Lambda Environment Variables

set -e

FUNCTION_NAME="whatsapp-llama-bot"
REGION="ap-south-1"

echo "🔑 Adding Anthropic API Key to Lambda..."
echo ""
echo "Please enter your Anthropic API key (starts with sk-ant-):"
read -s ANTHROPIC_API_KEY

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: API key cannot be empty"
    exit 1
fi

if [[ ! "$ANTHROPIC_API_KEY" =~ ^sk-ant- ]]; then
    echo "⚠️  Warning: API key doesn't start with 'sk-ant-'. Are you sure this is correct?"
    echo "Continue anyway? (y/n)"
    read -r confirm
    if [ "$confirm" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

echo ""
echo "📝 Updating Lambda environment variables..."

# Get current environment variables
CURRENT_ENV=$(aws lambda get-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Environment.Variables' \
    --output json)

# Add ANTHROPIC_API_KEY and USE_ANTHROPIC_DIRECT to environment
UPDATED_ENV=$(echo $CURRENT_ENV | jq --arg key "$ANTHROPIC_API_KEY" '. + {ANTHROPIC_API_KEY: $key, USE_ANTHROPIC_DIRECT: "true"}')

# Update Lambda
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --environment "Variables=$UPDATED_ENV" \
    > /dev/null

echo "⏳ Waiting for update to complete..."
aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION

echo "✅ Anthropic API key added successfully!"
echo ""
echo "🎯 Configuration:"
echo "   - ANTHROPIC_API_KEY: sk-ant-***${ANTHROPIC_API_KEY: -4}"
echo "   - USE_ANTHROPIC_DIRECT: true"
echo ""
echo "📊 The Lambda will now use direct Anthropic Claude API for better accuracy!"
echo ""
echo "🧪 Test with:"
echo "   Send a budget request via WhatsApp"
echo ""
echo "📊 View logs:"
echo "   aws logs tail /aws/lambda/$FUNCTION_NAME --follow --region $REGION"
