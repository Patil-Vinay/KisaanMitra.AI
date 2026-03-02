#!/bin/bash

# Setup DynamoDB tables for hyperlocal disease tracking and best practices

echo "🏥 Setting up Hyperlocal Disease & Best Practices Tables..."

# Table 1: Disease Reports (what farmers are experiencing)
aws dynamodb create-table \
    --table-name kisaanmitra-disease-reports \
    --attribute-definitions \
        AttributeName=report_id,AttributeType=S \
        AttributeName=village,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=report_id,KeyType=HASH \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"village-timestamp-index\",
                \"KeySchema\": [
                    {\"AttributeName\":\"village\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"timestamp\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\": {
                    \"ReadCapacityUnits\": 5,
                    \"WriteCapacityUnits\": 5
                }
            }
        ]" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ap-south-1

echo "✅ Disease Reports table created"

# Table 2: Treatment Success Stories (what worked for farmers)
aws dynamodb create-table \
    --table-name kisaanmitra-treatment-success \
    --attribute-definitions \
        AttributeName=success_id,AttributeType=S \
        AttributeName=disease_type,AttributeType=S \
        AttributeName=effectiveness_score,AttributeType=N \
    --key-schema \
        AttributeName=success_id,KeyType=HASH \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"disease-effectiveness-index\",
                \"KeySchema\": [
                    {\"AttributeName\":\"disease_type\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"effectiveness_score\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\": {
                    \"ReadCapacityUnits\": 5,
                    \"WriteCapacityUnits\": 5
                }
            }
        ]" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ap-south-1

echo "✅ Treatment Success table created"

# Table 3: Best Practices (community knowledge)
aws dynamodb create-table \
    --table-name kisaanmitra-best-practices \
    --attribute-definitions \
        AttributeName=practice_id,AttributeType=S \
        AttributeName=crop_type,AttributeType=S \
        AttributeName=upvotes,AttributeType=N \
    --key-schema \
        AttributeName=practice_id,KeyType=HASH \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"crop-upvotes-index\",
                \"KeySchema\": [
                    {\"AttributeName\":\"crop_type\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"upvotes\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\": {
                    \"ReadCapacityUnits\": 5,
                    \"WriteCapacityUnits\": 5
                }
            }
        ]" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region ap-south-1

echo "✅ Best Practices table created"

echo ""
echo "🎉 All hyperlocal tables created successfully!"
echo ""
echo "Tables created:"
echo "  1. kisaanmitra-disease-reports (disease tracking by village)"
echo "  2. kisaanmitra-treatment-success (what treatments worked)"
echo "  3. kisaanmitra-best-practices (community farming tips)"
