#!/bin/bash

# List all registered users from KisaanMitra

echo "📋 KisaanMitra - All Registered Users"
echo "======================================"
echo ""

# Fetch all users
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --output json | \
python3 -c "
import json
import sys

data = json.load(sys.stdin)
items = data.get('Items', [])

print(f'Total Users: {len(items)}\n')

for i, item in enumerate(items, 1):
    name = item.get('name', {}).get('S', 'N/A')
    phone = item.get('phone', {}).get('S', 'N/A')
    village = item.get('village', {}).get('S', 'N/A')
    district = item.get('district', {}).get('S', 'N/A')
    crops = item.get('current_crops', {}).get('S', 'N/A')
    land = item.get('land_acres', {}).get('S', 'N/A')
    
    print(f'{i}. {name}')
    print(f'   Phone: {phone}')
    print(f'   Location: {village}, {district}')
    print(f'   Crops: {crops}')
    print(f'   Land: {land} acres')
    print()
"