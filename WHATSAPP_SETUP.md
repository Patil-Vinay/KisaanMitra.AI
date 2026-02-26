# WhatsApp Integration Setup

## ✅ Existing WhatsApp Lambda Function Found!

### Function Details:
- **Name**: `whatsapp-llama-bot`
- **Runtime**: Python 3.14
- **Region**: ap-south-1
- **Memory**: 128 MB
- **Timeout**: 30 seconds
- **Status**: Active ✅

### Environment Variables (Already Configured):
```bash
PHONE_NUMBER_ID="1049535664900621"
WA_TOKEN="YOUR_WHATSAPP_TOKEN"
VERIFY_TOKEN="mySecret_123"
```

## 🎯 Integration Options

### Option 1: Use Existing Function (Recommended)
Update the existing `whatsapp-llama-bot` function with KisaanMitra agents.

**Pros**:
- WhatsApp already configured
- Token already working
- No new setup needed

**Cons**:
- Need to merge code
- May have existing logic

### Option 2: Create New Function
Deploy `kisaanmitra-crop-agent` and use the same token.

**Pros**:
- Clean separation
- Keep existing bot running
- Easy rollback

**Cons**:
- Need to update WhatsApp webhook
- Two functions to maintain

### Option 3: Migrate to KisaanMitra (Best)
Replace `whatsapp-llama-bot` code with KisaanMitra agents.

**Pros**:
- Single function
- Use existing setup
- No webhook changes

**Cons**:
- Lose existing bot functionality

## 🚀 Recommended Approach: Update Existing Function

### Step 1: Backup Current Function
```bash
# Download current code
aws lambda get-function --function-name whatsapp-llama-bot --region ap-south-1 \
  --query 'Code.Location' --output text | xargs curl -o whatsapp-llama-bot-backup.zip

# Save configuration
aws lambda get-function-configuration --function-name whatsapp-llama-bot \
  --region ap-south-1 > whatsapp-llama-bot-config.json
```

### Step 2: Update Environment Variables
```bash
aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --environment "Variables={
    PHONE_NUMBER_ID=1049535664900621,
    WA_TOKEN=YOUR_WHATSAPP_TOKEN,
    VERIFY_TOKEN=mySecret_123,
    CROP_HEALTH_API_KEY=YOUR_CROP_HEALTH_API_KEY,
    CONVERSATION_TABLE=kisaanmitra-conversations,
    S3_BUCKET=kisaanmitra-images
  }" \
  --region ap-south-1
```

### Step 3: Increase Memory & Timeout
```bash
aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --memory-size 512 \
  --timeout 30 \
  --region ap-south-1
```

### Step 4: Deploy KisaanMitra Code
```bash
cd src/lambda

# Create deployment package with KisaanMitra agents
rm -rf package
mkdir package

# Install dependencies
pip3 install boto3 urllib3 -t package/

# Copy all agent code
cp ../crop_agent/crop_agent.py package/lambda_function.py
cp ../market_agent/market_agent.py package/
cp ../finance_agent/finance_agent.py package/

# Create zip
cd package
zip -r ../kisaanmitra-deployment.zip .
cd ..

# Deploy to existing function
aws lambda update-function-code \
  --function-name whatsapp-llama-bot \
  --zip-file fileb://kisaanmitra-deployment.zip \
  --region ap-south-1
```

### Step 5: Update IAM Permissions
```bash
# Get role name
ROLE_NAME=$(aws lambda get-function-configuration \
  --function-name whatsapp-llama-bot \
  --region ap-south-1 \
  --query 'Role' --output text | cut -d'/' -f2)

echo "Role: $ROLE_NAME"

# Add required permissions
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name KisaanMitraPermissions \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ],
        "Resource": "arn:aws:bedrock:ap-south-1::foundation-model/amazon.nova-micro-v1:0"
      },
      {
        "Effect": "Allow",
        "Action": [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query"
        ],
        "Resource": "arn:aws:dynamodb:ap-south-1:482548785371:table/kisaanmitra-*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject",
          "s3:PutObject"
        ],
        "Resource": "arn:aws:s3:::kisaanmitra-images/*"
      }
    ]
  }'
```

### Step 6: Test
```bash
# Test webhook verification
curl "https://<your-api-gateway-url>/webhook?hub.mode=subscribe&hub.verify_token=mySecret_123&hub.challenge=test123"

# Should return: test123

# Test with actual WhatsApp message
# Send a message to your WhatsApp Business number
```

## 📊 Current Setup Summary

### WhatsApp Configuration
- ✅ Phone Number ID: 1049535664900621
- ✅ Access Token: Configured
- ✅ Verify Token: mySecret_123
- ✅ Lambda Function: whatsapp-llama-bot (Active)

### What's Missing
- ⚠️ Bedrock permissions (need to add)
- ⚠️ DynamoDB permissions (need to add)
- ⚠️ S3 permissions (need to add)
- ⚠️ KisaanMitra agent code (need to deploy)

### What's Working
- ✅ WhatsApp webhook endpoint
- ✅ Token authentication
- ✅ Basic Lambda function

## 🎯 Quick Migration Script

```bash
#!/bin/bash
# Quick migration to KisaanMitra

FUNCTION_NAME="whatsapp-llama-bot"
REGION="ap-south-1"

echo "🚀 Migrating to KisaanMitra..."

# 1. Update environment variables
aws lambda update-function-configuration \
  --function-name $FUNCTION_NAME \
  --environment "Variables={
    PHONE_NUMBER_ID=1049535664900621,
    WHATSAPP_TOKEN=YOUR_WHATSAPP_TOKEN,
    VERIFY_TOKEN=mySecret_123,
    CROP_HEALTH_API_KEY=YOUR_CROP_HEALTH_API_KEY,
    CONVERSATION_TABLE=kisaanmitra-conversations,
    S3_BUCKET=kisaanmitra-images
  }" \
  --memory-size 512 \
  --region $REGION

# 2. Deploy code (from src/lambda directory)
cd src/lambda
./deploy_lambda.sh --function-name $FUNCTION_NAME

echo "✅ Migration complete!"
echo "🧪 Test with: ./scripts/test/test_whatsapp_integration.sh"
```

## 🔒 Security Note

**IMPORTANT**: The WhatsApp token shown above is visible in Lambda environment variables. For production:

1. Move to Secrets Manager:
```bash
aws secretsmanager create-secret \
  --name kisaanmitra/whatsapp \
  --secret-string '{"WHATSAPP_TOKEN":"YOUR_WHATSAPP_TOKEN"}' \
  --region ap-south-1
```

2. Update Lambda to read from Secrets Manager
3. Remove from environment variables

## 📝 Next Steps

1. ✅ Found existing WhatsApp setup
2. ⏳ Update environment variables
3. ⏳ Add IAM permissions
4. ⏳ Deploy KisaanMitra code
5. ⏳ Test all 3 agents
6. ⏳ Monitor CloudWatch logs

---

**Status**: Ready to migrate  
**Existing Function**: whatsapp-llama-bot  
**WhatsApp**: Already configured ✅  
**Estimated Time**: 15 minutes
