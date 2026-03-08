# Knowledge Graph Dashboard Updated ✅

## URL
**http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com/**

## Status: LIVE WITH REAL DATA

The Knowledge Graph dashboard is now showing real, live data from your DynamoDB tables instead of the old dummy data.

## What Changed

### Before (Old Dummy Data):
- 10,000 fake farmers
- 8 districts
- 187 villages
- 30 crops
- 184,409 acres
- Static data from March 2, 2026

### After (Real Live Data):
- **6 real farmers** (actual registered users)
- **2 districts** (Sangli, Mumbai)
- **2 villages** (Nandani, Alibaug)
- **4 crops** (Sugarcane, Onion, Tomato, Mango)
- **119 acres** (actual farm sizes)
- **Auto-updates every hour**

## Current Data (Live)

### Farmers:
1. Nandani - Sangli, Maharashtra (Sugarcane, Onion, Tomato)
2. Parth - Sangli, Maharashtra (Sugarcane)
3. Vinay - Sangli, Maharashtra (Sugarcane)
4. Aditya - Sangli, Maharashtra (Sugarcane)
5. Test User - Sangli, Maharashtra (Tomato)
6. Mango Farmer - Alibaug, Mumbai (Mango)

### Statistics:
- **Total Land:** 119 acres
- **Districts:** Sangli (114 acres), Mumbai (5 acres)
- **Most Common Crop:** Sugarcane (101.5 acres)
- **Last Updated:** March 8, 2026 - 22:15 IST

## Auto-Update System

### How It Works:
```
EventBridge Rule (every hour)
    ↓
Lambda: kisaanmitra-kg-updater
    ↓
Fetch from DynamoDB:
  - kisaanmitra-farmer-profiles
  - kisaanmitra-conversations
    ↓
Generate knowledge graph JSON
    ↓
Upload to S3: knowledge_graph_dummy_data.json
    ↓
Dashboard shows updated data
```

### Update Schedule:
- **Frequency:** Every 1 hour
- **Next Update:** Top of every hour
- **Manual Update:** `./update_kg_data.sh`

## Data Structure

The dashboard now shows:

### Network Graph:
- **Districts** (green nodes) → **Villages** (blue nodes) → **Crops** (orange nodes)
- Node size = number of farmers
- Links show relationships

### Statistics Cards:
- Total Farmers: 6
- Districts: 2
- Villages: 2
- Crop Types: 4
- Total Acres: 119
- Avg Success: 72.5%

### Interactive Features:
- ✅ Drag nodes to rearrange
- ✅ Scroll to zoom
- ✅ Click to highlight connections
- ✅ Search nodes
- ✅ Filter by type
- ✅ Reset view
- ✅ Toggle clustering
- ✅ Export PNG

## Technical Details

### S3 Bucket:
- **Name:** kisaanmitra-knowledge-graph
- **File:** knowledge_graph_dummy_data.json
- **Region:** ap-south-1
- **Access:** Public read

### Lambda Function:
- **Name:** kisaanmitra-kg-updater
- **Runtime:** Python 3.9
- **Timeout:** 60 seconds
- **Memory:** 256 MB
- **Trigger:** EventBridge (hourly)

### DynamoDB Tables:
- **kisaanmitra-farmer-profiles** - User registration data
- **kisaanmitra-conversations** - Chat history

## Viewing the Dashboard

### Main URL:
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com/
```

### Direct Data API:
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com/knowledge_graph_dummy_data.json
```

## Manual Update

To manually update the KG data:

```bash
# Run the update script
./update_kg_data.sh

# Or invoke Lambda directly
aws lambda invoke \
  --function-name kisaanmitra-kg-updater \
  --region ap-south-1 \
  /tmp/response.json
```

## Data Growth

As more farmers register and use the system:
- Farmer count will increase
- More districts and villages will appear
- Crop diversity will grow
- Network graph will expand
- Statistics will update automatically

## Benefits

### For Evaluators:
- ✅ See real system usage
- ✅ Verify data collection works
- ✅ Monitor actual farmer activity
- ✅ Understand geographic distribution

### For Development:
- ✅ Real-time insights
- ✅ Data validation
- ✅ System health monitoring
- ✅ Growth tracking

### For Farmers:
- ✅ See community size
- ✅ Find nearby farmers
- ✅ Discover crop patterns
- ✅ Regional insights

## Comparison

| Metric | Old (Dummy) | New (Real) |
|--------|-------------|------------|
| Farmers | 10,000 | 6 |
| Districts | 8 | 2 |
| Villages | 187 | 2 |
| Crops | 30 | 4 |
| Land | 184,409 acres | 119 acres |
| Updates | Static | Hourly |
| Data Source | Fake | DynamoDB |

## Next Steps

1. ✅ Dashboard is live with real data
2. ✅ Auto-updates every hour
3. ✅ Manual update script available
4. 📈 Data will grow as more farmers register
5. 🔄 System continuously monitors and updates

## Status: DEPLOYED AND WORKING ✅

The Knowledge Graph dashboard now displays real, live data from your production system and updates automatically every hour.

**Last Updated:** March 8, 2026 - 22:15 IST
