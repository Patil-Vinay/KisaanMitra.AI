#!/bin/bash

# Deploy Knowledge Graph Dashboard to S3
# Makes it publicly accessible via HTTPS

BUCKET_NAME="kisaanmitra-knowledge-graph"
REGION="ap-south-1"

echo "🚀 Deploying Knowledge Graph Dashboard to S3..."

# Create S3 bucket if it doesn't exist
echo "📦 Creating S3 bucket..."
aws s3 mb s3://${BUCKET_NAME} --region ${REGION} 2>/dev/null || echo "Bucket already exists"

# Enable static website hosting
echo "🌐 Enabling static website hosting..."
aws s3 website s3://${BUCKET_NAME} \
    --index-document knowledge_graph_dashboard.html \
    --error-document knowledge_graph_dashboard.html

# Upload files
echo "📤 Uploading dashboard files..."
aws s3 cp knowledge_graph_dashboard.html s3://${BUCKET_NAME}/ --content-type "text/html"
aws s3 cp knowledge_graph_dummy_data.json s3://${BUCKET_NAME}/ --content-type "application/json"

# Make files publicly readable
echo "🔓 Making files public..."
aws s3api put-object-acl --bucket ${BUCKET_NAME} --key knowledge_graph_dashboard.html --acl public-read
aws s3api put-object-acl --bucket ${BUCKET_NAME} --key knowledge_graph_dummy_data.json --acl public-read

# Update bucket policy for public access
echo "📝 Updating bucket policy..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket ${BUCKET_NAME} --policy file:///tmp/bucket-policy.json

# Get the website URL
WEBSITE_URL="http://${BUCKET_NAME}.s3-website.${REGION}.amazonaws.com"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 Dashboard URL:"
echo "   ${WEBSITE_URL}"
echo ""
echo "📊 Direct link:"
echo "   ${WEBSITE_URL}/knowledge_graph_dashboard.html"
echo ""
echo "🎉 Share this link with examiners!"
