# Lambda Update Guide - Full Agent Integration

## What Changed

The Lambda function now includes **full implementations** of Market and Finance agents:

### Market Agent Features:
- Real-time mandi price fetching from AgMarkNet API
- Price trend analysis (increasing/decreasing/stable)
- DynamoDB caching (6-hour TTL)
- Multi-language crop name support (Hindi/English)

### Finance Agent Features:
- Detailed crop budget templates (wheat, rice, cotton, onion)
- Government scheme matching (PM-KISAN, PMFBY, KCC, etc.)
- Loan eligibility calculator with EMI
- Scalable by land size

## AWS Configuration Updates

### 1. Environment Variables to Add

In AWS Lambda Console → Configuration → Environment variables:

```bash
# Existing (keep these)
VERIFY_TOKEN=mySecret_123
WHATSAPP_TOKEN=YOUR_WHATSAPP_TOKEN
PHONE_NUMBER_ID=1049535664900621
CROP_HEALTH_API_KEY=YOUR_CROP_HEALTH_API_KEY

# NEW - Add this for Market Agent
AGMARKNET_API_KEY=<your-agmarknet-api-key>
```

**Get AgMarkNet API Key:**
1. Visit: https://data.gov.in/
2. Register/Login
3. Go to: https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
4. Request API access
5. Copy your API key

### 2. DynamoDB Tables Required

Run these setup scripts if not already done:

```bash
# Market data caching table
aws dynamodb create-table \
    --table-name kisaanmitra-market-data \
    --attribute-definitions \
        AttributeName=crop_name,AttributeType=S \
    --key-schema \
        AttributeName=crop_name,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1

# Finance data table
aws dynamodb create-table \
    --table-name kisaanmitra-finance \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1
```

Or use the infrastructure script:
```bash
bash infrastructure/setup_finance_tables.sh
```

### 3. IAM Permissions Update

Your Lambda execution role needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-conversations",
                "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-market-data",
                "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-finance"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:Converse"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-micro-v1:0"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

### 4. Deploy Updated Lambda

```bash
cd src/lambda
bash deploy_whatsapp.sh
```

Or manually:

```bash
# Package dependencies
cd src/lambda
pip install -r lambda_requirements.txt -t package/
cp lambda_whatsapp_kisaanmitra.py package/

# Create deployment package
cd package
zip -r ../lambda_deployment.zip .

# Upload to Lambda
aws lambda update-function-code \
    --function-name whatsapp-llama-bot \
    --zip-file fileb://../lambda_deployment.zip \
    --region ap-south-1
```

### 5. Increase Lambda Timeout & Memory

The integrated agents need more resources:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --timeout 60 \
    --memory-size 512 \
    --region ap-south-1
```

Or in AWS Console:
- Configuration → General configuration → Edit
- Timeout: 60 seconds
- Memory: 512 MB

## Testing the Updated Lambda

### Test Market Agent:
Send WhatsApp message:
```
गेहूं का भाव क्या है?
```
or
```
onion price
```

Expected response: Real mandi prices with trend analysis

### Test Finance Agent:
Send WhatsApp message:
```
गेहूं का बजट बताओ
```
or
```
wheat budget
```

Expected response: Detailed budget breakdown

```
सरकारी योजना
```

Expected response: List of government schemes

```
लोन चाहिए
```

Expected response: Loan eligibility details

### Test Crop Agent (existing):
Send crop image → Disease detection

## Monitoring

Check CloudWatch Logs for:
```
Market Agent: Fetching prices for <crop>
Market Agent: Cache hit/miss
Finance Agent: Budget calculation for <crop>
```

## Troubleshooting

### Market prices not showing:
- Check AGMARKNET_API_KEY is set
- Verify DynamoDB table exists: `kisaanmitra-market-data`
- Check IAM permissions for DynamoDB

### Finance calculations not working:
- Verify DynamoDB table exists: `kisaanmitra-finance`
- Check Lambda has sufficient memory (512 MB)

### General errors:
- Check CloudWatch Logs: `/aws/lambda/whatsapp-llama-bot`
- Verify all environment variables are set
- Ensure Lambda timeout is 60 seconds

## Cost Optimization

- Market data cached for 6 hours (reduces API calls)
- DynamoDB on-demand pricing (pay per request)
- Bedrock Nova Micro (cheapest model)

Estimated costs:
- 1000 messages/day: ~$5-10/month
- Market API: Free tier (500 requests/day)
- DynamoDB: ~$1-2/month

## Next Steps

1. ✅ Deploy updated Lambda code
2. ✅ Add AGMARKNET_API_KEY environment variable
3. ✅ Create DynamoDB tables
4. ✅ Update IAM permissions
5. ✅ Increase timeout to 60s and memory to 512 MB
6. ✅ Test all three agents via WhatsApp
7. Monitor CloudWatch logs for errors

## Rollback Plan

If issues occur, revert to simple version:
```bash
git checkout HEAD~1 src/lambda/lambda_whatsapp_kisaanmitra.py
bash src/lambda/deploy_whatsapp.sh
```
