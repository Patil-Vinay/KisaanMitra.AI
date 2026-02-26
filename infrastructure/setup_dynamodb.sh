#!/bin/bash

# Setup DynamoDB tables for KisaanMitra.AI

set -e

REGION="ap-south-1"

echo "🗄️  Setting up DynamoDB tables..."
echo "=================================="
echo ""

# 1. Conversation History Table
echo "1️⃣ Creating conversation history table..."
aws dynamodb create-table \
  --table-name kisaanmitra-conversations \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION \
  --tags Key=Project,Value=KisaanMitra Key=Environment,Value=Production \
  2>/dev/null || echo "Table already exists"

echo ""

# 2. Market Data Cache Table
echo "2️⃣ Creating market data cache table..."
aws dynamodb create-table \
  --table-name kisaanmitra-market-data \
  --attribute-definitions \
    AttributeName=crop_name,AttributeType=S \
  --key-schema \
    AttributeName=crop_name,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --time-to-live-specification Enabled=true,AttributeName=ttl \
  --region $REGION \
  --tags Key=Project,Value=KisaanMitra Key=Environment,Value=Production \
  2>/dev/null || echo "Table already exists"

echo ""

# 3. User Preferences Table
echo "3️⃣ Creating user preferences table..."
aws dynamodb create-table \
  --table-name kisaanmitra-user-preferences \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION \
  --tags Key=Project,Value=KisaanMitra Key=Environment,Value=Production \
  2>/dev/null || echo "Table already exists"

echo ""
echo "⏳ Waiting for tables to become active..."
sleep 10

echo ""
echo "✅ DynamoDB tables setup complete!"
echo ""
echo "📊 Tables created:"
echo "   • kisaanmitra-conversations (conversation history)"
echo "   • kisaanmitra-market-data (market price cache)"
echo "   • kisaanmitra-user-preferences (user settings)"
echo ""
echo "🔍 Verify tables:"
echo "   aws dynamodb list-tables --region $REGION"
