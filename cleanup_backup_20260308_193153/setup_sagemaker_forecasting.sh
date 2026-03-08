#!/bin/bash

# Setup SageMaker Canvas Time Series Forecasting
# No Docker required!

set -e

echo "=========================================="
echo "SAGEMAKER FORECASTING SETUP"
echo "=========================================="
echo ""

AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
S3_BUCKET="kisaanmitra-ml-data"
LAMBDA_FUNCTION_NAME="kisaanmitra-sagemaker-forecaster"
SAGEMAKER_ROLE_NAME="KisaanMitra-SageMaker-Role"
LAMBDA_ROLE_NAME="KisaanMitra-Lambda-SageMaker-Role"

echo "AWS Account: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "S3 Bucket: $S3_BUCKET"
echo ""

# Step 1: Create S3 bucket for ML data
echo "Step 1: Creating S3 bucket..."
aws s3 mb s3://$S3_BUCKET --region $AWS_REGION 2>/dev/null || echo "Bucket already exists"
echo "✅ S3 bucket ready"
echo ""

# Step 2: Create SageMaker execution role
echo "Step 2: Creating SageMaker execution role..."

cat > /tmp/sagemaker-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role if it doesn't exist
aws iam get-role --role-name $SAGEMAKER_ROLE_NAME 2>/dev/null || \
aws iam create-role \
    --role-name $SAGEMAKER_ROLE_NAME \
    --assume-role-policy-document file:///tmp/sagemaker-trust-policy.json

# Attach policies
aws iam attach-role-policy \
    --role-name $SAGEMAKER_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
    --role-name $SAGEMAKER_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

SAGEMAKER_ROLE_ARN="arn:aws:iam::$AWS_ACCOUNT_ID:role/$SAGEMAKER_ROLE_NAME"
echo "✅ SageMaker role: $SAGEMAKER_ROLE_ARN"
echo ""

# Step 3: Create Lambda execution role
echo "Step 3: Creating Lambda execution role..."

cat > /tmp/lambda-trust-policy.json <<EOF
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

# Create role if it doesn't exist
aws iam get-role --role-name $LAMBDA_ROLE_NAME 2>/dev/null || \
aws iam create-role \
    --role-name $LAMBDA_ROLE_NAME \
    --assume-role-policy-document file:///tmp/lambda-trust-policy.json

# Attach policies
aws iam attach-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

LAMBDA_ROLE_ARN="arn:aws:iam::$AWS_ACCOUNT_ID:role/$LAMBDA_ROLE_NAME"
echo "✅ Lambda role: $LAMBDA_ROLE_ARN"
echo ""

# Wait for roles to propagate
echo "Waiting for IAM roles to propagate..."
sleep 10

# Step 4: Package Lambda function
echo "Step 4: Packaging Lambda function..."

cd src
zip -r /tmp/lambda_sagemaker.zip \
    lambda/lambda_sagemaker_forecaster.py \
    sagemaker_forecasting/*.py

echo "✅ Lambda package created"
echo ""

# Step 5: Create or update Lambda function
echo "Step 5: Creating/updating Lambda function..."

if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --zip-file fileb:///tmp/lambda_sagemaker.zip \
        --region $AWS_REGION
else
    echo "Creating new Lambda function..."
    aws lambda create-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --runtime python3.11 \
        --role $LAMBDA_ROLE_ARN \
        --handler lambda_sagemaker_forecaster.lambda_handler \
        --zip-file fileb:///tmp/lambda_sagemaker.zip \
        --timeout 900 \
        --memory-size 512 \
        --environment "Variables={
            S3_BUCKET=$S3_BUCKET,
            SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE_ARN,
            DYNAMODB_TABLE=kisaanmitra-price-forecasts,
            USE_EXISTING_MODEL=false
        }" \
        --region $AWS_REGION
fi

echo "✅ Lambda function deployed"
echo ""

# Step 6: Create EventBridge rule for weekly training
echo "Step 6: Setting up weekly schedule..."

RULE_NAME="kisaanmitra-weekly-training"

# Create rule (runs every Sunday at 2 AM IST = Saturday 8:30 PM UTC)
aws events put-rule \
    --name $RULE_NAME \
    --schedule-expression "cron(30 20 ? * SUN *)" \
    --state ENABLED \
    --region $AWS_REGION \
    --description "Weekly price forecasting training"

# Add Lambda permission
aws lambda add-permission \
    --function-name $LAMBDA_FUNCTION_NAME \
    --statement-id AllowEventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$AWS_REGION:$AWS_ACCOUNT_ID:rule/$RULE_NAME \
    --region $AWS_REGION 2>/dev/null || echo "Permission already exists"

# Add Lambda as target
LAMBDA_ARN=$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION --query 'Configuration.FunctionArn' --output text)

aws events put-targets \
    --rule $RULE_NAME \
    --targets "Id"="1","Arn"="$LAMBDA_ARN" \
    --region $AWS_REGION

echo "✅ Weekly schedule configured"
echo ""

echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Resources created:"
echo "  - S3 Bucket: $S3_BUCKET"
echo "  - SageMaker Role: $SAGEMAKER_ROLE_ARN"
echo "  - Lambda Function: $LAMBDA_FUNCTION_NAME"
echo "  - Schedule: Weekly on Sunday at 2 AM IST"
echo ""
echo "Next steps:"
echo "1. Test Lambda manually:"
echo "   aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION output.json"
echo ""
echo "2. First run will create AutoML training job (takes 1-2 hours)"
echo ""
echo "3. After training completes, set USE_EXISTING_MODEL=true to use trained model"
echo ""
echo "4. Monitor SageMaker jobs in AWS Console"
