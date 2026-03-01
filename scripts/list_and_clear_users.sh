#!/bin/bash

# List all users and optionally clear one
# Usage: ./list_and_clear_users.sh

REGION="ap-south-1"
TABLE="kisaanmitra-conversations"

echo "🔍 Fetching all users from DynamoDB..."
echo ""

# Get unique user IDs
USERS=$(aws dynamodb scan \
    --table-name $TABLE \
    --region $REGION \
    --select "SPECIFIC_ATTRIBUTES" \
    --projection-expression "user_id" \
    --output json | jq -r '.Items[].user_id.S' | sort -u)

if [ -z "$USERS" ]; then
    echo "❌ No users found"
    exit 0
fi

echo "📋 Users in database:"
echo ""

# Array to store users
declare -a USER_ARRAY
INDEX=1

# List each user with their message count
for user in $USERS; do
    USER_ARRAY[$INDEX]=$user
    
    # Get message count
    COUNT=$(aws dynamodb query \
        --table-name $TABLE \
        --region $REGION \
        --key-condition-expression "user_id = :uid" \
        --expression-attribute-values "{\":uid\":{\"S\":\"$user\"}}" \
        --select "COUNT" \
        --output json | jq -r '.Count')
    
    # Get first message
    FIRST_MSG=$(aws dynamodb query \
        --table-name $TABLE \
        --region $REGION \
        --key-condition-expression "user_id = :uid" \
        --expression-attribute-values "{\":uid\":{\"S\":\"$user\"}}" \
        --limit 1 \
        --output json | jq -r '.Items[0].message.S // "N/A"')
    
    echo "$INDEX. User: +$user"
    echo "   Messages: $COUNT"
    echo "   First message: ${FIRST_MSG:0:50}..."
    echo ""
    
    INDEX=$((INDEX + 1))
done

echo ""
read -p "Enter user number to clear (or 0 to exit): " CHOICE

if [ "$CHOICE" -eq 0 ]; then
    echo "❌ Cancelled"
    exit 0
fi

if [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -ge "$INDEX" ]; then
    echo "❌ Invalid choice"
    exit 1
fi

SELECTED_USER=${USER_ARRAY[$CHOICE]}

echo ""
echo "⚠️  You selected: +$SELECTED_USER"
read -p "Are you sure you want to delete ALL data for this user? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "🗑️  Deleting all data for user: $SELECTED_USER"

# Get all items for this user
ITEMS=$(aws dynamodb query \
    --table-name $TABLE \
    --region $REGION \
    --key-condition-expression "user_id = :uid" \
    --expression-attribute-values "{\":uid\":{\"S\":\"$SELECTED_USER\"}}" \
    --projection-expression "user_id, #ts" \
    --expression-attribute-names '{"#ts":"timestamp"}' \
    --output json)

# Delete each item
DELETED=0
echo $ITEMS | jq -r '.Items[] | @json' | while read item; do
    USER_ID_VAL=$(echo $item | jq -r '.user_id.S')
    TIMESTAMP_VAL=$(echo $item | jq -r '.timestamp.S')
    
    aws dynamodb delete-item \
        --table-name $TABLE \
        --region $REGION \
        --key "{\"user_id\":{\"S\":\"$USER_ID_VAL\"},\"timestamp\":{\"S\":\"$TIMESTAMP_VAL\"}}" \
        > /dev/null 2>&1
    
    DELETED=$((DELETED + 1))
    echo "  ✓ Deleted item $DELETED"
done

echo ""
echo "✅ All data deleted for user: +$SELECTED_USER"
echo ""
echo "📝 User can start fresh by sending a new message to the WhatsApp bot"
