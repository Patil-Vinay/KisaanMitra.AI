#!/bin/bash

# Deploy Market Agent Lambda function

set -e

REGION="ap-south-1"
FUNCTION_NAME="kisaanmitra-market-agent"
ROLE_ARN="arn:aws:iam::482548785371:role/kisaanmitra-lambda-role"

echo "📦 Deploying Market Agent Lambda..."
echo "===================================="
echo ""

# Create deployment package
echo "1️⃣ Creating deployment package..."
cd "$(dirname "$0")"

# Clean previous package
rm -rf package_market
rm -f market_deployment.zip

# Create package directory
mkdir -p package_market

# Install dependencies
pip3 install \
  boto3 \
  urllib3 \
  -t package_market/ \
  --quiet

# Copy market agent code
cp ../market_agent/market_agent.py package_market/

# Create zip
cd package_market
zip -r ../market_deployment.zip . -q
cd ..

echo "✓ Package created: market_deployment.zip"
echo ""

# Check if function exists
echo "2️⃣ Checking if function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
  echo "Function exists, updating code..."
  aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://market_deployment.zip \
    --region $REGION
  
  echo ""
  echo "Updating configuration..."
  aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 30 \
    --memory-size 512 \
    --environment "Variables={MARKET_DATA_TABLE=kisaanmitra-market-data}" \
    --region $REGION
else
  echo "Creating new function..."
  aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.11 \
    --role $ROLE_ARN \
    --handler market_agent.lambda_handler \
    --zip-file fileb://market_deployment.zip \
    --timeout 30 \
    --memory-size 512 \
    --environment "Variables={MARKET_DATA_TABLE=kisaanmitra-market-data}" \
    --region $REGION
fi

echo ""
echo "✅ Market Agent deployed successfully!"
echo ""
echo "📋 Function details:"
echo "   Name: $FUNCTION_NAME"
echo "   Region: $REGION"
echo "   Runtime: Python 3.11"
echo "   Handler: market_agent.lambda_handler"
echo ""
echo "🧪 Test the function:"
echo "   aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"body\":\"{\\\"type\\\":\\\"price_check\\\",\\\"crop\\\":\\\"wheat\\\"}\"}' --region $REGION response.json"
