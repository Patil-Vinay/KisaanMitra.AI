# 👥 KisaanMitra - User Management Guide

## Current Users Overview

### Total Registered Users: 3

| Name | Phone | Village | District | Crops | Land |
|------|-------|---------|----------|-------|------|
| Vinay Patil | +91 9000000001 | Nandani | Sangli | Sugarcane | 50 acres |
| Aditya | +91 9000000003 | Alibaug | Mumbai | Mango | 5 acres |
| Parth Nikam | +91 9000000002 | Nandani | Sangli | Sugarcane | 20 acres |

---

## Quick Commands

### List All Users
```bash
./scripts/list_all_users.sh
```

### Export Users (JSON, CSV, Markdown)
```bash
./scripts/export_users.sh
```

### Get User Count
```bash
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --select COUNT
```

### Get Specific User Details
```bash
# Parth Nikam
aws dynamodb get-item \
    --table-name kisaanmitra-farmer-profiles \
    --key '{"user_id": {"S": "919000000002"}}' \
    --region ap-south-1

# Vinay Patil
aws dynamodb get-item \
    --table-name kisaanmitra-farmer-profiles \
    --key '{"user_id": {"S": "919000000001"}}' \
    --region ap-south-1

# Aditya
aws dynamodb get-item \
    --table-name kisaanmitra-farmer-profiles \
    --key '{"user_id": {"S": "919000000003"}}' \
    --region ap-south-1
```

---

## User Details

### 1. Parth Nikam (Primary Test User)
```
Phone: +91 9000000002
Location: Nandani, Sangli, Maharashtra
Crops: Sugarcane
Past Crops: Rice, Wheat, Sugarcane
Land: 20 acres
Experience: 10 years
Soil: Black Cotton Soil
Irrigation: Drip Irrigation
Challenges: Water management, Market price fluctuations
Status: ✅ Active, Profile Complete
```

**Use for testing:**
- General queries
- Market price inquiries
- Weather updates
- Budget planning
- Disease detection

### 2. Vinay Patil (Large-Scale Farmer)
```
Phone: +91 9000000001
Location: Nandani, Sangli, Maharashtra
Crops: Sugarcane
Past Crops: Rice, Soybean, Sugarcane
Land: 50 acres
Experience: 15 years
Soil: Black Cotton Soil
Irrigation: Drip Irrigation
Challenges: Pest infestations
Status: ✅ Active, Profile Complete
```

**Use for testing:**
- Large-scale farming scenarios
- Pest management
- Advanced irrigation queries
- High-volume market transactions

### 3. Aditya (Fruit Farmer)
```
Phone: +91 9000000003
Location: Alibaug, Mumbai, Maharashtra
Crops: Mango
Land: 5 acres
Status: ✅ Active, Profile Complete
```

**Use for testing:**
- Fruit cultivation queries
- Different geographic location
- Small-scale farming
- Coastal region farming

---

## User Statistics

### Geographic Distribution
- **Sangli District:** 2 users (66.7%)
- **Mumbai District:** 1 user (33.3%)

### Crop Distribution
- **Sugarcane:** 2 farmers (66.7%)
- **Mango:** 1 farmer (33.3%)

### Land Distribution
- **Total Land:** 75 acres
- **Average:** 25 acres per farmer
- **Largest:** 50 acres (Vinay Patil)
- **Smallest:** 5 acres (Aditya)

### Experience Level
- **Most Experienced:** Vinay Patil (15 years)
- **Experienced:** Parth Nikam (10 years)
- **Average:** 12.5 years

---

## User Management Operations

### Add New User
Users are added automatically through WhatsApp onboarding. To manually add:

```bash
aws dynamodb put-item \
    --table-name kisaanmitra-farmer-profiles \
    --item '{
        "user_id": {"S": "91XXXXXXXXXX"},
        "phone": {"S": "91XXXXXXXXXX"},
        "name": {"S": "Farmer Name"},
        "village": {"S": "Village Name"},
        "district": {"S": "District Name"},
        "current_crops": {"S": "Crop Name"},
        "land_acres": {"S": "10"},
        "profile_complete": {"BOOL": true},
        "registered_at": {"S": "2026-03-08T00:00:00"}
    }' \
    --region ap-south-1
```

### Update User Profile
```bash
aws dynamodb update-item \
    --table-name kisaanmitra-farmer-profiles \
    --key '{"user_id": {"S": "919000000002"}}' \
    --update-expression "SET land_acres = :land" \
    --expression-attribute-values '{":land": {"S": "25"}}' \
    --region ap-south-1
```

### Delete User
```bash
aws dynamodb delete-item \
    --table-name kisaanmitra-farmer-profiles \
    --key '{"user_id": {"S": "91XXXXXXXXXX"}}' \
    --region ap-south-1
```

### Clear All Users (Except Parth)
```bash
./scripts/clear_all_except_parth.sh
```

---

## Conversation History

### View User Conversations
```bash
# Get last 10 conversations for Parth
aws dynamodb query \
    --table-name kisaanmitra-conversations \
    --key-condition-expression "user_id = :uid" \
    --expression-attribute-values '{":uid": {"S": "919000000002"}}' \
    --scan-index-forward false \
    --limit 10 \
    --region ap-south-1
```

### Count User Messages
```bash
aws dynamodb query \
    --table-name kisaanmitra-conversations \
    --key-condition-expression "user_id = :uid" \
    --expression-attribute-values '{":uid": {"S": "919000000002"}}' \
    --select COUNT \
    --region ap-south-1
```

---

## Testing Scenarios

### Test with Parth Nikam (+91 9000000002)
```
1. "Hi" - Get main menu
2. "What's the weather?" - Weather for Nandani, Sangli
3. "Sugarcane market price" - Get current rates
4. "Budget for 20 acres sugarcane" - Financial planning
5. Send crop image - Disease detection
```

### Test with Vinay Patil (+91 9000000001)
```
1. "Hi" - Get main menu
2. "Pest control for sugarcane" - Pest management
3. "Market forecast for next week" - Price prediction
4. "Best irrigation schedule" - Water management
```

### Test with Aditya (+91 9000000003)
```
1. "Hi" - Get main menu
2. "Mango market price" - Different crop
3. "Weather in Alibaug" - Different location
4. "Mango cultivation tips" - Fruit farming
```

---

## Dashboard Access

### View Users in Streamlit Dashboard
```bash
cd dashboard
streamlit run streamlit_app.py
```

Navigate to "Users" page to see:
- Complete user list with all details
- Export to CSV functionality
- Real-time data from DynamoDB
- User statistics and charts

### View in Knowledge Graph
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
```

---

## Exported Data

All user data is exported to `exports/` directory:

- **JSON:** `exports/all_users.json` - Full data with all fields
- **CSV:** `exports/all_users.csv` - Spreadsheet format
- **Markdown:** `exports/all_users.md` - Table format

### Re-export Data
```bash
./scripts/export_users.sh
```

---

## User Onboarding Status

### Check Onboarding State
```bash
aws dynamodb get-item \
    --table-name kisaanmitra-onboarding \
    --key '{"user_id": {"S": "919000000002"}}' \
    --region ap-south-1
```

### All Users Onboarding Status
```bash
aws dynamodb scan \
    --table-name kisaanmitra-onboarding \
    --region ap-south-1
```

---

## Backup & Restore

### Backup All Users
```bash
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --output json > backup_users_$(date +%Y%m%d).json
```

### Restore User
```bash
# Extract user data from backup and restore
aws dynamodb put-item \
    --table-name kisaanmitra-farmer-profiles \
    --item file://user_data.json \
    --region ap-south-1
```

---

## Monitoring

### Active Users (Last 7 Days)
```bash
# Check conversations in last 7 days
aws dynamodb scan \
    --table-name kisaanmitra-conversations \
    --filter-expression "timestamp > :week_ago" \
    --expression-attribute-values '{":week_ago": {"S": "2026-03-01"}}' \
    --select COUNT \
    --region ap-south-1
```

### User Engagement Metrics
```bash
# Total conversations per user
for user in 919000000002 919000000001 919000000003; do
    echo "User: $user"
    aws dynamodb query \
        --table-name kisaanmitra-conversations \
        --key-condition-expression "user_id = :uid" \
        --expression-attribute-values "{\":uid\": {\"S\": \"$user\"}}" \
        --select COUNT \
        --region ap-south-1 \
        --query 'Count'
    echo ""
done
```

---

## Support & Troubleshooting

### User Can't Login
1. Check if user exists in farmer-profiles table
2. Check onboarding status
3. Verify phone number format (91XXXXXXXXXX)
4. Check WhatsApp webhook logs

### User Profile Incomplete
1. Check onboarding table for current state
2. Restart onboarding: Delete from onboarding table
3. User sends "Hi" to restart

### User Data Not Showing
1. Verify table name and region
2. Check IAM permissions
3. Test with AWS CLI directly
4. Check dashboard logs

---

## Quick Reference

### User Phone Numbers
- Parth Nikam: +91 9000000002
- Vinay Patil: +91 9000000001
- Aditya: +91 9000000003

### DynamoDB Tables
- Profiles: `kisaanmitra-farmer-profiles`
- Conversations: `kisaanmitra-conversations`
- Onboarding: `kisaanmitra-onboarding`

### Region
- All tables: `ap-south-1` (Mumbai)

---

**Last Updated:** March 8, 2026  
**Total Users:** 3  
**Active Users:** 3  
**Profile Completion:** 100%