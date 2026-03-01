#!/bin/bash

# Clear all users except Parth (919000000001)
# This will reset Vinay and any other test users

REGION="ap-south-1"
TABLE="kisaanmitra-conversations"
KEEP_USER="919000000001"

echo "🔍 Fetching all users..."

# Get all unique user IDs
USERS=$(aws dynamodb scan \
    --table-name $TABLE \
    --region $REGION \
    --select "SPECIFIC_ATTRIBUTES" \
    --projection-expression "user_id" \
    --output json | jq -r '.Items[].user_id.S' | sort -u)

echo ""
echo "📋 Users found:"
for user in $USERS; do
    if [ "$user" == "$KEEP_USER" ]; then
        echo "  ✓ $user (Parth - will keep)"
    else
        echo "  ✗ $user (will delete)"
    fi
done

echo ""
read -p "⚠️  Delete all users except Parth? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""

# Delete each user except Parth
for user in $USERS; do
    if [ "$user" == "$KEEP_USER" ]; then
        echo "⏭️  Skipping Parth ($user)"
        continue
    fi
    
    echo "🗑️  Deleting user: $user"
    
    # Get all items for this user
    ITEMS=$(aws dynamodb query \
        --table-name $TABLE \
        --region $REGION \
        --key-condition-expression "user_id = :uid" \
        --expression-attribute-values "{\":uid\":{\"S\":\"$user\"}}" \
        --projection-expression "user_id, #ts" \
        --expression-attribute-names '{"#ts":"timestamp"}' \
        --output json)
    
    # Count items
    COUNT=$(echo $ITEMS | jq '.Items | length')
    echo "   Found $COUNT items"
    
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
    done
    
    echo "   ✅ Deleted $COUNT items"
    echo ""
done

echo "✅ Cleanup complete!"
echo ""
echo "📊 Remaining users:"
aws dynamodb scan \
    --table-name $TABLE \
    --region $REGION \
    --select "SPECIFIC_ATTRIBUTES" \
    --projection-expression "user_id" \
    --output json | jq -r '.Items[].user_id.S' | sort -u | while read user; do
    COUNT=$(aws dynamodb query \
        --table-name $TABLE \
        --region $REGION \
        --key-condition-expression "user_id = :uid" \
        --expression-attribute-values "{\":uid\":{\"S\":\"$user\"}}" \
        --select "COUNT" \
        --output json | jq -r '.Count')
    echo "  ✓ $user ($COUNT messages)"
done
