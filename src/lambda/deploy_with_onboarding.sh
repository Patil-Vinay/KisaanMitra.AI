#!/bin/bash

# Deploy Lambda with Onboarding and Knowledge Graph support
# This script packages and deploys the enhanced Lambda function

echo "📦 Deploying KisaanMitra Lambda with Onboarding..."

# Configuration
FUNCTION_NAME="kisaanmitra-whatsapp"
REGION="ap-south-1"
RUNTIME="python3.11"
HANDLER="lambda_whatsapp_kisaanmitra.lambda_handler"
ROLE_ARN="arn:aws:iam::482548785371:role/lambda-kisaanmitra-role"

# Create deployment package directory
rm -rf package
mkdir -p package

# Install dependencies
echo "Installing dependencies..."
pip install \
    boto3 \
    urllib3 \
    langgraph \
    gremlinpython \
    -t package/

# Copy source files
echo "Copying source files..."
cp lambda_whatsapp_kisaanmitra.py package/
cp agent_router.py package/
cp market_data_sources.py package/

# Copy onboarding module
mkdir -p package/onboarding
cp ../onboarding/farmer_onboarding.py package/onboarding/
touch package/onboarding/__init__.py

# Copy knowledge graph module
mkdir -p package/knowledge_graph
cp ../knowledge_graph/village_graph.py package/knowledge_graph/
touch package/knowledge_graph/__init__.py

# Create deployment package
echo "Creating deployment package..."
cd package
zip -r ../lambda_deployment.zip . -q
cd ..

# Check package size
PACKAGE_SIZE=$(du -h lambda_deployment.zip | cut -f1)
echo "Package size: $PACKAGE_SIZE"

# Upload to Lambda
echo "Uploading to Lambda..."
aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://lambda_deployment.zip \
    --region $REGION

# Wait for update to complete
echo "Waiting for Lambda update..."
aws lambda wait function-updated \
    --function-name $FUNCTION_NAME \
    --region $REGION

# Update environment variables
echo "Updating environment variables..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --environment "Variables={
        VERIFY_TOKEN=mySecret_123,
        WHATSAPP_TOKEN=$WHATSAPP_TOKEN,
        PHONE_NUMBER_ID=$PHONE_NUMBER_ID,
        CROP_HEALTH_API_KEY=$CROP_HEALTH_API_KEY,
        AGMARKNET_API_KEY=$AGMARKNET_API_KEY,
        NEPTUNE_ENDPOINT=$NEPTUNE_ENDPOINT,
        ONBOARDING_TABLE=kisaanmitra-onboarding,
        USER_PROFILE_TABLE=kisaanmitra-user-profiles
    }" \
    --region $REGION

# Update timeout and memory
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 60 \
    --memory-size 1024 \
    --region $REGION

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Function: $FUNCTION_NAME"
echo "Region: $REGION"
echo "Package: $PACKAGE_SIZE"
echo ""
echo "Next steps:"
echo "  1. Test onboarding: Send 'Hi' to WhatsApp"
echo "  2. View dashboard: cd ../../dashboard && ./run_dashboard.sh"
echo "  3. Monitor logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
