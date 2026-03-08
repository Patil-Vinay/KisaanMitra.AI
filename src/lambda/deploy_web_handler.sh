#!/bin/bash

echo "🚀 Deploying KisaanMitra Web Handler..."

# Clean up old package
rm -f web_handler_deployment.zip

# Create deployment package with web handler
echo "📦 Creating deployment package..."
zip -r web_handler_deployment.zip \
    lambda_handler_web.py \
    services/ \
    agents/ \
    anthropic_client.py \
    market_data_sources.py \
    price_forecasting.py \
    enhanced_disease_detection.py \
    knowledge_graph_helper.py \
    crop_yield_database.py \
    ai_orchestrator.py \
    -x "*.pyc" -x "*__pycache__*" -x "*.git*" -q

# Include onboarding module
cd ../onboarding
zip -j ../lambda/web_handler_deployment.zip *.py -q
cd ../lambda

# Include hyperlocal module
cd ../hyperlocal
zip -j ../lambda/web_handler_deployment.zip *.py -q
cd ../lambda

# Include knowledge graph demo data
cd ../../demo
zip -j ../src/lambda/web_handler_deployment.zip knowledge_graph_dummy_data.json -q
cd ../src/lambda

echo "✅ Package created"

# Update Lambda function code
echo "🚀 Updating Lambda function..."
aws lambda update-function-code \
    --function-name whatsapp-llama-bot \
    --zip-file fileb://web_handler_deployment.zip \
    --region ap-south-1 \
    --output json | jq -r '"Code Size:", (.CodeSize|tostring) + " bytes"'

# Wait for update to complete
echo "⏳ Waiting for update..."
aws lambda wait function-updated \
    --function-name whatsapp-llama-bot \
    --region ap-south-1

echo "✅ Deployment complete!"
echo ""
echo "The Lambda function now supports both:"
echo "  • WhatsApp webhook (lambda_handler_v2.lambda_handler)"
echo "  • Web API Gateway (lambda_handler_web.lambda_handler)"
echo ""
echo "To switch handlers:"
echo "  # For WhatsApp:"
echo "  aws lambda update-function-configuration --function-name whatsapp-llama-bot --handler lambda_handler_v2.lambda_handler --region ap-south-1"
echo ""
echo "  # For Web Demo:"
echo "  aws lambda update-function-configuration --function-name whatsapp-llama-bot --handler lambda_handler_web.lambda_handler --region ap-south-1"
echo ""
