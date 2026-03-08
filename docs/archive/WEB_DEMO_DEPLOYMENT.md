# 🌐 KisaanMitra Web Demo - Complete Deployment Guide

## Overview

This guide will help you deploy a web-based demo of KisaanMitra for AWS AI Challenge evaluators. The demo provides instant access without requiring WhatsApp numbers.

## Architecture

```
Evaluator Browser
    ↓
S3 Static Website (HTML/JS/CSS)
    ↓
API Gateway (REST API)
    ↓
Lambda Function (Web Handler)
    ↓
AWS Bedrock + DynamoDB
```

## 🚀 Quick Deployment (15 minutes)

### Step 1: Set up API Gateway

```bash
chmod +x infrastructure/setup_api_gateway.sh
./infrastructure/setup_api_gateway.sh
```

This will:
- Create REST API in API Gateway
- Set up /chat endpoint
- Configure CORS
- Grant Lambda permissions
- Deploy to production stage

**Output:** You'll get an API endpoint URL like:
```
https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod/chat
```

### Step 2: Update Web Chat Interface

Edit `demo/web-chat-demo.html` and replace:

```javascript
const API_ENDPOINT = 'YOUR_API_GATEWAY_URL_HERE';
```

With your actual API Gateway URL from Step 1.

### Step 3: Deploy Web Handler to Lambda

```bash
cd src/lambda
chmod +x deploy_web_handler.sh
./deploy_web_handler.sh
```

### Step 4: Switch Lambda Handler to Web Mode

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --handler lambda_handler_web.lambda_handler \
    --region ap-south-1
```

### Step 5: Deploy Web Interface to S3

#### Option A: Create New S3 Bucket

```bash
# Create bucket
BUCKET_NAME="kisaanmitra-web-demo-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region ap-south-1

# Enable static website hosting
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html

# Upload web chat interface
aws s3 cp demo/web-chat-demo.html s3://$BUCKET_NAME/index.html \
    --acl public-read \
    --content-type "text/html"

# Get website URL
echo "Website URL: http://$BUCKET_NAME.s3-website.ap-south-1.amazonaws.com"
```

#### Option B: Use Existing Bucket

```bash
# Upload to existing bucket
aws s3 cp demo/web-chat-demo.html s3://YOUR-EXISTING-BUCKET/chat.html \
    --acl public-read \
    --content-type "text/html"
```

### Step 6: Test the Demo

Open the S3 website URL in your browser and try:

1. **Text Messages:**
   - "Hi"
   - "What is the current price of tomato?"
   - "Budget planning for wheat in 10 acres"
   - "Weather forecast"

2. **Image Upload:**
   - Click the 📎 icon
   - Upload a crop disease image
   - Get AI-powered diagnosis

## 🔄 Switching Between WhatsApp and Web Demo

### Switch to Web Demo Mode

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --handler lambda_handler_web.lambda_handler \
    --region ap-south-1
```

### Switch Back to WhatsApp Mode

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --handler lambda_handler_v2.lambda_handler \
    --region ap-south-1
```

## 🎨 Customization

### Change Colors

Edit `demo/web-chat-demo.html`:

```css
/* Header gradient */
background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);

/* Send button */
background: #25D366;
```

### Add Your Logo

Replace the header icon:

```html
<div class="header-icon">🌾</div>
```

With:

```html
<div class="header-icon">
    <img src="your-logo.png" alt="Logo" style="width: 100%; height: 100%; object-fit: cover;">
</div>
```

### Modify Quick Actions

Edit the quick action buttons:

```html
<button class="quick-btn" onclick="sendQuickMessage('Your custom message')">
    🎯 Your Action
</button>
```

## 📊 Monitoring

### Check API Gateway Logs

```bash
# Get API ID
API_ID=$(aws apigateway get-rest-apis \
    --query 'items[?name==`kisaanmitra-web-demo`].id' \
    --output text \
    --region ap-south-1)

# View logs
aws logs tail /aws/apigateway/$API_ID --follow --region ap-south-1
```

### Check Lambda Logs

```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

### Monitor Usage

```bash
# API Gateway requests
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApiGateway \
    --metric-name Count \
    --dimensions Name=ApiName,Value=kisaanmitra-web-demo \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum \
    --region ap-south-1
```

## 🔐 Security Best Practices

### 1. Add API Key (Optional)

```bash
# Create API key
aws apigateway create-api-key \
    --name kisaanmitra-demo-key \
    --enabled \
    --region ap-south-1

# Create usage plan
aws apigateway create-usage-plan \
    --name kisaanmitra-demo-plan \
    --throttle burstLimit=100,rateLimit=50 \
    --quota limit=10000,period=DAY \
    --region ap-south-1
```

### 2. Enable CloudFront (Recommended)

```bash
# Create CloudFront distribution for S3
aws cloudfront create-distribution \
    --origin-domain-name $BUCKET_NAME.s3.ap-south-1.amazonaws.com \
    --default-root-object index.html
```

### 3. Add WAF Rules (Optional)

```bash
# Create WAF web ACL
aws wafv2 create-web-acl \
    --name kisaanmitra-waf \
    --scope REGIONAL \
    --default-action Allow={} \
    --region ap-south-1
```

## 💰 Cost Estimation

### Monthly Costs (Assuming 1000 demo sessions)

- **API Gateway:** ~$3.50 (1M requests free tier)
- **Lambda:** ~$0.20 (1M requests free tier)
- **S3:** ~$0.50 (hosting + data transfer)
- **Bedrock:** ~$10-20 (based on usage)
- **DynamoDB:** ~$1 (25GB free tier)

**Total:** ~$15-25/month

## 🐛 Troubleshooting

### Issue: CORS Error

**Solution:** Ensure OPTIONS method is configured:

```bash
aws apigateway put-method \
    --rest-api-id YOUR_API_ID \
    --resource-id YOUR_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --region ap-south-1
```

### Issue: 403 Forbidden

**Solution:** Check Lambda permissions:

```bash
aws lambda get-policy \
    --function-name whatsapp-llama-bot \
    --region ap-south-1
```

### Issue: Timeout

**Solution:** Increase Lambda timeout:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --timeout 120 \
    --region ap-south-1
```

### Issue: No Response

**Solution:** Check Lambda handler is set correctly:

```bash
aws lambda get-function-configuration \
    --function-name whatsapp-llama-bot \
    --region ap-south-1 \
    --query 'Handler'
```

Should return: `lambda_handler_web.lambda_handler`

## 📱 Mobile Optimization

The web chat interface is fully responsive and works on:
- ✅ Desktop browsers
- ✅ Mobile phones
- ✅ Tablets
- ✅ iOS Safari
- ✅ Android Chrome

## 🎯 For Evaluators

Share this URL with evaluators:

```
http://kisaanmitra-web-demo-XXXXX.s3-website.ap-south-1.amazonaws.com
```

Or with CloudFront:

```
https://d1234567890.cloudfront.net
```

### Demo Features

1. **Real-time Chat:** Instant responses from AWS Bedrock
2. **Multi-language:** Switch between English and Hindi
3. **Disease Detection:** Upload crop images for AI diagnosis
4. **Market Intelligence:** Live prices and forecasts
5. **Budget Planning:** Complete ROI calculations
6. **Weather Updates:** Hyperlocal forecasts

## 🔄 Updates

To update the web interface:

```bash
# Update HTML
aws s3 cp demo/web-chat-demo.html s3://$BUCKET_NAME/index.html \
    --acl public-read \
    --content-type "text/html"

# Clear CloudFront cache (if using)
aws cloudfront create-invalidation \
    --distribution-id YOUR_DISTRIBUTION_ID \
    --paths "/*"
```

## 📞 Support

For issues or questions:
- Check Lambda logs: `aws logs tail /aws/lambda/whatsapp-llama-bot --follow`
- Check API Gateway logs
- Verify handler configuration
- Test API endpoint with curl

## ✅ Deployment Checklist

- [ ] API Gateway created and deployed
- [ ] Lambda handler updated to web mode
- [ ] Web interface uploaded to S3
- [ ] API endpoint configured in HTML
- [ ] CORS enabled and working
- [ ] Tested text messages
- [ ] Tested image upload
- [ ] Mobile responsive verified
- [ ] Shared URL with evaluators

---

**Status:** Ready for AWS AI Challenge Submission  
**Demo Type:** Live Interactive Web Interface  
**AWS Services:** Lambda, API Gateway, S3, Bedrock, DynamoDB  
**Cost:** ~$15-25/month
