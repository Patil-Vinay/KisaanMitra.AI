#!/bin/bash

# Clear all KisaanMitra DynamoDB tables
echo "🗑️  Clearing all KisaanMitra DynamoDB tables..."

REGION="ap-south-1"
TABLES=(
    "kisaanmitra-conversations"
    "kisaanmitra-market-data"
    "kisaanmitra-finance"
    "kisaanmitra-onboarding"
)

for TABLE in "${TABLES[@]}"; do
    echo ""
    echo "📋 Clearing table: $TABLE"
    
    # Get table key schema
    KEY_SCHEMA=$(aws dynamodb describe-table --table-name "$TABLE" --region "$REGION" --query "Table.KeySchema" --output json)
    HASH_KEY=$(echo "$KEY_SCHEMA" | jq -r '.[] | select(.KeyType == "HASH") | .AttributeName')
    RANGE_KEY=$(echo "$KEY_SCHEMA" | jq -r '.[] | select(.KeyType == "RANGE") | .AttributeName')
    
    echo "   Hash key: $HASH_KEY"
    if [ "$RANGE_KEY" != "null" ] && [ -n "$RANGE_KEY" ]; then
        echo "   Range key: $RANGE_KEY"
    fi
    
    # Scan and delete all items
    SCAN_OUTPUT=$(aws dynamodb scan --table-name "$TABLE" --region "$REGION" --output json)
    COUNT=$(echo "$SCAN_OUTPUT" | jq '.Items | length')
    
    if [ "$COUNT" -eq 0 ]; then
        echo "   ✅ Already empty (0 items)"
        continue
    fi
    
    echo "   Found $COUNT items to delete..."
    
    DELETED=0
    
    # Handle tables with composite keys
    if [ "$RANGE_KEY" != "null" ] && [ -n "$RANGE_KEY" ]; then
        # Composite key (hash + range)
        while IFS= read -r item; do
            HASH_VALUE=$(echo "$item" | jq -r ".$HASH_KEY | to_entries[0].value")
            HASH_TYPE=$(echo "$item" | jq -r ".$HASH_KEY | to_entries[0].key")
            RANGE_VALUE=$(echo "$item" | jq -r ".$RANGE_KEY | to_entries[0].value")
            RANGE_TYPE=$(echo "$item" | jq -r ".$RANGE_KEY | to_entries[0].key")
            
            KEY_JSON="{\"$HASH_KEY\":{\"$HASH_TYPE\":\"$HASH_VALUE\"},\"$RANGE_KEY\":{\"$RANGE_TYPE\":\"$RANGE_VALUE\"}}"
            
            aws dynamodb delete-item --table-name "$TABLE" --key "$KEY_JSON" --region "$REGION" > /dev/null 2>&1
            DELETED=$((DELETED + 1))
            echo -ne "   Deleting... $DELETED/$COUNT\r"
        done < <(echo "$SCAN_OUTPUT" | jq -c '.Items[]')
    else
        # Simple key (hash only)
        while IFS= read -r item; do
            HASH_VALUE=$(echo "$item" | jq -r ".$HASH_KEY | to_entries[0].value")
            HASH_TYPE=$(echo "$item" | jq -r ".$HASH_KEY | to_entries[0].key")
            
            KEY_JSON="{\"$HASH_KEY\":{\"$HASH_TYPE\":\"$HASH_VALUE\"}}"
            
            aws dynamodb delete-item --table-name "$TABLE" --key "$KEY_JSON" --region "$REGION" > /dev/null 2>&1
            DELETED=$((DELETED + 1))
            echo -ne "   Deleting... $DELETED/$COUNT\r"
        done < <(echo "$SCAN_OUTPUT" | jq -c '.Items[]')
    fi
    
    echo ""
    echo "   ✅ Deleted $DELETED items"
done

echo ""
echo "🎉 All tables cleared!"
echo ""
echo "📊 Verification:"
for TABLE in "${TABLES[@]}"; do
    COUNT=$(aws dynamodb scan --table-name "$TABLE" --region "$REGION" --select COUNT --query "Count" --output text)
    echo "   $TABLE: $COUNT items"
done
