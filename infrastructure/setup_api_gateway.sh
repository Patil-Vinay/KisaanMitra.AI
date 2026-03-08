#!/bin/bash

echo "🚀 Setting up API Gateway for KisaanMitra Web Demo..."

# Configuration
LAMBDA_FUNCTION="whatsapp-llama-bot"
API_NAME="kisaanmitra-web-demo"
REGION="ap-south-1"
STAGE_NAME="prod"

# Create REST API
echo "📡 Creating REST API..."
API_ID=$(aws apigateway create-rest-api \
    --name "$API_NAME" \
    --description "KisaanMitra Web Demo API for AWS AI Challenge" \
    --region $REGION \
    --endpoint-configuration types=REGIONAL \
    --query 'id' \
    --output text)

if [ -z "$API_ID" ]; then
    echo "❌ Failed to create API"
    exit 1
fi

echo "✅ API created: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region $REGION \
    --query 'items[0].id' \
    --output text)

echo "📁 Root resource: $ROOT_ID"

# Create /chat resource
echo "📁 Creating /chat resource..."
CHAT_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part chat \
    --region $REGION \
    --query 'id' \
    --output text)

echo "✅ Chat resource created: $CHAT_RESOURCE_ID"

# Create POST method
echo "🔧 Creating POST method..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region $REGION

# Create OPTIONS method for CORS
echo "🔧 Creating OPTIONS method for CORS..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --region $REGION

# Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name $LAMBDA_FUNCTION \
    --region $REGION \
    --query 'Configuration.FunctionArn' \
    --output text)

echo "🔗 Lambda ARN: $LAMBDA_ARN"

# Set up Lambda integration for POST
echo "🔗 Setting up Lambda integration..."
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
    --region $REGION

# Set up mock integration for OPTIONS (CORS)
echo "🔗 Setting up CORS integration..."
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}' \
    --region $REGION

# Set up OPTIONS method response
aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": false, "method.response.header.Access-Control-Allow-Methods": false, "method.response.header.Access-Control-Allow-Origin": false}' \
    --region $REGION

# Set up OPTIONS integration response
aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $CHAT_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": "'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'", "method.response.header.Access-Control-Allow-Methods": "'"'"'POST,OPTIONS'"'"'", "method.response.header.Access-Control-Allow-Origin": "'"'"'*'"'"'"}' \
    --region $REGION

# Grant API Gateway permission to invoke Lambda
echo "🔐 Granting API Gateway permission..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws lambda add-permission \
    --function-name $LAMBDA_FUNCTION \
    --statement-id apigateway-web-demo-$(date +%s) \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*/chat" \
    --region $REGION 2>/dev/null || echo "Permission may already exist"

# Deploy API
echo "🚀 Deploying API to $STAGE_NAME stage..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name $STAGE_NAME \
    --description "Initial deployment for web demo" \
    --region $REGION

# Get API endpoint
API_ENDPOINT="https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE_NAME/chat"

echo ""
echo "=========================================="
echo "✅ API Gateway Setup Complete!"
echo "=========================================="
echo ""
echo "API Endpoint:"
echo "  $API_ENDPOINT"
echo ""
echo "Next Steps:"
echo "1. Update demo/web-chat-demo.html with this endpoint:"
echo "   const API_ENDPOINT = '$API_ENDPOINT';"
echo ""
echo "2. Deploy Lambda handler for web:"
echo "   cd src/lambda && ./deploy_web_handler.sh"
echo ""
echo "3. Upload web-chat-demo.html to S3:"
echo "   aws s3 cp demo/web-chat-demo.html s3://YOUR-BUCKET/index.html --acl public-read"
echo ""
echo "Test the API:"
echo "  curl -X POST $API_ENDPOINT \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"user_id\":\"test\",\"type\":\"text\",\"message\":\"Hi\",\"language\":\"english\"}'"
echo ""
