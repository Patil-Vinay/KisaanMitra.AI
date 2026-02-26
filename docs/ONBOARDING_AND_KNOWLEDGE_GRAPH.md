# KisaanMitra Onboarding & Knowledge Graph

## Overview

This document describes the farmer onboarding system and village-level knowledge graph implementation.

## Features

### 1. Automated Farmer Onboarding
- **New User Detection**: Automatically detects first-time WhatsApp users
- **Conversational Flow**: Natural Hindi conversation to collect information
- **AI-Powered Extraction**: Uses Amazon Bedrock to extract information from free-form text
- **Progressive Disclosure**: Asks one question at a time for better UX

### 2. Village Knowledge Graph
- **Graph Database**: Amazon Neptune stores relationships between farmers, villages, and crops
- **Scalable Design**: Single unified graph with village nodes
- **Rich Relationships**: Captures LIVES_IN, GROWS, HAS_FARMER relationships
- **Fallback Storage**: Local in-memory graph when Neptune unavailable

### 3. Streamlit Dashboard
- **Real-time Visualization**: Interactive network graph of farmer relationships
- **Village Analytics**: Statistics per village (farmer count, land, crops)
- **Crop Distribution**: Pie charts and bar graphs
- **Export Capability**: Download farmer data as CSV

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ONBOARDING FLOW                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. New User Detected                                           │
│     ↓                                                            │
│  2. Welcome Message (Hindi)                                     │
│     "आपका नाम क्या है?"                                         │
│     ↓                                                            │
│  3. Extract Name with AI                                        │
│     Bedrock Nova Pro extracts from free text                    │
│     ↓                                                            │
│  4. Ask for Crops                                               │
│     "आप कौन सी फसलें उगाते हैं?"                                │
│     ↓                                                            │
│  5. Extract Crops with AI                                       │
│     Handles Hindi/English, multiple crops                       │
│     ↓                                                            │
│  6. Ask for Land Size                                           │
│     "आपके पास कितनी जमीन है?"                                   │
│     ↓                                                            │
│  7. Extract Land with AI                                        │
│     Converts hectares to acres                                  │
│     ↓                                                            │
│  8. Ask for Village                                             │
│     "आप किस गांव से हैं?"                                       │
│     ↓                                                            │
│  9. Extract Village with AI                                     │
│     Handles Hindi/Marathi names                                 │
│     ↓                                                            │
│  10. Save Profile & Add to Knowledge Graph                      │
│      ✅ Registration Complete!                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE GRAPH STRUCTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  (Farmer) ──[LIVES_IN]──> (Village)                            │
│     │                                                            │
│     └──[GROWS]──> (Crop)                                        │
│                                                                  │
│  Node Types:                                                    │
│    • Farmer: user_id, name, phone, land_acres, registered_at   │
│    • Village: name                                              │
│    • Crop: name                                                 │
│                                                                  │
│  Edge Types:                                                    │
│    • LIVES_IN: Farmer → Village                                │
│    • GROWS: Farmer → Crop (with land_acres property)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Storage

### DynamoDB Tables

#### 1. kisaanmitra-onboarding
Tracks onboarding state for users in progress.

```
{
  "user_id": "919876543210",
  "state": "asked_crops",
  "data": {
    "name": "Rajesh Patil"
  },
  "updated_at": "2026-02-26T10:30:00Z"
}
```

**States:**
- `new`: Initial state
- `asked_name`: Waiting for name
- `asked_crops`: Waiting for crops
- `asked_land`: Waiting for land size
- `asked_village`: Waiting for village
- `completed`: Onboarding finished

#### 2. kisaanmitra-user-profiles
Stores complete farmer profiles.

```
{
  "user_id": "919876543210",
  "name": "Rajesh Patil",
  "crops": "wheat, rice",
  "land_acres": "5",
  "village": "Pune",
  "phone": "919876543210",
  "registered_at": "2026-02-26T10:35:00Z",
  "profile_complete": true
}
```

**Indexes:**
- Primary: `user_id` (HASH)
- GSI: `village-index` (for village-based queries)

### Amazon Neptune

Graph database storing relationships between farmers, villages, and crops.

**Vertices:**
- `farmer`: Farmer nodes with properties
- `village`: Village nodes
- `crop`: Crop nodes

**Edges:**
- `LIVES_IN`: Farmer → Village
- `GROWS`: Farmer → Crop

## Onboarding Flow Example

### User Experience (Hindi)

```
User: Hi

Bot: 🙏 नमस्ते! KisaanMitra में आपका स्वागत है!

मैं आपका कृषि सहायक हूं। मैं आपकी मदद कर सकता हूं:
🌾 फसल रोग पहचान
📊 बाजार भाव
💰 बजट योजना

पहले मुझे आपके बारे में कुछ जानकारी चाहिए।

*आपका नाम क्या है?*

---

User: मेरा नाम राजेश पाटील है

Bot: धन्यवाद राजेश पाटील जी! 🙏

*आप कौन सी फसलें उगाते हैं?*
(उदाहरण: गेहूं, धान, कपास)

---

User: मैं गेहूं और धान उगाता हूं

Bot: बढ़िया! आप wheat, rice उगाते हैं। 🌾

*आपके पास कितनी जमीन है? (एकड़ में)*
(उदाहरण: 5 एकड़)

---

User: 5 एकड़

Bot: अच्छा! 5 एकड़ जमीन। 📏

*आप किस गांव/शहर से हैं?*
(उदाहरण: पुणे, नाशिक)

---

User: पुणे

Bot: ✅ *रजिस्ट्रेशन पूरा हुआ!*

📋 *आपकी जानकारी:*
👤 नाम: राजेश पाटील
🌾 फसलें: wheat, rice
📏 जमीन: 5 एकड़
📍 गांव: पुणे

अब आप मुझसे कुछ भी पूछ सकते हैं:
• फसल की बीमारी के लिए फोटो भेजें
• बाजार भाव पूछें
• बजट योजना के लिए पूछें

कैसे मदद करूं? 😊
```

## AI-Powered Information Extraction

The system uses Amazon Bedrock (Nova Pro) to extract information from free-form text.

### Example Extractions

**Name Extraction:**
```
Input: "मेरा नाम राजेश पाटील है"
Output: "Rajesh Patil"

Input: "I am Suresh Kumar"
Output: "Suresh Kumar"
```

**Crop Extraction:**
```
Input: "मैं गेहूं और धान उगाता हूं"
Output: "wheat, rice"

Input: "I grow tomato and onion"
Output: "tomato, onion"
```

**Land Size Extraction:**
```
Input: "मेरे पास 5 एकड़ जमीन है"
Output: "5"

Input: "I have 2 hectares"
Output: "4.94"  (converted to acres)
```

**Village Extraction:**
```
Input: "मैं पुणे के पास रहता हूं"
Output: "Pune"

Input: "I am from Nashik district"
Output: "Nashik"
```

## Knowledge Graph Queries

### Get All Farmers in a Village

```python
from knowledge_graph.village_graph import knowledge_graph

farmers = knowledge_graph.get_village_farmers("Pune")
# Returns list of farmer profiles
```

### Get All Farmers Growing a Crop

```python
farmers = knowledge_graph.get_crop_farmers("wheat")
# Returns list of farmers growing wheat
```

### Get Village Statistics

```python
stats = knowledge_graph.get_village_statistics("Pune")
# Returns:
# {
#   "village": "Pune",
#   "farmer_count": 10,
#   "total_land_acres": 50.5,
#   "crops_grown": {"wheat": 7, "rice": 5, "cotton": 3},
#   "farmers": [...]
# }
```

### Get Graph Summary

```python
summary = knowledge_graph.get_graph_summary()
# Returns:
# {
#   "total_farmers": 25,
#   "total_villages": 5,
#   "total_crops": 8,
#   "villages": ["Pune", "Nashik", ...],
#   "crops": ["wheat", "rice", ...]
# }
```

## Streamlit Dashboard

### Features

1. **Overview Metrics**
   - Total farmers
   - Total villages
   - Total crops
   - Total land area

2. **Interactive Network Graph**
   - Farmers (green circles)
   - Villages (blue squares)
   - Crops (orange diamonds)
   - Relationships shown as edges

3. **Village Breakdown**
   - Expandable cards per village
   - Farmer count, land area, crops

4. **Detailed Tables**
   - Farmer profiles with all details
   - CSV export functionality

5. **Analytics**
   - Crop distribution pie chart
   - Land distribution bar chart
   - Registration timeline

### Running the Dashboard

```bash
cd dashboard
./run_dashboard.sh
```

The dashboard will open at `http://localhost:8501`

### Dashboard Screenshots

**Main View:**
- Network graph showing all relationships
- Overview metrics at top
- Village cards on right

**Farmers Tab:**
- Searchable table of all farmers
- Download CSV button

**Crops Analysis Tab:**
- Pie chart: Farmers by crop
- Bar chart: Land by crop

**Statistics Tab:**
- Village-wise breakdown table
- Registration timeline graph

## Deployment

### Step 1: Create DynamoDB Tables

```bash
cd infrastructure
./setup_onboarding_tables.sh
```

Creates:
- `kisaanmitra-onboarding`
- `kisaanmitra-user-profiles`

### Step 2: Setup Neptune (Optional)

```bash
./setup_neptune.sh
```

Creates Neptune cluster for production use. For development, the system uses local in-memory storage.

**Cost:** ~$73/month for db.t3.medium instance

### Step 3: Deploy Lambda

```bash
cd ../src/lambda
./deploy_with_onboarding.sh
```

Packages and deploys Lambda with onboarding modules.

### Step 4: Update Lambda IAM Role

Add permissions for new tables:

```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem",
    "dynamodb:Query",
    "dynamodb:Scan"
  ],
  "Resource": [
    "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-onboarding",
    "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-user-profiles",
    "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-user-profiles/index/*"
  ]
}
```

For Neptune access (if using):

```json
{
  "Effect": "Allow",
  "Action": [
    "neptune-db:*"
  ],
  "Resource": "arn:aws:neptune-db:ap-south-1:*:*/*"
}
```

### Step 5: Test Onboarding

Send "Hi" to your WhatsApp Business number and follow the onboarding flow.

### Step 6: View Dashboard

```bash
cd dashboard
./run_dashboard.sh
```

## Monitoring

### CloudWatch Logs

Monitor onboarding process:

```bash
aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow
```

Look for:
- "Profile saved for user {user_id}"
- "Added farmer {name} to knowledge graph"

### DynamoDB Console

Check tables:
- `kisaanmitra-onboarding`: Active onboarding sessions
- `kisaanmitra-user-profiles`: Completed profiles

### Neptune Console

View graph metrics:
- Vertex count (farmers + villages + crops)
- Edge count (relationships)
- Query performance

## Cost Breakdown

### Development (Local Graph)
- **DynamoDB**: $0.25/month (on-demand, low usage)
- **Lambda**: $0.20/month (included in existing cost)
- **Bedrock**: $0.50/month (extraction queries)
- **Total**: ~$1/month

### Production (with Neptune)
- **DynamoDB**: $1/month
- **Lambda**: $0.50/month
- **Bedrock**: $2/month
- **Neptune**: $73/month (db.t3.medium)
- **Total**: ~$76.50/month

### Cost Optimization

1. **Use Local Graph for Development**: No Neptune cost
2. **Neptune Serverless**: Pay per query (coming soon)
3. **Reserved Instances**: 30-40% discount for Neptune
4. **Smaller Instance**: db.t3.small for $36/month

## Troubleshooting

### Issue: Onboarding not triggering

**Solution:**
1. Check Lambda logs for errors
2. Verify `ONBOARDING_AVAILABLE = True` in logs
3. Check DynamoDB table exists

### Issue: AI extraction failing

**Solution:**
1. Verify Bedrock access in IAM role
2. Check region (us-east-1 for cross-region inference)
3. Review extraction prompts in `farmer_onboarding.py`

### Issue: Neptune connection timeout

**Solution:**
1. Ensure Lambda is in same VPC as Neptune
2. Check security group allows port 8182
3. Verify Neptune endpoint in environment variable
4. Use local graph as fallback

### Issue: Dashboard not loading data

**Solution:**
1. Check AWS credentials configured
2. Verify DynamoDB table names
3. Check region (ap-south-1)
4. Review Streamlit logs for errors

## Future Enhancements

1. **Multi-language Support**: Marathi, Gujarati, Tamil
2. **Voice Onboarding**: WhatsApp voice message support
3. **Photo Verification**: Upload farm photo during onboarding
4. **Family Members**: Add multiple farmers per household
5. **Crop Calendar**: Track planting and harvest dates
6. **Yield Tracking**: Record actual yields per season
7. **Market Linkage**: Connect farmers with buyers
8. **Group Formation**: Create farmer producer organizations (FPOs)
9. **Advanced Analytics**: Predictive models for yield, prices
10. **Mobile App**: Native app for field agents

## API Reference

### FarmerOnboarding Class

```python
from onboarding.farmer_onboarding import onboarding_manager

# Check if user is new
is_new = onboarding_manager.is_new_user(user_id)

# Get onboarding state
state, data = onboarding_manager.get_onboarding_state(user_id)

# Process message
response, is_completed = onboarding_manager.process_onboarding_message(
    user_id, user_message
)

# Get user profile
profile = onboarding_manager.get_user_profile(user_id)
```

### VillageKnowledgeGraph Class

```python
from knowledge_graph.village_graph import knowledge_graph

# Add farmer to graph
success = knowledge_graph.add_farmer_to_graph(user_profile)

# Query farmers
farmers = knowledge_graph.get_village_farmers("Pune")
farmers = knowledge_graph.get_crop_farmers("wheat")

# Get statistics
stats = knowledge_graph.get_village_statistics("Pune")
summary = knowledge_graph.get_graph_summary()

# Export for visualization
graph_data = knowledge_graph.export_graph_data()
```

## Support

For issues or questions:
- Check logs: `aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow`
- Review documentation: `docs/`
- Contact: team@kisaanmitra.ai

---

**Status**: Production Ready ✅
**Last Updated**: 2026-02-26
**Version**: 2.0.0
