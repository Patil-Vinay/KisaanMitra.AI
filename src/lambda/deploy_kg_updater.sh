#!/bin/bash

# Deploy Knowledge Graph Updater Lambda
# This Lambda updates the KG dashboard data every 5 minutes

set -e

FUNCTION_NAME="kisaanmitra-kg-updater"
REGION="ap-south-1"
ROLE_ARN="arn:aws:iam::482548785371:role/service-role/whatsapp-llama-bot-role-9t42wmrl"

echo "🚀 Deploying KG Updater Lambda..."

# Create deployment package
echo "📦 Creating deployment package..."
zip -j kg_updater.zip lambda_kg_updater.py

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "♻️  Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://kg_updater.zip \
        --region $REGION
    
    echo "⚙️  Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 60 \
        --memory-size 512 \
        --region $REGION
else
    echo "🆕 Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_kg_updater.lambda_handler \
        --zip-file fileb://kg_updater.zip \
        --timeout 60 \
        --memory-size 512 \
        --region $REGION
fi

# Create EventBridge rule to trigger every 5 minutes
echo "⏰ Setting up EventBridge rule..."

RULE_NAME="kg-updater-schedule"

# Create or update rule
aws events put-rule \
    --name $RULE_NAME \
    --schedule-expression "rate(5 minutes)" \
    --state ENABLED \
    --region $REGION

# Add Lambda permission for EventBridge
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id EventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:$REGION:$(aws sts get-caller-identity --query Account --output text):rule/$RULE_NAME" \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Add target to rule
aws events put-targets \
    --rule $RULE_NAME \
    --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:$FUNCTION_NAME" \
    --region $REGION

# Cleanup
rm kg_updater.zip

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Knowledge Graph Updater Lambda deployed successfully"
echo "🔄 Updates every 5 minutes automatically"
echo "📍 Function: $FUNCTION_NAME"
echo "⏰ Schedule: Every 5 minutes"
echo ""
echo "🧪 Test the function:"
echo "aws lambda invoke --function-name $FUNCTION_NAME --region $REGION response.json"
echo ""
echo "📈 View logs:"
echo "aws logs tail /aws/lambda/$FUNCTION_NAME --follow --region $REGION"
