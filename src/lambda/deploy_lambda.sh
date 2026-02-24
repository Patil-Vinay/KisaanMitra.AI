#!/bin/bash

# KisaanMitra.AI - Deploy Crop Agent to AWS Lambda
# Usage: ./deploy_lambda.sh

set -e

# Configuration
FUNCTION_NAME="kisaanmitra-crop-agent"
REGION="ap-south-1"
RUNTIME="python3.11"
HANDLER="lambda_crop_agent.lambda_handler"
ROLE_NAME="kisaanmitra-lambda-role"
S3_BUCKET="kisaanmitra-images"
SECRET_NAME="kisaanmitra/crop-health-api"

echo "🚀 Deploying KisaanMitra.AI Crop Agent to AWS Lambda..."

# Step 1: Create deployment package
echo "📦 Creating deployment package..."
rm -rf package lambda_deployment.zip
mkdir -p package

# Install dependencies
pip install -r lambda_requirements.txt -t package/

# Copy Lambda function
cp lambda_crop_agent.py package/

# Create ZIP
cd package
zip -r ../lambda_deployment.zip .
cd ..

echo "✅ Deployment package created: lambda_deployment.zip"

# Step 2: Create IAM role (if not exists)
echo "🔐 Checking IAM role..."
if ! aws iam get-role --role-name $ROLE_NAME --region $REGION 2>/dev/null; then
    echo "Creating IAM role..."
    
    # Create trust policy
    cat > trust-policy.json <<EOF
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
        --assume-role-policy-document file://trust-policy.json \
        --region $REGION

    # Attach policies
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
        --region $REGION

    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
        --region $REGION

    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite \
        --region $REGION

    echo "✅ IAM role created"
    sleep 10  # Wait for role to propagate
else
    echo "✅ IAM role already exists"
fi

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text --region $REGION)
echo "Role ARN: $ROLE_ARN"

# Step 3: Create or update Lambda function
echo "⚡ Deploying Lambda function..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_deployment.zip \
        --region $REGION

    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --timeout 30 \
        --memory-size 512 \
        --environment "Variables={S3_BUCKET=$S3_BUCKET,SECRET_NAME=$SECRET_NAME,AWS_REGION=$REGION}" \
        --region $REGION
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda_deployment.zip \
        --timeout 30 \
        --memory-size 512 \
        --environment "Variables={S3_BUCKET=$S3_BUCKET,SECRET_NAME=$SECRET_NAME,AWS_REGION=$REGION}" \
        --region $REGION
fi

echo "✅ Lambda function deployed successfully!"

# Step 4: Create API Gateway (optional)
echo ""
echo "📝 Next steps:"
echo "1. Store your API key in AWS Secrets Manager:"
echo "   aws secretsmanager create-secret --name $SECRET_NAME --secret-string '{\"CROP_HEALTH_API_KEY\":\"your_api_key\"}' --region $REGION"
echo ""
echo "2. Test the function:"
echo "   aws lambda invoke --function-name $FUNCTION_NAME --payload file://test_event.json response.json --region $REGION"
echo ""
echo "3. Create API Gateway to expose HTTP endpoint (optional)"
echo ""
echo "🎉 Deployment complete!"
