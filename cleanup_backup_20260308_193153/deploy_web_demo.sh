#!/bin/bash

echo "🌐 KisaanMitra Web Demo - Complete Deployment"
echo "=============================================="
echo ""

# Step 1: Set up API Gateway
echo "📡 Step 1/4: Setting up API Gateway..."
./infrastructure/setup_api_gateway.sh

# Get API endpoint
API_ID=$(aws apigateway get-rest-apis \
    --query 'items[?name==`kisaanmitra-web-demo`].id' \
    --output text \
    --region ap-south-1)

if [ -z "$API_ID" ]; then
    echo "❌ Failed to get API ID"
    exit 1
fi

API_ENDPOINT="https://$API_ID.execute-api.ap-south-1.amazonaws.com/prod/chat"
echo "✅ API Endpoint: $API_ENDPOINT"
echo ""

# Step 2: Update HTML with API endpoint
echo "📝 Step 2/4: Updating web interface with API endpoint..."
sed -i.bak "s|YOUR_API_GATEWAY_URL_HERE|$API_ENDPOINT|g" demo/web-chat-demo.html
echo "✅ Web interface updated"
echo ""

# Step 3: Deploy web handler
echo "🚀 Step 3/4: Deploying web handler to Lambda..."
cd src/lambda
./deploy_web_handler.sh
cd ../..
echo ""

# Step 4: Switch Lambda to web handler
echo "🔄 Step 4/4: Switching Lambda to web handler..."
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --handler lambda_handler_web.lambda_handler \
    --region ap-south-1 \
    --output json | jq -r '"Handler:", .Handler'

aws lambda wait function-updated \
    --function-name whatsapp-llama-bot \
    --region ap-south-1

echo "✅ Lambda handler switched"
echo ""

# Step 5: Deploy to S3
echo "📤 Step 5/5: Deploying web interface to S3..."
BUCKET_NAME="kisaanmitra-web-demo-$(date +%s)"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region ap-south-1

# Enable static website hosting
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html

# Make bucket public
aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [{
            \"Sid\": \"PublicReadGetObject\",
            \"Effect\": \"Allow\",
            \"Principal\": \"*\",
            \"Action\": \"s3:GetObject\",
            \"Resource\": \"arn:aws:s3:::$BUCKET_NAME/*\"
        }]
    }"

# Upload web interface
aws s3 cp demo/web-chat-demo.html s3://$BUCKET_NAME/index.html \
    --content-type "text/html"

WEBSITE_URL="http://$BUCKET_NAME.s3-website.ap-south-1.amazonaws.com"

echo "✅ Web interface deployed"
echo ""

# Summary
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Web Demo URL:"
echo "   $WEBSITE_URL"
echo ""
echo "📡 API Endpoint:"
echo "   $API_ENDPOINT"
echo ""
echo "📊 Other Demo Links:"
echo "   Knowledge Graph: http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com"
echo ""
echo "🧪 Test the API:"
echo "   curl -X POST $API_ENDPOINT \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"user_id\":\"test\",\"type\":\"text\",\"message\":\"Hi\",\"language\":\"english\"}'"
echo ""
echo "📱 Share with evaluators:"
echo "   $WEBSITE_URL"
echo ""
echo "🔄 To switch back to WhatsApp mode:"
echo "   aws lambda update-function-configuration \\"
echo "     --function-name whatsapp-llama-bot \\"
echo "     --handler lambda_handler_v2.lambda_handler \\"
echo "     --region ap-south-1"
echo ""
echo "📖 Full documentation: WEB_DEMO_DEPLOYMENT.md"
echo ""
