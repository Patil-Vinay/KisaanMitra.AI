#!/bin/bash

# Setup DynamoDB tables for farmer onboarding
# Run this script to create required tables

echo "Creating DynamoDB tables for onboarding..."

# Create onboarding state table
aws dynamodb create-table \
    --table-name kisaanmitra-onboarding \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1 \
    --tags Key=Project,Value=KisaanMitra Key=Purpose,Value=Onboarding

echo "Created kisaanmitra-onboarding table"

# Create user profiles table
aws dynamodb create-table \
    --table-name kisaanmitra-user-profiles \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=village,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"village-index\",
                \"KeySchema\": [{\"AttributeName\":\"village\",\"KeyType\":\"HASH\"}],
                \"Projection\": {\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
            }
        ]" \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1 \
    --tags Key=Project,Value=KisaanMitra Key=Purpose,Value=UserProfiles

echo "Created kisaanmitra-user-profiles table with village index"

echo "✅ Onboarding tables created successfully!"
echo ""
echo "Tables created:"
echo "  1. kisaanmitra-onboarding (tracks onboarding state)"
echo "  2. kisaanmitra-user-profiles (stores farmer profiles)"
echo ""
echo "Next steps:"
echo "  1. Setup Neptune cluster: ./setup_neptune.sh"
echo "  2. Deploy Lambda with onboarding: cd ../src/lambda && ./deploy_with_onboarding.sh"
