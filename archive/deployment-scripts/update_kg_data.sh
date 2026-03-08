#!/bin/bash
# Update Knowledge Graph data from DynamoDB

echo "Fetching latest Knowledge Graph data from DynamoDB..."

# Fetch farmer profiles
aws dynamodb scan \
  --table-name kisaanmitra-farmer-profiles \
  --region ap-south-1 \
  --max-items 100 \
  --output json > /tmp/kg_profiles.json

# Fetch conversations
aws dynamodb scan \
  --table-name kisaanmitra-conversations \
  --region ap-south-1 \
  --max-items 100 \
  --output json > /tmp/kg_conversations.json

# Count items
PROFILE_COUNT=$(cat /tmp/kg_profiles.json | jq '.Items | length')
CONVERSATION_COUNT=$(cat /tmp/kg_conversations.json | jq '.Items | length')

echo "Found $PROFILE_COUNT farmer profiles"
echo "Found $CONVERSATION_COUNT conversations"

# Create simplified KG data
cat > /tmp/kg_data_live.json <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "stats": {
    "total_farmers": $PROFILE_COUNT,
    "total_conversations": $CONVERSATION_COUNT,
    "active_users": $PROFILE_COUNT
  },
  "farmers": $(cat /tmp/kg_profiles.json | jq '[.Items[] | {
    user_id: .user_id.S,
    name: .name.S,
    village: .village.S,
    district: .district.S,
    state: .state.S,
    crops: (.crops.L // [] | map(.S)),
    farm_size: (.farm_size.N // "0" | tonumber)
  }]'),
  "recent_queries": $(cat /tmp/kg_conversations.json | jq '[.Items[] | {
    user_id: .user_id.S,
    query: .user_message.S,
    timestamp: .timestamp.S,
    agent: .agent.S
  }] | sort_by(.timestamp) | reverse | .[0:20]')
}
EOF

echo "Generated KG data file"

# Upload to S3
aws s3 cp /tmp/kg_data_live.json s3://kisaanmitra-web-demo-1772974554/kg_data_live.json \
  --region ap-south-1 \
  --content-type "application/json"

echo "✅ Knowledge Graph data updated successfully!"
echo "View at: https://d28gkw3jboipw5.cloudfront.net/knowledge-graph.html"

# Cleanup
rm /tmp/kg_profiles.json /tmp/kg_conversations.json /tmp/kg_data_live.json
