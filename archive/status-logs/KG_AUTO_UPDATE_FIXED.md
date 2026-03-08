# Knowledge Graph Auto-Update Fixed ✅

## Problem
The Knowledge Graph dashboard was showing outdated data because:
1. Lambda didn't have S3 write permissions
2. No automatic update schedule was configured
3. Data was stale from initial deployment

## Solution Implemented

### 1. Fixed Lambda Permissions ✅
Added S3 write permissions to the KG updater Lambda role:
```json
{
  "Effect": "Allow",
  "Action": ["s3:PutObject", "s3:PutObjectAcl"],
  "Resource": "arn:aws:s3:::kisaanmitra-web-demo-1772974554/*"
}
```

### 2. Set Up Automatic Updates ✅
Created EventBridge rule to run Lambda every hour:
- **Rule:** kisaanmitra-kg-update-hourly
- **Schedule:** Every 1 hour
- **Target:** kisaanmitra-kg-updater Lambda
- **Status:** ENABLED

### 3. Manual Update Script ✅
Created `update_kg_data.sh` for manual updates:
```bash
./update_kg_data.sh
```

## Current Data (Updated)

### Statistics:
- **Total Farmers:** 6
- **Total Districts:** 2
- **Total Villages:** 2
- **Total Crops:** 4
- **Total Land:** 119 acres
- **Total Conversations:** 100+

### Last Updated:
March 8, 2026 - 22:06 IST

## How It Works

### Automatic Updates (Every Hour):
```
EventBridge Rule (hourly)
    ↓
Trigger Lambda: kisaanmitra-kg-updater
    ↓
Fetch data from DynamoDB:
  - kisaanmitra-farmer-profiles
  - kisaanmitra-conversations
    ↓
Generate kg_data_live.json
    ↓
Upload to S3
    ↓
CloudFront serves updated data
    ↓
KG Dashboard shows latest info
```

### Manual Updates:
```bash
# Run the update script
./update_kg_data.sh

# Or invoke Lambda directly
aws lambda invoke \
  --function-name kisaanmitra-kg-updater \
  --region ap-south-1 \
  /tmp/response.json
```

## Data Structure

### kg_data_live.json:
```json
{
  "timestamp": "2026-03-08T16:06:29Z",
  "stats": {
    "total_farmers": 6,
    "total_conversations": 100,
    "active_users": 6
  },
  "farmers": [
    {
      "user_id": "919000000002",
      "name": "Nandani",
      "village": "Sangli",
      "district": "Sangli",
      "state": "Maharashtra",
      "crops": ["Tomato", "Onion"],
      "farm_size": 5
    }
  ],
  "recent_queries": [
    {
      "user_id": "919000000002",
      "query": "What is the current price of tomato?",
      "timestamp": "2026-03-08T15:26:01",
      "agent": "market"
    }
  ]
}
```

## Files Created

### Scripts:
- `update_kg_data.sh` - Manual update script
- `fix_kg_updater_permissions.sh` - Permission fix script

### Lambda:
- `src/lambda/lambda_kg_updater.py` - KG updater Lambda function
- `src/lambda/deploy_kg_updater.sh` - Deployment script

## URLs

### Knowledge Graph Dashboard:
- **CloudFront:** https://d28gkw3jboipw5.cloudfront.net/knowledge-graph.html
- **S3 Direct:** https://kisaanmitra-web-demo-1772974554.s3.ap-south-1.amazonaws.com/knowledge-graph.html

### Live Data API:
- **CloudFront:** https://d28gkw3jboipw5.cloudfront.net/kg_data_live.json
- **S3 Direct:** https://kisaanmitra-web-demo-1772974554.s3.ap-south-1.amazonaws.com/kg_data_live.json

## Testing

### Verify Auto-Update:
1. Wait 1 hour
2. Check KG dashboard
3. Data should be updated automatically

### Manual Update:
```bash
# Run update script
./update_kg_data.sh

# Check the dashboard
open https://d28gkw3jboipw5.cloudfront.net/knowledge-graph.html
```

### Check Lambda Logs:
```bash
aws logs tail /aws/lambda/kisaanmitra-kg-updater \
  --follow \
  --region ap-south-1
```

## EventBridge Schedule

### Current Schedule:
- **Frequency:** Every 1 hour
- **Next Run:** Top of every hour (e.g., 23:00, 00:00, 01:00)
- **Status:** ENABLED

### Modify Schedule:
```bash
# Change to every 30 minutes
aws events put-rule \
  --name kisaanmitra-kg-update-hourly \
  --schedule-expression "rate(30 minutes)" \
  --region ap-south-1

# Change to daily at midnight
aws events put-rule \
  --name kisaanmitra-kg-update-hourly \
  --schedule-expression "cron(0 0 * * ? *)" \
  --region ap-south-1
```

## Benefits

### For Users:
- ✅ Always see latest farmer data
- ✅ Real-time conversation insights
- ✅ Up-to-date statistics

### For Evaluators:
- ✅ See actual system usage
- ✅ Verify data is being collected
- ✅ Monitor system activity

### For Development:
- ✅ Automatic updates (no manual work)
- ✅ Scalable solution
- ✅ Easy to maintain

## Troubleshooting

### If KG data is stale:
1. Check Lambda logs for errors
2. Run manual update: `./update_kg_data.sh`
3. Verify EventBridge rule is enabled
4. Check S3 file timestamp

### If Lambda fails:
1. Check IAM permissions
2. Verify DynamoDB tables exist
3. Check Lambda timeout (should be 60s+)
4. Review CloudWatch logs

## Status: FIXED AND AUTOMATED ✅

The Knowledge Graph now updates automatically every hour with the latest data from DynamoDB. Manual updates are also available via the update script.

**Last Updated:** March 8, 2026 - 22:10 IST
