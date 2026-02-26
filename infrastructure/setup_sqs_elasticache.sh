#!/bin/bash

# Setup SQS and ElastiCache for KisaanMitra.AI

set -e

REGION="ap-south-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Setting up AWS Enhancements"
echo "=============================="
echo ""

# 1. Create SQS Queue
echo "1️⃣ Creating SQS Queue..."
aws sqs create-queue \
  --queue-name kisaanmitra-messages \
  --attributes \
    VisibilityTimeout=300,\
    MessageRetentionPeriod=86400,\
    ReceiveMessageWaitTimeSeconds=20 \
  --tags Key=Project,Value=KisaanMitra Key=Environment,Value=Production \
  --region $REGION \
  2>/dev/null || echo "Queue already exists"

# Get queue URL
QUEUE_URL=$(aws sqs get-queue-url --queue-name kisaanmitra-messages --region $REGION --query QueueUrl --output text)
echo "✓ Queue URL: $QUEUE_URL"

# 2. Create Dead Letter Queue
echo ""
echo "2️⃣ Creating Dead Letter Queue..."
aws sqs create-queue \
  --queue-name kisaanmitra-messages-dlq \
  --attributes MessageRetentionPeriod=1209600 \
  --tags Key=Project,Value=KisaanMitra Key=Type,Value=DLQ \
  --region $REGION \
  2>/dev/null || echo "DLQ already exists"

DLQ_URL=$(aws sqs get-queue-url --queue-name kisaanmitra-messages-dlq --region $REGION --query QueueUrl --output text)
DLQ_ARN=$(aws sqs get-queue-attributes --queue-url $DLQ_URL --attribute-names QueueArn --region $REGION --query Attributes.QueueArn --output text)

# Configure DLQ on main queue
aws sqs set-queue-attributes \
  --queue-url $QUEUE_URL \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_ARN\\\",\\\"maxReceiveCount\\\":\\\"3\\\"}\"}" \
  --region $REGION

echo "✓ DLQ configured with 3 max retries"

# 3. Create ElastiCache Subnet Group
echo ""
echo "3️⃣ Creating ElastiCache Subnet Group..."

# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --region $REGION --query 'Vpcs[0].VpcId' --output text)
echo "Using VPC: $VPC_ID"

# Get subnets
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --region $REGION --query 'Subnets[*].SubnetId' --output text)
SUBNET_ARRAY=($SUBNET_IDS)

aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name kisaanmitra-cache-subnet \
  --cache-subnet-group-description "Subnet group for KisaanMitra cache" \
  --subnet-ids ${SUBNET_ARRAY[@]} \
  --region $REGION \
  2>/dev/null || echo "Subnet group already exists"

echo "✓ Subnet group created"

# 4. Create Security Group for ElastiCache
echo ""
echo "4️⃣ Creating Security Group..."

SG_ID=$(aws ec2 create-security-group \
  --group-name kisaanmitra-cache-sg \
  --description "Security group for KisaanMitra ElastiCache" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text 2>/dev/null || \
  aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=kisaanmitra-cache-sg" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

echo "Security Group: $SG_ID"

# Allow Redis port from Lambda
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 6379 \
  --source-group $SG_ID \
  --region $REGION \
  2>/dev/null || echo "Ingress rule already exists"

echo "✓ Security group configured"

# 5. Create ElastiCache Redis Cluster
echo ""
echo "5️⃣ Creating ElastiCache Redis Cluster..."
echo "⏳ This may take 5-10 minutes..."

aws elasticache create-cache-cluster \
  --cache-cluster-id kisaanmitra-cache \
  --cache-node-type cache.t4g.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --cache-subnet-group-name kisaanmitra-cache-subnet \
  --security-group-ids $SG_ID \
  --tags Key=Project,Value=KisaanMitra Key=Environment,Value=Production \
  --region $REGION \
  2>/dev/null || echo "Cache cluster already exists"

echo "✓ ElastiCache cluster creation initiated"

# 6. Wait for cluster to be available
echo ""
echo "⏳ Waiting for cluster to be available..."
aws elasticache wait cache-cluster-available \
  --cache-cluster-id kisaanmitra-cache \
  --region $REGION || true

# Get Redis endpoint
REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
  --cache-cluster-id kisaanmitra-cache \
  --show-cache-node-info \
  --region $REGION \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
  --output text 2>/dev/null || echo "pending")

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📊 Resources Created:"
echo "   • SQS Queue: kisaanmitra-messages"
echo "   • Dead Letter Queue: kisaanmitra-messages-dlq"
echo "   • ElastiCache Cluster: kisaanmitra-cache"
echo "   • Security Group: $SG_ID"
echo ""
echo "🔗 Endpoints:"
echo "   • Queue URL: $QUEUE_URL"
echo "   • Redis Endpoint: $REDIS_ENDPOINT:6379"
echo ""
echo "📝 Next Steps:"
echo "   1. Update Lambda environment variables:"
echo "      QUEUE_URL=$QUEUE_URL"
echo "      REDIS_ENDPOINT=$REDIS_ENDPOINT"
echo ""
echo "   2. Update Lambda VPC configuration to use:"
echo "      VPC: $VPC_ID"
echo "      Security Group: $SG_ID"
echo ""
echo "   3. Add SQS trigger to Lambda functions"
echo ""
echo "   4. Install redis-py in Lambda: pip install redis"
