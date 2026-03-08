# Web Demo & Knowledge Graph - Complete Setup ✅

## What Was Done

### 1. Enhanced Evaluator Banner
- Made banner **permanently visible** (removed close button)
- Enhanced styling:
  - Darker red gradient (#dc2626 → #991b1b)
  - Larger text (20px, font-weight 800, uppercase)
  - Bigger icon (40px)
  - Stronger shadows and borders
  - More prominent appearance

### 2. Added Knowledge Graph Dashboard Link
- Added purple "Knowledge Graph" button in footer
- Links to: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com/knowledge-graph.html
- Positioned next to GitHub link

### 3. Dynamic Knowledge Graph Updates
Created complete system for real-time KG dashboard updates:

#### Lambda Function: `kisaanmitra-kg-updater`
- Fetches all farmers from DynamoDB
- Generates knowledge graph structure (nodes, links, metadata)
- Uploads JSON to S3 every 5 minutes
- Triggered automatically by EventBridge

#### Python Script: `fetch_kg_data.py`
- Manual data update script
- Can be run locally or in CI/CD
- Generates same format as Lambda

#### Deployment Script: `deploy_kg_updater.sh`
- One-command deployment
- Sets up Lambda + EventBridge rule
- Configures permissions automatically

### 4. Repository Cleanup
- Archived 97 unnecessary MD files to `docs/archive/`
- Kept only 11 essential docs in root
- Clean, organized structure

## Live URLs

### Web Chat Demo
**URL**: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com

**Features**:
- Phone number collection modal
- AI for Bharat Hackathon banner (permanent)
- Team members in footer
- GitHub link
- Knowledge Graph link

### Knowledge Graph Dashboard
**URL**: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com/knowledge-graph.html

**Features**:
- Interactive D3.js network visualization
- Real-time data from DynamoDB
- Auto-refresh every 5 minutes
- Search and filter capabilities
- Export as PNG
- Live statistics

### Live Data JSON
**URL**: https://kisaanmitra-web-demo-1772974554.s3.ap-south-1.amazonaws.com/kg_data_live.json

**Updates**: Every 5 minutes via Lambda

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DynamoDB Tables                          │
│  • kisaanmitra-farmer-profiles                             │
│  • kisaanmitra-conversations                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│         Lambda: kisaanmitra-kg-updater                      │
│  • Triggered every 5 minutes (EventBridge)                 │
│  • Fetches all farmers                                     │
│  • Generates KG structure                                  │
│  • Uploads to S3                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│              S3: kg_data_live.json                          │
│  • Updated every 5 minutes                                 │
│  • Cache: 60 seconds                                       │
│  • Public read access                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│         Static HTML: knowledge-graph.html                   │
│  • Fetches JSON on page load                               │
│  • Auto-refreshes every 5 minutes                          │
│  • Interactive D3.js visualization                         │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Commands

### Deploy KG Updater Lambda
```bash
cd src/lambda
./deploy_kg_updater.sh
```

### Manual Data Update
```bash
python3 demo/fetch_kg_data.py
```

### Test Lambda
```bash
aws lambda invoke \
  --function-name kisaanmitra-kg-updater \
  --region ap-south-1 \
  response.json
```

### View Logs
```bash
aws logs tail /aws/lambda/kisaanmitra-kg-updater --follow --region ap-south-1
```

## Data Flow

1. **Farmers register** via WhatsApp → Stored in DynamoDB
2. **Lambda runs** every 5 minutes → Fetches all farmers
3. **KG data generated** → Nodes (districts, villages, crops) + Links
4. **JSON uploaded** to S3 → `kg_data_live.json`
5. **Dashboard loads** → Fetches latest JSON
6. **Auto-refresh** → Dashboard reloads every 5 minutes

## Cost Analysis

| Service | Usage | Cost/Month |
|---------|-------|------------|
| Lambda | 8,640 invocations | $0.18 |
| S3 Storage | <1 MB | $0.02 |
| S3 Requests | ~10K GET | $0.03 |
| EventBridge | Free tier | $0.00 |
| **Total** | | **$0.23** |

## Team

- **Aditya Rane** - Project Manager
- **Parth Nikam** - Advanced Analytics, Data Science
- **Vinay Patil** - Lead Engineer, Backend AI Systems

## GitHub

https://github.com/parth-nikam/KisaanMitra.AI

## Hackathon

**AI for Bharat** - Building India's first village-level agricultural data infrastructure

---

**Status**: ✅ All systems deployed and operational
**Last Updated**: March 8, 2026
