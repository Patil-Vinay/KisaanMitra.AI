#!/bin/bash

# Setup Amazon Neptune for Knowledge Graph
# This creates a Neptune cluster for village-level knowledge graph

echo "Setting up Amazon Neptune cluster..."

# Configuration
CLUSTER_ID="kisaanmitra-knowledge-graph"
INSTANCE_CLASS="db.t3.medium"  # Cost-effective for development
REGION="ap-south-1"

# Create Neptune subnet group (requires VPC)
echo "Creating Neptune subnet group..."
aws neptune create-db-subnet-group \
    --db-subnet-group-name kisaanmitra-neptune-subnet \
    --db-subnet-group-description "Subnet group for KisaanMitra Neptune" \
    --subnet-ids subnet-xxxxx subnet-yyyyy \
    --region $REGION

# Create Neptune cluster
echo "Creating Neptune cluster..."
aws neptune create-db-cluster \
    --db-cluster-identifier $CLUSTER_ID \
    --engine neptune \
    --engine-version 1.2.1.0 \
    --db-subnet-group-name kisaanmitra-neptune-subnet \
    --vpc-security-group-ids sg-xxxxx \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "mon:04:00-mon:05:00" \
    --enable-cloudwatch-logs-exports '["audit"]' \
    --tags Key=Project,Value=KisaanMitra Key=Purpose,Value=KnowledgeGraph \
    --region $REGION

echo "Waiting for cluster to be available..."
aws neptune wait db-cluster-available \
    --db-cluster-identifier $CLUSTER_ID \
    --region $REGION

# Create Neptune instance
echo "Creating Neptune instance..."
aws neptune create-db-instance \
    --db-instance-identifier ${CLUSTER_ID}-instance-1 \
    --db-instance-class $INSTANCE_CLASS \
    --engine neptune \
    --db-cluster-identifier $CLUSTER_ID \
    --region $REGION

echo "Waiting for instance to be available..."
aws neptune wait db-instance-available \
    --db-instance-identifier ${CLUSTER_ID}-instance-1 \
    --region $REGION

# Get cluster endpoint
ENDPOINT=$(aws neptune describe-db-clusters \
    --db-cluster-identifier $CLUSTER_ID \
    --query 'DBClusters[0].Endpoint' \
    --output text \
    --region $REGION)

echo ""
echo "✅ Neptune cluster created successfully!"
echo ""
echo "Cluster Details:"
echo "  Cluster ID: $CLUSTER_ID"
echo "  Endpoint: $ENDPOINT"
echo "  Port: 8182"
echo "  Region: $REGION"
echo ""
echo "Connection String:"
echo "  wss://$ENDPOINT:8182/gremlin"
echo ""
echo "Next steps:"
echo "  1. Update src/knowledge_graph/village_graph.py with endpoint: $ENDPOINT"
echo "  2. Update Lambda environment variable: NEPTUNE_ENDPOINT=$ENDPOINT"
echo "  3. Ensure Lambda has VPC access to Neptune"
echo ""
echo "⚠️  IMPORTANT: Neptune is in a VPC. Lambda must be in same VPC to access it."
echo "⚠️  Cost: ~$0.10/hour (~$73/month) for db.t3.medium instance"
