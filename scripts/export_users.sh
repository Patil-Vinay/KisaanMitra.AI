#!/bin/bash

# Export KisaanMitra users in various formats

echo "📊 KisaanMitra - Export Users"
echo "=============================="
echo ""

# Create exports directory
mkdir -p exports

# Export to JSON
echo "Exporting to JSON..."
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --output json > exports/all_users.json

echo "✅ Exported to: exports/all_users.json"

# Export to CSV
echo "Exporting to CSV..."
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --output json | \
python3 -c "
import json
import sys
import csv

data = json.load(sys.stdin)
items = data.get('Items', [])

with open('exports/all_users.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Phone', 'Village', 'District', 'Crops', 'Land (acres)', 'Experience', 'Registered'])
    
    for item in items:
        writer.writerow([
            item.get('name', {}).get('S', ''),
            item.get('phone', {}).get('S', ''),
            item.get('village', {}).get('S', ''),
            item.get('district', {}).get('S', ''),
            item.get('current_crops', {}).get('S', ''),
            item.get('land_acres', {}).get('S', ''),
            item.get('experience', {}).get('S', ''),
            item.get('registered_at', {}).get('S', '')
        ])

print('✅ Exported to: exports/all_users.csv')
"

# Export to Markdown table
echo "Exporting to Markdown..."
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --output json | \
python3 -c "
import json
import sys

data = json.load(sys.stdin)
items = data.get('Items', [])

with open('exports/all_users.md', 'w') as f:
    f.write('# KisaanMitra Users\n\n')
    f.write('| Name | Phone | Village | District | Crops | Land |\n')
    f.write('|------|-------|---------|----------|-------|------|\n')
    
    for item in items:
        name = item.get('name', {}).get('S', '')
        phone = item.get('phone', {}).get('S', '')
        village = item.get('village', {}).get('S', '')
        district = item.get('district', {}).get('S', '')
        crops = item.get('current_crops', {}).get('S', '')
        land = item.get('land_acres', {}).get('S', '')
        
        f.write(f'| {name} | {phone} | {village} | {district} | {crops} | {land} acres |\n')

print('✅ Exported to: exports/all_users.md')
"

echo ""
echo "📁 All exports saved to: exports/"
echo ""
ls -lh exports/