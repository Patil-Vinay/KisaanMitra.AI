#!/bin/bash

# Quick Deploy Script for KisaanMitra Streamlit Dashboard
# Run this to deploy to AWS EC2 in one command

set -e

echo "🚀 KisaanMitra Streamlit Dashboard - Quick Deploy"
echo "================================================"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured"
    echo ""
    echo "Please run: aws configure"
    echo ""
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region: ap-south-1"
    echo ""
    exit 1
fi

echo "✅ AWS CLI configured"
echo ""

# Show current AWS account
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)

echo "📋 Deployment Details:"
echo "  AWS Account: $ACCOUNT_ID"
echo "  Region: $REGION"
echo "  Instance Type: t3.small"
echo "  Estimated Cost: ~$10-15/month"
echo ""

# Confirm deployment
read -p "Do you want to proceed with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting deployment..."
echo ""

# Run the deployment script
cd dashboard
./deploy_streamlit_to_aws.sh

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📖 For more details, see: STREAMLIT_AWS_DEPLOYMENT.md"
