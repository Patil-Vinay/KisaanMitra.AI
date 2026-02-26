#!/bin/bash

# Setup Finance Agent DynamoDB tables

set -e

REGION="ap-south-1"

echo "💰 Setting up Finance Agent tables..."
echo "======================================"
echo ""

# Finance Plans Table
echo "1️⃣ Creating finance plans table..."
aws dynamodb create-table \
  --table-name kisaanmitra-finance \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --time-to-live-specification Enabled=true,AttributeName=ttl \
  --region $REGION \
  --tags Key=Project,Value=KisaanMitra Key=Agent,Value=Finance \
  2>/dev/null || echo "Table already exists"

echo ""

# Government Schemes Table
echo "2️⃣ Creating schemes database table..."
aws dynamodb create-table \
  --table-name kisaanmitra-schemes \
  --attribute-definitions \
    AttributeName=scheme_id,AttributeType=S \
    AttributeName=state,AttributeType=S \
  --key-schema \
    AttributeName=scheme_id,KeyType=HASH \
  --global-secondary-indexes \
    "IndexName=StateIndex,KeySchema=[{AttributeName=state,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
  --billing-mode PROVISIONED \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region $REGION \
  --tags Key=Project,Value=KisaanMitra Key=Agent,Value=Finance \
  2>/dev/null || echo "Table already exists"

echo ""

# Create S3 bucket for budget PDFs
echo "3️⃣ Creating S3 bucket for financial plans..."
aws s3 mb s3://kisaanmitra-budgets --region $REGION 2>/dev/null || echo "Bucket already exists"

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket kisaanmitra-budgets \
  --versioning-configuration Status=Enabled \
  --region $REGION 2>/dev/null || true

echo ""
echo "✅ Finance Agent infrastructure ready!"
echo ""
echo "📊 Resources created:"
echo "   • kisaanmitra-finance (financial plans)"
echo "   • kisaanmitra-schemes (government schemes)"
echo "   • s3://kisaanmitra-budgets (plan storage)"
