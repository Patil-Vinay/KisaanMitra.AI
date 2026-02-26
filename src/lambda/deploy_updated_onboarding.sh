#!/bin/bash

# Deploy Updated Lambda with Enhanced Onboarding Check
# This script deploys the updated Lambda that ALWAYS checks for new users first

echo "🚀 Deploying Updated KisaanMitra Lambda with Enhanced Onboarding..."

# Configuration
FUNCTION_NAME="kisaanmitra-whatsapp"
REGION="ap-south-1"

# Create deployment package directory
rm -rf package
mkdir -p package

# Install dependencies
echo "📦 Installing dependencies..."
pip install \
    boto3 \
    urllib3 \
    langgraph \
    gremlinpython \
    -t package/ -q

# Copy source files
echo "📄 Copying source files..."
cp lambda_whatsapp_kisaanmitra.py package/
cp agent_router.py package/
cp market_data_sources.py package/ 2>/dev/null || echo "market_data_sources.py not found, skipping"

# Copy onboarding module
echo "📋 Copying onboarding module..."
mkdir -p package/onboarding
cp ../onboarding/farmer_onboarding.py package/onboarding/
touch package/onboarding/__init__.py

# Copy knowledge graph module
echo "🕸️ Copying knowledge graph module..."
mkdir -p package/knowledge_graph
cp ../knowledge_graph/village_graph.py package/knowledge_graph/
touch package/knowledge_graph/__init__.py

# Create deployment package
echo "📦 Creating deployment package..."
cd package
zip -r ../lambda_deployment.zip . -q
cd ..

# Check package size
PACKAGE_SIZE=$(du -h lambda_deployment.zip | cut -f1)
echo "📊 Package size: $PACKAGE_SIZE"

# Upload to Lambda
echo "☁️ Uploading to Lambda..."
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda_deployment.zip \
    --region $REGION

# Wait for update to complete
echo "⏳ Waiting for Lambda update..."
aws lambda wait function-updated \
    --function-name $FUNCTION_NAME \
    --region $REGION

# Update timeout and memory (if needed)
echo "⚙️ Updating Lambda configuration..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 60 \
    --memory-size 1024 \
    --region $REGION \
    2>/dev/null || echo "Configuration already up to date"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Summary:"
echo "  Function: $FUNCTION_NAME"
echo "  Region: $REGION"
echo "  Package: $PACKAGE_SIZE"
echo ""
echo "🔍 Key Changes:"
echo "  ✅ ALWAYS checks if user is new (first priority)"
echo "  ✅ Blocks non-text messages during onboarding"
echo "  ✅ Enhanced logging with emojis"
echo "  ✅ Helper function: check_user_status()"
echo ""
echo "📝 Next steps:"
echo "  1. Test with new user: Send 'Hi' to WhatsApp"
echo "  2. Monitor logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo "  3. Verify onboarding flow completes"
echo "  4. Check DynamoDB: kisaanmitra-user-profiles"
echo "  5. View dashboard: cd ../../dashboard && ./run_dashboard.sh"
echo ""
echo "🎉 Ready to onboard farmers!"
