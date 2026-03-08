# Knowledge Graph Dashboard - Dynamic Updates

## Overview
The Knowledge Graph dashboard now updates automatically every 5 minutes with real-time data from DynamoDB.

## Architecture

```
DynamoDB (Farmer Profiles)
    ↓
Lambda (KG Updater) - Triggered every 5 minutes by EventBridge
    ↓
S3 (kg_data_live.json) - Updated JSON data
    ↓
Static HTML Dashboard - Fetches latest data on page load
```

## Components

### 1. Lambda Function: `kisaanmitra-kg-updater`
- **File**: `src/lambda/lambda_kg_updater.py`
- **Trigger**: EventBridge (every 5 minutes)
- **Function**: 
  - Fetches all farmers from DynamoDB
  - Generates knowledge graph structure (nodes & links)
  - Uploads JSON to S3

### 2. S3 Data File: `kg_data_live.json`
- **Location**: `s3://kisaanmitra-web-demo-1772974554/kg_data_live.json`
- **Cache**: 60 seconds
- **Format**: JSON with nodes, links, and metadata

### 3. Static Dashboard: `knowledge-graph.html`
- **URL**: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com/knowledge-graph.html
- **Features**:
  - Interactive D3.js network graph
  - Real-time statistics
  - Search and filter capabilities
  - Auto-refresh every 5 minutes

## Deployment

### Deploy Lambda Function
```bash
cd src/lambda
./deploy_kg_updater.sh
```

This will:
1. Create/update the Lambda function
2. Set up EventBridge rule (5-minute schedule)
3. Configure permissions

### Manual Data Update
```bash
# Run locally to update KG data
python3 demo/fetch_kg_data.py
```

### Test Lambda Function
```bash
aws lambda invoke \
  --function-name kisaanmitra-kg-updater \
  --region ap-south-1 \
  response.json

cat response.json
```

## Data Structure

### Nodes
```json
{
  "id": "d_Pune",
  "name": "Pune",
  "type": "district",
  "count": 150,
  "land": 2500.5,
  "group": 1
}
```

### Links
```json
{
  "source": "d_Pune",
  "target": "v_Kharadi|Pune",
  "value": 50
}
```

### Metadata
```json
{
  "total_farmers": 1000,
  "total_districts": 8,
  "total_villages": 187,
  "total_crops": 30,
  "total_land": 18440.5,
  "last_updated": "2026-03-08T14:30:00Z"
}
```

## Access URLs

- **Web Chat Demo**: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com
- **Knowledge Graph**: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com/knowledge-graph.html
- **Live Data JSON**: https://kisaanmitra-web-demo-1772974554.s3.ap-south-1.amazonaws.com/kg_data_live.json

## Monitoring

### View Lambda Logs
```bash
aws logs tail /aws/lambda/kisaanmitra-kg-updater --follow --region ap-south-1
```

### Check EventBridge Rule
```bash
aws events describe-rule --name kg-updater-schedule --region ap-south-1
```

### Verify S3 File
```bash
aws s3 ls s3://kisaanmitra-web-demo-1772974554/kg_data_live.json --region ap-south-1
```

## Features

### Auto-Refresh
- Lambda updates data every 5 minutes
- Dashboard auto-refreshes every 5 minutes
- Manual refresh button available

### Real-Time Stats
- Total farmers
- Districts and villages
- Crop distribution
- Land allocation
- Last update timestamp

### Interactive Features
- Drag nodes to reposition
- Zoom in/out with scroll
- Click nodes to highlight connections
- Search by name
- Filter by type (district/village/crop)
- Export as PNG

## Cost Optimization

- **Lambda**: ~8,640 invocations/month = $0.18/month
- **S3**: Minimal storage + requests = $0.05/month
- **EventBridge**: Free tier covers usage
- **Total**: ~$0.25/month

## Troubleshooting

### Data not updating?
1. Check Lambda logs for errors
2. Verify EventBridge rule is enabled
3. Check S3 file timestamp
4. Verify DynamoDB table has data

### Dashboard not loading?
1. Check browser console for errors
2. Verify S3 bucket is public
3. Check CORS configuration
4. Clear browser cache

### Lambda timeout?
- Increase timeout in `deploy_kg_updater.sh`
- Current: 60 seconds (sufficient for 10K+ farmers)

## Future Enhancements

- [ ] Add disease outbreak tracking
- [ ] Show market price trends
- [ ] Display weather patterns
- [ ] Add farmer success stories
- [ ] Implement real-time WebSocket updates
- [ ] Add historical data comparison
