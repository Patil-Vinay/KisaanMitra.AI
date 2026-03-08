#!/bin/bash

# Deploy Price Forecasting Integration to WhatsApp Lambda
# Updates the main Lambda function with price forecasting capabilities

set -e

REGION="ap-south-1"
LAMBDA_FUNCTION="whatsapp-llama-bot"
DYNAMODB_TABLE="kisaanmitra-price-forecasts"
S3_BUCKET="kisaanmitra-price-data"

echo "🚀 Deploying Price Forecasting Integration"
echo "=" * 60

# 1. Package Lambda code
echo "📦 Packaging Lambda code..."
cd src/lambda

# Create deployment package
rm -f whatsapp_deployment.zip
zip -q whatsapp_deployment.zip \
    lambda_whatsapp_kisaanmitra.py \
    knowledge_graph_helper.py \
    anthropic_client.py \
    whatsapp_interactive.py \
    navigation_controller.py \
    user_state_manager.py

echo "✅ Core files packaged"

# Add onboarding module
cd ..
zip -r -q lambda/whatsapp_deployment.zip onboarding/__init__.py onboarding/farmer_onboarding.py

echo "✅ Onboarding module added"

cd lambda

# 2. Update Lambda function code
echo "⚡ Updating Lambda function code..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION \
    --zip-file fileb://whatsapp_deployment.zip \
    --region $REGION \
    --no-cli-pager

echo "✅ Code updated"

# 3. Wait for update to complete
echo "⏳ Waiting for update to complete..."
aws lambda wait function-updated --function-name $LAMBDA_FUNCTION --region $REGION

# 4. Update environment variables
echo "🔧 Updating environment variables..."

# Get existing environment variables
EXISTING_VARS=$(aws lambda get-function-configuration \
    --function-name $LAMBDA_FUNCTION \
    --region $REGION \
    --query 'Environment.Variables' \
    --output json)

# Add new variables
UPDATED_VARS=$(echo $EXISTING_VARS | jq \
    --arg table "$DYNAMODB_TABLE" \
    --arg bucket "$S3_BUCKET" \
    '. + {PRICE_FORECAST_TABLE: $table, S3_BUCKET: $bucket}')

# Update Lambda configuration
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION \
    --environment "Variables=$UPDATED_VARS" \
    --region $REGION \
    --no-cli-pager

echo "✅ Environment variables updated"

# 5. Wait for configuration update
echo "⏳ Waiting for configuration update..."
aws lambda wait function-updated --function-name $LAMBDA_FUNCTION --region $REGION

# 6. Test the deployment
echo "🧪 Testing deployment..."
echo ""
echo "Test queries to try:"
echo "  - 'What is onion price today?'"
echo "  - 'Tomorrow wheat price'"
echo "  - 'Week forecast for rice'"
echo "  - 'Cotton price' (should show only 5 crops supported)"
echo ""

# 7. View recent logs
echo "📋 Recent logs:"
aws logs tail /aws/lambda/$LAMBDA_FUNCTION --since 5m --region $REGION --format short | head -20

echo ""
echo "=" * 60
echo "✅ Deployment Complete!"
echo "=" * 60
echo ""
echo "📊 Price Forecasting Integration:"
echo "  - DynamoDB Table: $DYNAMODB_TABLE"
echo "  - S3 Bucket: $S3_BUCKET"
echo "  - Supported Crops: Onion, Rice, Sugarcane, Tomato, Wheat"
echo ""
echo "🔧 Next Steps:"
echo "  1. Test with WhatsApp: 'What is onion price today?'"
echo "  2. View logs: aws logs tail /aws/lambda/$LAMBDA_FUNCTION --follow --region $REGION"
echo "  3. Monitor DynamoDB: aws dynamodb scan --table-name $DYNAMODB_TABLE --region $REGION"
echo ""
echo "📚 Documentation:"
echo "  - AWS_PRICE_FORECASTING_COMPLETE.md"
echo "  - PRICE_FORECASTING_AWS_SUMMARY.md"
