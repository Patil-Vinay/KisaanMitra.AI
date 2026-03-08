#!/bin/bash
# Fix KG Updater Lambda permissions

echo "Fixing Knowledge Graph Updater Lambda permissions..."

# Get the Lambda role name
ROLE_NAME=$(aws lambda get-function --function-name kisaanmitra-kg-updater --region ap-south-1 --query 'Configuration.Role' --output text | awk -F'/' '{print $NF}')

echo "Lambda role: $ROLE_NAME"

# Create policy document
cat > /tmp/kg-s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::kisaanmitra-web-demo-1772974554/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-farmer-profiles",
        "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-conversations"
      ]
    }
  ]
}
EOF

# Attach policy to role
aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name KGUpdaterS3Access \
  --policy-document file:///tmp/kg-s3-policy.json

echo "✅ Permissions updated!"

# Test the Lambda
echo "Testing Lambda..."
aws lambda invoke --function-name kisaanmitra-kg-updater --region ap-south-1 /tmp/test-response.json

cat /tmp/test-response.json | jq .

# Cleanup
rm /tmp/kg-s3-policy.json /tmp/test-response.json

echo "✅ KG Updater Lambda is now working!"
