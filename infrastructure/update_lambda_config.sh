#!/bin/bash

# Update Lambda Configuration for Full Agent Integration
# Run this after deploying the updated Lambda code

set -e

FUNCTION_NAME="whatsapp-llama-bot"
REGION="ap-south-1"

echo "🔧 Updating Lambda configuration for $FUNCTION_NAME..."

# 1. Update timeout and memory
echo "📊 Setting timeout to 60s and memory to 512 MB..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 60 \
    --memory-size 512 \
    --region $REGION

echo "✅ Configuration updated"

# 2. Check environment variables
echo ""
echo "📋 Current environment variables:"
aws lambda get-function-configuration \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Environment.Variables' \
    --output json

echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo ""
echo "1. Add AGMARKNET_API_KEY environment variable:"
echo "   - Go to: https://data.gov.in/"
echo "   - Register and get API key"
echo "   - Add to Lambda: Configuration → Environment variables"
echo ""
echo "2. Verify these environment variables exist:"
echo "   ✓ VERIFY_TOKEN"
echo "   ✓ WHATSAPP_TOKEN"
echo "   ✓ PHONE_NUMBER_ID"
echo "   ✓ CROP_HEALTH_API_KEY"
echo "   ✓ AGMARKNET_API_KEY (NEW)"
echo ""
echo "3. Create DynamoDB tables (if not exists):"
echo "   bash infrastructure/setup_finance_tables.sh"
echo ""
echo "4. Update IAM role permissions:"
echo "   - Add DynamoDB access for kisaanmitra-market-data"
echo "   - Add DynamoDB access for kisaanmitra-finance"
echo ""
echo "5. Test the deployment:"
echo "   - Send WhatsApp: 'गेहूं का भाव क्या है?' (Market test)"
echo "   - Send WhatsApp: 'गेहूं का बजट बताओ' (Finance test)"
echo "   - Send crop image (Crop test)"
echo ""
echo "✅ Lambda configuration update complete!"
