# 🚀 AWS Lambda Updates Required

## Summary
Your Lambda code has been updated with **full Market and Finance agent implementations**. Now you need to update AWS configuration.

## ✅ What's Been Done
- ✅ Integrated full Market Agent (mandi prices, trend analysis, caching)
- ✅ Integrated full Finance Agent (budgets, loans, schemes)
- ✅ Updated `src/lambda/lambda_whatsapp_kisaanmitra.py`

## 🔧 What You Need to Do in AWS

### Step 1: Add Environment Variable (CRITICAL)

**In AWS Lambda Console:**

1. Go to: https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/whatsapp-llama-bot
2. Click **Configuration** tab → **Environment variables** → **Edit**
3. Click **Add environment variable**
4. Add:
   ```
   Key: AGMARKNET_API_KEY
   Value: <get from data.gov.in>
   ```

**How to get AgMarkNet API Key:**
- Visit: https://data.gov.in/
- Register/Login
- Go to: https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
- Click "API Access" and copy your key

**OR use a placeholder for testing:**
```
AGMARKNET_API_KEY=test_key_123
```
(Market agent will work without real API, just won't fetch live prices)

### Step 2: Update Lambda Configuration

**Option A - Using Script (Recommended):**
```bash
bash infrastructure/update_lambda_config.sh
```

**Option B - Manual in AWS Console:**
1. Go to Lambda → Configuration → General configuration → Edit
2. Set **Timeout**: 60 seconds
3. Set **Memory**: 512 MB
4. Click **Save**

### Step 3: Create DynamoDB Tables

**Run this command:**
```bash
bash infrastructure/setup_finance_tables.sh
```

**Or manually create tables:**
```bash
# Market data table
aws dynamodb create-table \
    --table-name kisaanmitra-market-data \
    --attribute-definitions AttributeName=crop_name,AttributeType=S \
    --key-schema AttributeName=crop_name,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1

# Finance table
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

### Step 4: Update IAM Permissions

**In AWS Console:**
1. Go to Lambda → Configuration → Permissions
2. Click on the **Execution role** name
3. Click **Add permissions** → **Attach policies**
4. Add **AmazonDynamoDBFullAccess** (or create custom policy)

**Or add inline policy:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query"
            ],
            "Resource": [
                "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-market-data",
                "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-finance"
            ]
        }
    ]
}
```

### Step 5: Deploy Updated Code

```bash
cd src/lambda
bash deploy_whatsapp.sh
```

This will:
- Package dependencies
- Zip the updated code
- Upload to AWS Lambda

### Step 6: Test Everything

**Test Market Agent:**
Send WhatsApp message to your bot:
```
गेहूं का भाव क्या है?
```
Expected: Mandi prices with trend

**Test Finance Agent:**
```
गेहूं का बजट बताओ
```
Expected: Budget breakdown

```
सरकारी योजना
```
Expected: List of schemes

```
लोन चाहिए
```
Expected: Loan eligibility

**Test Crop Agent:**
Send a crop image
Expected: Disease detection

## 📊 Quick Checklist

```
[ ] Add AGMARKNET_API_KEY environment variable
[ ] Update Lambda timeout to 60 seconds
[ ] Update Lambda memory to 512 MB
[ ] Create kisaanmitra-market-data DynamoDB table
[ ] Create kisaanmitra-finance DynamoDB table
[ ] Update IAM role with DynamoDB permissions
[ ] Deploy updated Lambda code
[ ] Test Market Agent via WhatsApp
[ ] Test Finance Agent via WhatsApp
[ ] Test Crop Agent via WhatsApp
[ ] Check CloudWatch logs for errors
```

## 🔍 Monitoring

**Check CloudWatch Logs:**
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

Look for:
- "Market Agent: Fetching prices..."
- "Finance Agent: Budget calculation..."
- Any error messages

## 💰 Cost Impact

**New costs:**
- DynamoDB: ~$1-2/month (on-demand pricing)
- AgMarkNet API: Free (500 requests/day)
- Lambda: Minimal increase (same Bedrock usage)

**Total estimated: $5-10/month for 1000 messages/day**

## 🆘 Troubleshooting

**Market prices not showing:**
- Check AGMARKNET_API_KEY is set
- Verify table `kisaanmitra-market-data` exists
- Check CloudWatch logs

**Finance not working:**
- Verify table `kisaanmitra-finance` exists
- Check Lambda has 512 MB memory
- Check timeout is 60 seconds

**Lambda timeout errors:**
- Increase timeout to 90 seconds
- Check Bedrock region (should be us-east-1)

## 📚 Documentation

- Full guide: `docs/LAMBDA_UPDATE_GUIDE.md`
- Deployment checklist: `docs/DEPLOYMENT_CHECKLIST.md`
- Testing guide: `docs/TESTING_GUIDE.md`

## 🎯 Next Steps After Deployment

1. Monitor CloudWatch logs for 24 hours
2. Test with real farmers
3. Collect feedback on budget accuracy
4. Fine-tune market price display format
5. Add more crops to budget templates

---

**Need help?** Check CloudWatch logs or run:
```bash
bash scripts/test/test_whatsapp_integration.sh
```
