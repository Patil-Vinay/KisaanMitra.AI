#!/bin/bash

# Remove specific users from all tables

USERS=(
    "919000000001"
    "919000000003"
    "919000000002"
)

echo "🗑️  Removing specific users from all tables..."

for USER in "${USERS[@]}"; do
    echo ""
    echo "Removing user: $USER"
    
    # Remove from farmer profiles
    echo "  - Removing from kisaanmitra-farmer-profiles..."
    aws dynamodb delete-item \
        --table-name kisaanmitra-farmer-profiles \
        --key "{\"user_id\": {\"S\": \"$USER\"}}" \
        --region ap-south-1 2>/dev/null
    
    # Remove from onboarding table
    echo "  - Removing from kisaanmitra-onboarding..."
    aws dynamodb delete-item \
        --table-name kisaanmitra-onboarding \
        --key "{\"user_id\": {\"S\": \"$USER\"}}" \
        --region ap-south-1 2>/dev/null
    
    # Remove conversations (scan and delete)
    echo "  - Removing conversations..."
    aws dynamodb query \
        --table-name kisaanmitra-conversations \
        --key-condition-expression "user_id = :uid" \
        --expression-attribute-values "{\":uid\": {\"S\": \"$USER\"}}" \
        --region ap-south-1 \
        --query "Items[*].[user_id.S, timestamp.S]" \
        --output text | while read uid ts; do
            aws dynamodb delete-item \
                --table-name kisaanmitra-conversations \
                --key "{\"user_id\": {\"S\": \"$uid\"}, \"timestamp\": {\"S\": \"$ts\"}}" \
                --region ap-south-1 2>/dev/null
        done
    
    # Remove from finance table
    echo "  - Removing from kisaanmitra-finance..."
    aws dynamodb query \
        --table-name kisaanmitra-finance \
        --key-condition-expression "user_id = :uid" \
        --expression-attribute-values "{\":uid\": {\"S\": \"$USER\"}}" \
        --region ap-south-1 \
        --query "Items[*].[user_id.S, timestamp.S]" \
        --output text | while read uid ts; do
            aws dynamodb delete-item \
                --table-name kisaanmitra-finance \
                --key "{\"user_id\": {\"S\": \"$uid\"}, \"timestamp\": {\"S\": \"$ts\"}}" \
                --region ap-south-1 2>/dev/null
        done
    
    echo "  ✅ User $USER removed"
done

echo ""
echo "✅ All specified users removed successfully!"
echo ""
echo "Remaining users:"
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --query "Items[*].[user_id.S, name.S]" \
    --output table
