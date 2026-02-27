#!/bin/bash

# Update IAM role with required permissions

set -e

ROLE_NAME="kisaanmitra-lambda-role"
REGION="ap-south-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🔐 Updating IAM permissions for Lambda..."
echo "=========================================="
echo ""

# Create policy document
cat > lambda-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:${REGION}:${ACCOUNT_ID}:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::kisaanmitra-images/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:kisaanmitra/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:Converse"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-micro-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0",
        "arn:aws:bedrock:${REGION}::foundation-model/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/kisaanmitra-conversations",
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/kisaanmitra-market-data",
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/kisaanmitra-finance",
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/kisaanmitra-user-preferences",
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/kisaanmitra-navigation-state",
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/kisaanmitra-onboarding",
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/kisaanmitra-farmer-profiles"
      ]
    }
  ]
}
EOF

echo "1️⃣ Creating/updating policy..."
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name kisaanmitra-lambda-policy \
  --policy-document file://lambda-policy.json

echo ""
echo "✅ IAM permissions updated!"
echo ""
echo "📋 Permissions granted:"
echo "   • CloudWatch Logs (write)"
echo "   • S3 (read/write images)"
echo "   • Secrets Manager (read API keys)"
echo "   • Bedrock (invoke Nova Micro)"
echo "   • DynamoDB (read/write all tables)"
echo ""

# Cleanup
rm lambda-policy.json
