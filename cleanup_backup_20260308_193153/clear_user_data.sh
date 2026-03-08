#!/bin/bash

# Clear user data from DynamoDB
# Usage: ./clear_user_data.sh <phone_number>

if [ -z "$1" ]; then
    echo "Usage: ./clear_user_data.sh <phone_number>"
    echo "Example: ./clear_user_data.sh 919876543210"
    exit 1
fi

USER_ID=$1
REGION="ap-south-1"
TABLE="kisaanmitra-conversations"

echo "🔍 Searching for user: $USER_ID"

# Query all items for this user
ITEMS=$(aws dynamodb query \
    --table-name $TABLE \
    --region $REGION \
    --key-condition-expression "user_id = :uid" \
    --expression-attribute-values "{\":uid\":{\"S\":\"$USER_ID\"}}" \
    --projection-expression "user_id, #ts" \
    --expression-attribute-names '{"#ts":"timestamp"}' \
    --output json)

# Count items
COUNT=$(echo $ITEMS | jq '.Items | length')

if [ "$COUNT" -eq 0 ]; then
    echo "❌ No data found for user: $USER_ID"
    exit 0
fi

echo "📊 Found $COUNT items for user: $USER_ID"
echo ""
read -p "⚠️  Are you sure you want to delete all data for this user? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "🗑️  Deleting items..."

# Delete each item
echo $ITEMS | jq -r '.Items[] | @json' | while read item; do
    USER_ID_VAL=$(echo $item | jq -r '.user_id.S')
    TIMESTAMP_VAL=$(echo $item | jq -r '.timestamp.S')
    
    aws dynamodb delete-item \
        --table-name $TABLE \
        --region $REGION \
        --key "{\"user_id\":{\"S\":\"$USER_ID_VAL\"},\"timestamp\":{\"S\":\"$TIMESTAMP_VAL\"}}" \
        > /dev/null 2>&1
    
    echo "  ✓ Deleted item with timestamp: $TIMESTAMP_VAL"
done

echo ""
echo "✅ All data deleted for user: $USER_ID"
echo ""
echo "📝 Note: User can start fresh by sending a new message"
