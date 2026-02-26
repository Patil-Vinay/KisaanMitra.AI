#!/bin/bash

# Deploy Finance Agent Lambda

set -e

REGION="ap-south-1"
FUNCTION_NAME="kisaanmitra-finance-agent"
ROLE_ARN="arn:aws:iam::482548785371:role/kisaanmitra-lambda-role"

echo "💰 Deploying Finance Agent Lambda..."
echo "====================================="
echo ""

cd "$(dirname "$0")"

# Clean previous package
rm -rf package_finance
rm -f finance_deployment.zip

# Create package
mkdir -p package_finance

# Install dependencies
pip3 install \
  boto3 \
  urllib3 \
  -t package_finance/ \
  --quiet

# Copy finance agent code
cp ../finance_agent/finance_agent.py package_finance/

# Create zip
cd package_finance
zip -r ../finance_deployment.zip . -q
cd ..

echo "✓ Package created"
echo ""

# Deploy
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
  echo "Updating existing function..."
  aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://finance_deployment.zip \
    --region $REGION
  
  aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 30 \
    --memory-size 512 \
    --environment "Variables={FINANCE_TABLE=kisaanmitra-finance,SCHEMES_TABLE=kisaanmitra-schemes,BUDGET_BUCKET=kisaanmitra-budgets}" \
    --region $REGION
else
  echo "Creating new function..."
  aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.11 \
    --role $ROLE_ARN \
    --handler finance_agent.lambda_handler \
    --zip-file fileb://finance_deployment.zip \
    --timeout 30 \
    --memory-size 512 \
    --environment "Variables={FINANCE_TABLE=kisaanmitra-finance,SCHEMES_TABLE=kisaanmitra-schemes,BUDGET_BUCKET=kisaanmitra-budgets}" \
    --region $REGION
fi

echo ""
echo "✅ Finance Agent deployed!"
echo ""
echo "🧪 Test command:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"body\":\"{\\\"type\\\":\\\"budget_plan\\\",\\\"crop\\\":\\\"wheat\\\",\\\"land_size\\\":2,\\\"income\\\":50000}\"}' --region $REGION response.json"
