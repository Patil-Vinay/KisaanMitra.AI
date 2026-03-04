#!/bin/bash
# Setup AWS Lambda + EventBridge for Daily Price Training
# Runs every morning at 6:00 AM IST (00:30 UTC)

REGION="ap-south-1"
FUNCTION_NAME="kisaanmitra-daily-trainer"
ROLE_NAME="kisaanmitra-trainer-role"
RULE_NAME="kisaanmitra-daily-training-trigger"
S3_BUCKET="kisaanmitra-images"

echo "=========================================="
echo "DAILY TRAINING LAMBDA SETUP"
echo "=========================================="

# Step 1: Create IAM Role for Lambda
echo ""
echo "[STEP 1] Creating IAM role..."

TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document "$TRUST_POLICY" \
  --region $REGION 2>/dev/null || echo "Role already exists"

# Attach policies
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

echo "✅ IAM role configured"

# Step 2: Package Lambda function
echo ""
echo "[STEP 2] Packaging Lambda function..."

cd src/lambda
zip -r lambda_daily_trainer.zip lambda_daily_trainer.py
cd ../..

echo "✅ Lambda package created"

# Step 3: Create Lambda function
echo ""
echo "[STEP 3] Creating Lambda function..."

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_daily_trainer.lambda_handler \
  --zip-file fileb://src/lambda/lambda_daily_trainer.zip \
  --timeout 900 \
  --memory-size 1024 \
  --environment "Variables={
    AGMARKNET_API_KEY=$AGMARKNET_API_KEY,
    PRICE_FORECAST_TABLE=kisaanmitra-price-forecasts,
    S3_BUCKET=$S3_BUCKET
  }" \
  --region $REGION 2>/dev/null || \
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://src/lambda/lambda_daily_trainer.zip \
  --region $REGION

echo "✅ Lambda function deployed"

# Step 4: Create EventBridge rule (6:00 AM IST = 00:30 UTC)
echo ""
echo "[STEP 4] Creating EventBridge rule..."

aws events put-rule \
  --name $RULE_NAME \
  --schedule-expression "cron(30 0 * * ? *)" \
  --description "Trigger daily price training at 6:00 AM IST" \
  --region $REGION

echo "✅ EventBridge rule created"

# Step 5: Add Lambda permission for EventBridge
echo ""
echo "[STEP 5] Granting EventBridge permission..."

aws lambda add-permission \
  --function-name $FUNCTION_NAME \
  --statement-id AllowEventBridgeInvoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn $(aws events describe-rule --name $RULE_NAME --query 'Arn' --output text --region $REGION) \
  --region $REGION 2>/dev/null || echo "Permission already exists"

echo "✅ Permission granted"

# Step 6: Add Lambda as target to EventBridge rule
echo ""
echo "[STEP 6] Connecting EventBridge to Lambda..."

LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.FunctionArn' --output text --region $REGION)

aws events put-targets \
  --rule $RULE_NAME \
  --targets "Id=1,Arn=$LAMBDA_ARN" \
  --region $REGION

echo "✅ Target configured"

# Summary
echo ""
echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "📋 CONFIGURATION:"
echo "   Lambda Function: $FUNCTION_NAME"
echo "   EventBridge Rule: $RULE_NAME"
echo "   Schedule: Daily at 6:00 AM IST (00:30 UTC)"
echo "   Timeout: 15 minutes"
echo "   Memory: 1024 MB"
echo ""
echo "🧪 TEST COMMANDS:"
echo "   Test Lambda:"
echo "   aws lambda invoke --function-name $FUNCTION_NAME --region $REGION output.json"
echo ""
echo "   View logs:"
echo "   aws logs tail /aws/lambda/$FUNCTION_NAME --since 10m --region $REGION"
echo ""
echo "   Check EventBridge rule:"
echo "   aws events describe-rule --name $RULE_NAME --region $REGION"
echo ""
echo "⚠️  NOTE: You need to add Prophet library to Lambda Layer"
echo "   Prophet is too large for Lambda deployment package"
echo "   Create a Lambda Layer with: pandas, prophet, pystan"
echo ""
echo "=========================================="
