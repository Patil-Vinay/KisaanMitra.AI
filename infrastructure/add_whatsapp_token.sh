#!/bin/bash

# Add WhatsApp Token to AWS Secrets Manager

set -e

REGION="ap-south-1"

echo "🔐 Adding WhatsApp Token to AWS"
echo "================================"
echo ""

# Check if secret exists
SECRET_EXISTS=$(aws secretsmanager list-secrets --region $REGION --query "SecretList[?Name=='kisaanmitra/whatsapp'].Name" --output text)

if [ -z "$SECRET_EXISTS" ]; then
    echo "📝 Please enter your WhatsApp Business API Token:"
    read -s WHATSAPP_TOKEN
    echo ""
    
    if [ -z "$WHATSAPP_TOKEN" ]; then
        echo "❌ Error: Token cannot be empty"
        exit 1
    fi
    
    echo "Creating new secret..."
    aws secretsmanager create-secret \
        --name kisaanmitra/whatsapp \
        --description "WhatsApp Business API credentials for KisaanMitra" \
        --secret-string "{\"WHATSAPP_TOKEN\":\"$WHATSAPP_TOKEN\",\"PHONE_NUMBER_ID\":\"1049535664900621\",\"VERIFY_TOKEN\":\"mySecret_123\"}" \
        --region $REGION
    
    echo "✅ Secret created successfully!"
else
    echo "Secret already exists. Updating..."
    echo "📝 Please enter your WhatsApp Business API Token:"
    read -s WHATSAPP_TOKEN
    echo ""
    
    if [ -z "$WHATSAPP_TOKEN" ]; then
        echo "❌ Error: Token cannot be empty"
        exit 1
    fi
    
    aws secretsmanager update-secret \
        --secret-id kisaanmitra/whatsapp \
        --secret-string "{\"WHATSAPP_TOKEN\":\"$WHATSAPP_TOKEN\",\"PHONE_NUMBER_ID\":\"1049535664900621\",\"VERIFY_TOKEN\":\"mySecret_123\"}" \
        --region $REGION
    
    echo "✅ Secret updated successfully!"
fi

echo ""
echo "🔧 Updating Lambda environment variables..."

# Update Crop Agent Lambda
aws lambda update-function-configuration \
    --function-name kisaanmitra-crop-agent \
    --environment "Variables={S3_BUCKET=kisaanmitra-images,SECRET_NAME=kisaanmitra/crop-health-api,WHATSAPP_SECRET_NAME=kisaanmitra/whatsapp,CONVERSATION_TABLE=kisaanmitra-conversations}" \
    --region $REGION \
    2>/dev/null || echo "Crop agent not found or already configured"

echo ""
echo "✅ Configuration Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Update Lambda IAM role to allow reading the new secret:"
echo "      aws iam put-role-policy \\"
echo "        --role-name kisaanmitra-lambda-role \\"
echo "        --policy-name WhatsAppSecretAccess \\"
echo "        --policy-document file://whatsapp-secret-policy.json"
echo ""
echo "   2. Update your Lambda code to read from Secrets Manager:"
echo "      secret = boto3.client('secretsmanager').get_secret_value(SecretId='kisaanmitra/whatsapp')"
echo "      WHATSAPP_TOKEN = json.loads(secret['SecretString'])['WHATSAPP_TOKEN']"
echo ""
echo "   3. Configure WhatsApp webhook URL in Meta Business:"
echo "      Webhook URL: https://<your-api-gateway-url>/webhook"
echo "      Verify Token: mySecret_123"
echo ""
echo "🔍 Verify secret:"
echo "   aws secretsmanager get-secret-value --secret-id kisaanmitra/whatsapp --region $REGION"
