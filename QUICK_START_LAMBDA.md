# Quick Start: Deploy to AWS Lambda in 5 Minutes

## Prerequisites
- AWS CLI configured (`aws configure`)
- Your Crop Health API key

## Step 1: Store API Key (30 seconds)
```bash
aws secretsmanager create-secret \
    --name kisaanmitra/crop-health-api \
    --secret-string '{"CROP_HEALTH_API_KEY":"YOUR_API_KEY_HERE"}' \
    --region ap-south-1
```

## Step 2: Create S3 Bucket (30 seconds)
```bash
aws s3 mb s3://kisaanmitra-images --region ap-south-1
```

## Step 3: Deploy Lambda (2 minutes)
```bash
./deploy_lambda.sh
```

## Step 4: Test (1 minute)
```bash
# Upload test image
aws s3 cp 2.jpg s3://kisaanmitra-images/test/crop.jpg

# Test Lambda
aws lambda invoke \
    --function-name kisaanmitra-crop-agent \
    --payload '{"image_source":"s3","s3_bucket":"kisaanmitra-images","s3_key":"test/crop.jpg","latitude":18.5204,"longitude":73.8567,"language":"hi"}' \
    --region ap-south-1 \
    response.json

# View result
cat response.json | jq .
```

## Done! 🎉

Your Crop Agent is now running serverless on AWS Lambda!

**Next**: Integrate with WhatsApp (see LAMBDA_SETUP.md)
