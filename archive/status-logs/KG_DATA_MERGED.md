# Knowledge Graph Data Merge - COMPLETE ✅

## Issue Fixed
User was seeing old data (only 6 real farmers) on the Knowledge Graph dashboard instead of the full dataset with 10,000 dummy farmers + real users.

## Root Cause
The Lambda KG updater was only fetching real farmers from DynamoDB and not merging with the original 10,000 dummy farmers.

## Solution Implemented

### 1. Updated Lambda Function (`lambda_kg_updater.py`)
- Added `fetch_dummy_data()` function to load 10k farmers from S3
- Added `fetch_real_farmers()` to get real users from DynamoDB
- Added `convert_dynamodb_to_farmer_format()` to normalize data structure
- Modified `lambda_handler()` to merge both datasets
- Changed cache control to `no-cache, no-store, must-revalidate`

### 2. Data Structure
```
S3 Bucket: kisaanmitra-knowledge-graph
├── dummy_farmers_10k.json (source: 10,000 dummy farmers)
└── knowledge_graph_dummy_data.json (output: merged KG data)
```

### 3. Deployment
```bash
cd src/lambda
./deploy_kg_updater.sh
aws lambda invoke --function-name kisaanmitra-kg-updater --region ap-south-1
```

### 4. Cache Invalidation
```bash
# CloudFront cache cleared
aws cloudfront create-invalidation --distribution-id E17NCPEJL27P1L --paths "/*"
```

## Current Status

### Data Statistics
- **Dummy Farmers**: 10,000
- **Real Farmers**: 6 (Nandani, Parth, Vinay, Aditya, Test User, Mango Farmer)
- **Total Farmers**: 10,006
- **Districts**: 9
- **Villages**: 191
- **Crops**: 31
- **Total Land**: 184,527.92 acres
- **Last Updated**: 2026-03-08T16:22:44

### File Size
- KG Data File: 4.08 MB (4,083,509 bytes)

## How to View Updated Data

### Option 1: Hard Refresh Browser
- **Windows/Linux**: Ctrl + Shift + R
- **Mac**: Cmd + Shift + R

### Option 2: Incognito/Private Mode
Open the KG dashboard in a new incognito window to bypass browser cache

### Option 3: Clear Browser Cache
Clear site data for the KG dashboard URL

## URLs
- **Knowledge Graph Dashboard**: http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com/
- **CloudFront URL**: https://d28gkw3jboipw5.cloudfront.net/knowledge-graph.html

## Auto-Update Schedule
The Lambda runs hourly via EventBridge to keep the KG updated with new real farmers while maintaining the 10k dummy dataset.

## Testing
```bash
# Verify current data
aws s3 cp s3://kisaanmitra-knowledge-graph/knowledge_graph_dummy_data.json - | \
  python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Total: {d[\"metadata\"][\"total_farmers\"]}')"
```

Expected output: `Total: 10006`

## Notes
- Browser caching can cause old data to persist - users must hard refresh
- CloudFront cache invalidation takes 1-2 minutes to propagate
- Lambda automatically merges new real farmers with the 10k dummy dataset
- The dummy data provides realistic scale for demo purposes
