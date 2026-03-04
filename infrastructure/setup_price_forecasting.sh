#!/bin/bash

# Setup AWS Infrastructure for Price Forecasting
# Creates S3 bucket, DynamoDB table, Lambda function, EventBridge rule, and SNS topic

set -e

REGION="ap-south-1"
S3_BUCKET="kisaanmitra-price-data"
DYNAMODB_TABLE="kisaanmitra-price-forecasts"
LAMBDA_FUNCTION="kisaanmitra-price-updater"
SNS_TOPIC="kisaanmitra-price-alerts"
EVENTBRIDGE_RULE="kisaanmitra-daily-price-update"

echo "🚀 Setting up Price Forecasting Infrastructure in $REGION"
echo "=" * 60

# 1. Create S3 Bucket for price data
echo "📦 Creating S3 bucket: $S3_BUCKET"
aws s3 mb s3://$S3_BUCKET --region $REGION 2>/dev/null || echo "Bucket already exists"

# Create folders
aws s3api put-object --bucket $S3_BUCKET --key historical_prices/ --region $REGION
aws s3api put-object --bucket $S3_BUCKET --key forecasts/ --region $REGION
aws s3api put-object --bucket $S3_BUCKET --key models/ --region $REGION

echo "✅ S3 bucket created"

# 2. Upload initial CSV files to S3
echo "📤 Uploading historical price data to S3..."
aws s3 sync data/historical_prices/ s3://$S3_BUCKET/historical_prices/ --region $REGION
echo "✅ Historical data uploaded"

# 3. Create DynamoDB Table for forecasts
echo "🗄️  Creating DynamoDB table: $DYNAMODB_TABLE"
aws dynamodb create-table \
    --table-name $DYNAMODB_TABLE \
    --attribute-definitions \
        AttributeName=commodity,AttributeType=S \
    --key-schema \
        AttributeName=commodity,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --tags Key=Project,Value=KisaanMitra Key=Component,Value=PriceForecasting \
    2>/dev/null || echo "Table already exists"

# Enable TTL for auto-cleanup
aws dynamodb update-time-to-live \
    --table-name $DYNAMODB_TABLE \
    --time-to-live-specification "Enabled=true, AttributeName=ttl" \
    --region $REGION 2>/dev/null || echo "TTL already enabled"

echo "✅ DynamoDB table created"

# 4. Create SNS Topic for alerts
echo "📧 Creating SNS topic: $SNS_TOPIC"
SNS_TOPIC_ARN=$(aws sns create-topic \
    --name $SNS_TOPIC \
    --region $REGION \
    --query 'TopicArn' \
    --output text)

echo "✅ SNS topic created: $SNS_TOPIC_ARN"

# 5. Create IAM Role for Lambda
echo "👤 Creating IAM role for Lambda..."
ROLE_NAME="kisaanmitra-price-updater-role"

# Create trust policy
cat > /tmp/trust-policy.json <<EOF
{
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
}
EOF

# Create role
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file:///tmp/trust-policy.json \
    --region $REGION 2>/dev/null || echo "Role already exists"

# Attach policies
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
    --region $REGION

# Create custom policy for S3, DynamoDB, SNS
cat > /tmp/lambda-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$S3_BUCKET",
        "arn:aws:s3:::$S3_BUCKET/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:$REGION:*:table/$DYNAMODB_TABLE"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "$SNS_TOPIC_ARN"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name KisaanMitraPriceUpdaterPolicy \
    --policy-document file:///tmp/lambda-policy.json \
    --region $REGION

echo "✅ IAM role created"

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

# Wait for role to propagate
echo "⏳ Waiting for IAM role to propagate..."
sleep 10

# 6. Create Lambda function
echo "⚡ Creating Lambda function: $LAMBDA_FUNCTION"

# Package Lambda code
cd src/lambda
zip -q lambda_price_updater.zip lambda_price_updater.py
cd ../..

# Create Lambda function
aws lambda create-function \
    --function-name $LAMBDA_FUNCTION \
    --runtime python3.12 \
    --role $ROLE_ARN \
    --handler lambda_price_updater.lambda_handler \
    --zip-file fileb://src/lambda/lambda_price_updater.zip \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{
        S3_BUCKET=$S3_BUCKET,
        PRICE_FORECAST_TABLE=$DYNAMODB_TABLE,
        SNS_TOPIC_ARN=$SNS_TOPIC_ARN,
        AGMARKNET_API_KEY=$AGMARKNET_API_KEY
    }" \
    --region $REGION \
    2>/dev/null || echo "Lambda function already exists"

echo "✅ Lambda function created"

# 7. Create EventBridge Rule (CloudWatch Events) for daily trigger
echo "⏰ Creating EventBridge rule for daily 6 AM IST trigger..."

# 6 AM IST = 12:30 AM UTC (IST is UTC+5:30)
aws events put-rule \
    --name $EVENTBRIDGE_RULE \
    --schedule-expression "cron(30 0 * * ? *)" \
    --state ENABLED \
    --description "Daily price forecast update at 6 AM IST" \
    --region $REGION

# Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name $LAMBDA_FUNCTION \
    --region $REGION \
    --query 'Configuration.FunctionArn' \
    --output text)

# Add Lambda as target
aws events put-targets \
    --rule $EVENTBRIDGE_RULE \
    --targets "Id"="1","Arn"="$LAMBDA_ARN" \
    --region $REGION

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
    --function-name $LAMBDA_FUNCTION \
    --statement-id AllowEventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$REGION:$(aws sts get-caller-identity --query Account --output text):rule/$EVENTBRIDGE_RULE \
    --region $REGION \
    2>/dev/null || echo "Permission already exists"

echo "✅ EventBridge rule created"

# 8. Update main WhatsApp Lambda with price forecasting
echo "🔄 Updating main WhatsApp Lambda..."

# Add environment variable
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --environment Variables="{
        PRICE_FORECAST_TABLE=$DYNAMODB_TABLE,
        S3_BUCKET=$S3_BUCKET
    }" \
    --region $REGION

echo "✅ Main Lambda updated"

# 9. Test the setup
echo "🧪 Testing Lambda function..."
aws lambda invoke \
    --function-name $LAMBDA_FUNCTION \
    --region $REGION \
    /tmp/lambda-response.json

cat /tmp/lambda-response.json
echo ""

echo "=" * 60
echo "✅ Price Forecasting Infrastructure Setup Complete!"
echo "=" * 60
echo ""
echo "📊 Resources Created:"
echo "  - S3 Bucket: $S3_BUCKET"
echo "  - DynamoDB Table: $DYNAMODB_TABLE"
echo "  - Lambda Function: $LAMBDA_FUNCTION"
echo "  - SNS Topic: $SNS_TOPIC_ARN"
echo "  - EventBridge Rule: $EVENTBRIDGE_RULE (Daily 6 AM IST)"
echo ""
echo "🔧 Next Steps:"
echo "  1. Subscribe to SNS topic for alerts:"
echo "     aws sns subscribe --topic-arn $SNS_TOPIC_ARN --protocol email --notification-endpoint your@email.com"
echo ""
echo "  2. Manually trigger update:"
echo "     aws lambda invoke --function-name $LAMBDA_FUNCTION --region $REGION response.json"
echo ""
echo "  3. View logs:"
echo "     aws logs tail /aws/lambda/$LAMBDA_FUNCTION --follow --region $REGION"
