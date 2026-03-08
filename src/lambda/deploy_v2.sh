#!/bin/bash

echo "🚀 Deploying KisaanMitra WhatsApp Lambda - Microservice Architecture v2.0..."

# Clean up old package
rm -f whatsapp_deployment.zip

# Create deployment package
echo "📦 Creating deployment package..."
zip -r whatsapp_deployment.zip \
    lambda_handler_v2.py \
    lambda_handler_web.py \
    lambda_handler_unified.py \
    services/ \
    agents/ \
    anthropic_client.py \
    whatsapp_interactive.py \
    navigation_controller.py \
    user_state_manager.py \
    weather_service.py \
    reminder_manager.py \
    market_data_sources.py \
    price_forecasting.py \
    enhanced_disease_detection.py \
    knowledge_graph_helper.py \
    crop_yield_database.py \
    ai_orchestrator.py \
    -x "*.pyc" -x "*__pycache__*" -x "*.git*"

# Include onboarding module
echo "📦 Including onboarding module..."
cd ../onboarding
zip -r ../lambda/whatsapp_deployment.zip . -x "*.pyc" -x "*__pycache__*"
cd ../lambda

# Include hyperlocal module
echo "📦 Including hyperlocal module..."
cd ../hyperlocal
zip -r ../lambda/whatsapp_deployment.zip . -x "*.pyc" -x "*__pycache__*"
cd ../lambda

# Include knowledge graph demo data
echo "📊 Including knowledge graph demo data..."
cd ../../demo
zip -j ../src/lambda/whatsapp_deployment.zip knowledge_graph_dummy_data.json
cd ../src/lambda

echo "✅ Package created"

# Deploy to Lambda
echo "🚀 Deploying to Lambda..."
aws lambda update-function-code \
    --function-name whatsapp-llama-bot \
    --zip-file fileb://whatsapp_deployment.zip \
    --region ap-south-1

# Wait for update to complete
echo "⏳ Waiting for update to complete..."
aws lambda wait function-updated \
    --function-name whatsapp-llama-bot \
    --region ap-south-1

# Update handler configuration
echo "🔧 Updating handler configuration..."
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --handler lambda_handler_unified.lambda_handler \
    --description "Unified Handler (WhatsApp + Web) - $(date '+%Y-%m-%d %H:%M')" \
    --region ap-south-1

# Wait for configuration update
echo "⏳ Waiting for configuration update..."
aws lambda wait function-updated \
    --function-name whatsapp-llama-bot \
    --region ap-south-1

echo "✅ Deployment complete!"
echo ""
echo "🧪 Test with:"
echo "   Send WhatsApp message to your number"
echo ""
echo "📊 View logs:"
echo "   aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1"
echo ""
echo "🔄 To rollback to old handler:"
echo "   aws lambda update-function-configuration --function-name whatsapp-llama-bot --handler lambda_whatsapp_kisaanmitra.lambda_handler --region ap-south-1"
