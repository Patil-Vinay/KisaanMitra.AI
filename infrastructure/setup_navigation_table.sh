#!/bin/bash

# Setup Navigation State Table for KisaanMitra
# This table stores user navigation history for Back/Home/Cancel functionality

echo "🔧 Setting up Navigation State Table..."

# Create navigation state table
aws dynamodb create-table \
    --table-name kisaanmitra-navigation-state \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1 \
    --tags Key=Project,Value=KisaanMitra Key=Purpose,Value=NavigationState

if [ $? -eq 0 ]; then
    echo "✅ Navigation state table created successfully!"
else
    echo "⚠️  Table might already exist or there was an error"
fi

# Wait for table to be active
echo "⏳ Waiting for table to be active..."
aws dynamodb wait table-exists --table-name kisaanmitra-navigation-state --region ap-south-1

echo "✅ Navigation state table is ready!"
echo ""
echo "📋 Table Details:"
aws dynamodb describe-table --table-name kisaanmitra-navigation-state --region ap-south-1 --query 'Table.[TableName,TableStatus,ItemCount]' --output table

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update Lambda IAM role to allow access to this table"
echo "2. Deploy updated Lambda code with NavigationController"
echo "3. Test navigation flow in WhatsApp"
