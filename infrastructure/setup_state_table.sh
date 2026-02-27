#!/bin/bash

# Create DynamoDB table for user state tracking
# This tracks what the user is currently doing (awaiting budget details, etc.)

REGION="ap-south-1"
TABLE_NAME="kisaanmitra-user-state"

echo "🔧 Creating user state tracking table..."

aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --tags Key=Project,Value=KisaanMitra Key=Purpose,Value=StateTracking

echo "⏳ Waiting for table to be active..."
aws dynamodb wait table-exists --table-name $TABLE_NAME --region $REGION

# Enable TTL after table is created
echo "🕐 Enabling TTL..."
aws dynamodb update-time-to-live \
    --table-name $TABLE_NAME \
    --time-to-live-specification Enabled=true,AttributeName=ttl \
    --region $REGION

echo "✅ State tracking table created: $TABLE_NAME"
echo ""
echo "📊 Table details:"
aws dynamodb describe-table --table-name $TABLE_NAME --region $REGION --query 'Table.[TableName,TableStatus,ItemCount]' --output table
