# Quick Deployment Guide

## 🚀 Deploy in 5 Minutes

### Prerequisites
- AWS CLI configured
- AWS account: 482548785371
- Region: ap-south-1

### Step 1: Infrastructure (2 min)
```bash
# Create DynamoDB tables
chmod +x infrastructure/*.sh
./infrastructure/setup_dynamodb.sh

# Update IAM permissions
./infrastructure/update_iam_permissions.sh
```

### Step 2: Deploy Market Agent (2 min)
```bash
cd src/lambda
chmod +x deploy_market_agent.sh
./deploy_market_agent.sh
```

### Step 3: Update Crop Agent (1 min)
```bash
# Copy enhanced version to Lambda
cp ../crop_agent/crop_agent_enhanced.py lambda_crop_agent.py

# Redeploy
./deploy_lambda.sh
```

### Step 4: Configure Environment
```bash
# Add to Lambda environment variables
aws lambda update-function-configuration \
  --function-name kisaanmitra-crop-agent \
  --environment "Variables={
    WHATSAPP_TOKEN=<your-token>,
    CROP_HEALTH_API_KEY=<your-key>,
    CONVERSATION_TABLE=kisaanmitra-conversations
  }" \
  --region ap-south-1
```

### Step 5: Test
```bash
# Test crop agent
./test_whatsapp_integration.sh

# Test market agent
./test_market_agent.sh
```

## ✅ Done!

Both agents deployed and ready for WhatsApp integration.

## 🔗 Next: Setup WhatsApp Webhook
1. Get Lambda function URL
2. Configure in Meta Business
3. Verify webhook
4. Start testing!
