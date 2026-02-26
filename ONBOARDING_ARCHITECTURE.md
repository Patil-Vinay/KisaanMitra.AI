# KisaanMitra Onboarding & Knowledge Graph Architecture

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     KISAANMITRA ONBOARDING SYSTEM                            │
│                    With Village Knowledge Graph                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. USER INTERACTION (WhatsApp)                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   New Farmer: "Hi"                                                           │
│        ↓                                                                      │
│   WhatsApp Business API                                                      │
│        ↓                                                                      │
│   API Gateway                                                                │
│        ↓                                                                      │
│   Lambda: lambda_whatsapp_kisaanmitra                                        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. NEW USER DETECTION                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   onboarding_manager.is_new_user(user_id)                                   │
│        ↓                                                                      │
│   Query: kisaanmitra-user-profiles                                           │
│        ↓                                                                      │
│   Profile exists? → No → START ONBOARDING                                   │
│                  → Yes → Normal agent routing                                │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. ONBOARDING STATE MACHINE                                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   STATE: new                                                                 │
│   ├─ Send: "आपका नाम क्या है?"                                              │
│   └─ Next: asked_name                                                        │
│        ↓                                                                      │
│   STATE: asked_name                                                          │
│   ├─ Extract name with AI (Bedrock Nova Pro)                                │
│   ├─ Save: data["name"] = "Rajesh Patil"                                    │
│   ├─ Send: "आप कौन सी फसलें उगाते हैं?"                                     │
│   └─ Next: asked_crops                                                       │
│        ↓                                                                      │
│   STATE: asked_crops                                                         │
│   ├─ Extract crops with AI                                                   │
│   ├─ Save: data["crops"] = "wheat, rice"                                    │
│   ├─ Send: "आपके पास कितनी जमीन है?"                                        │
│   └─ Next: asked_land                                                        │
│        ↓                                                                      │
│   STATE: asked_land                                                          │
│   ├─ Extract land size with AI                                              │
│   ├─ Save: data["land_acres"] = "5"                                         │
│   ├─ Send: "आप किस गांव से हैं?"                                            │
│   └─ Next: asked_village                                                     │
│        ↓                                                                      │
│   STATE: asked_village                                                       │
│   ├─ Extract village with AI                                                │
│   ├─ Save: data["village"] = "Pune"                                         │
│   ├─ Send: "✅ रजिस्ट्रेशन पूरा हुआ!"                                        │
│   └─ Next: completed                                                         │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. AI-POWERED INFORMATION EXTRACTION                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   Amazon Bedrock (Nova Pro)                                                 │
│   ├─ Model: us.amazon.nova-pro-v1:0                                         │
│   ├─ Temperature: 0.2 (precise extraction)                                  │
│   └─ Max Tokens: 100                                                         │
│                                                                               │
│   Extraction Prompts:                                                        │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ NAME EXTRACTION                                             │            │
│   │ Input: "मेरा नाम राजेश पाटील है"                           │            │
│   │ Output: "Rajesh Patil"                                      │            │
│   │                                                              │            │
│   │ Handles: Hindi/English names, full names                   │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ CROP EXTRACTION                                             │            │
│   │ Input: "मैं गेहूं और धान उगाता हूं"                        │            │
│   │ Output: "wheat, rice"                                       │            │
│   │                                                              │            │
│   │ Handles: Multiple crops, Hindi/English, standardization    │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ LAND SIZE EXTRACTION                                        │            │
│   │ Input: "मेरे पास 5 एकड़ जमीन है"                           │            │
│   │ Output: "5"                                                 │            │
│   │                                                              │            │
│   │ Handles: Acres, hectares (converts), Hindi numbers         │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ VILLAGE EXTRACTION                                          │            │
│   │ Input: "मैं पुणे के पास रहता हूं"                          │            │
│   │ Output: "Pune"                                              │            │
│   │                                                              │            │
│   │ Handles: Hindi/Marathi names, districts, towns             │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ 5. DATA PERSISTENCE                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   DynamoDB: kisaanmitra-onboarding                                           │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ user_id: "919876543210"                                     │            │
│   │ state: "asked_crops"                                        │            │
│   │ data: {                                                     │            │
│   │   "name": "Rajesh Patil"                                    │            │
│   │ }                                                            │            │
│   │ updated_at: "2026-02-26T10:30:00Z"                          │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   DynamoDB: kisaanmitra-user-profiles                                        │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ user_id: "919876543210"                                     │            │
│   │ name: "Rajesh Patil"                                        │            │
│   │ crops: "wheat, rice"                                        │            │
│   │ land_acres: "5"                                             │            │
│   │ village: "Pune"                                             │            │
│   │ phone: "919876543210"                                       │            │
│   │ registered_at: "2026-02-26T10:35:00Z"                       │            │
│   │ profile_complete: true                                      │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ 6. KNOWLEDGE GRAPH POPULATION                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   knowledge_graph.add_farmer_to_graph(profile)                              │
│        ↓                                                                      │
│   Create/Update Nodes:                                                       │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ FARMER NODE                                                 │            │
│   │ ├─ id: "919876543210"                                       │            │
│   │ ├─ label: "Rajesh Patil"                                    │            │
│   │ ├─ type: "farmer"                                           │            │
│   │ ├─ properties:                                              │            │
│   │ │  ├─ name: "Rajesh Patil"                                 │            │
│   │ │  ├─ phone: "919876543210"                                │            │
│   │ │  ├─ land_acres: "5"                                      │            │
│   │ │  └─ registered_at: "2026-02-26T10:35:00Z"               │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ VILLAGE NODE                                                │            │
│   │ ├─ id: "village_Pune"                                       │            │
│   │ ├─ label: "Pune"                                            │            │
│   │ ├─ type: "village"                                          │            │
│   │ └─ properties:                                              │            │
│   │    └─ name: "Pune"                                          │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ CROP NODES                                                  │            │
│   │ ├─ Wheat:                                                   │            │
│   │ │  ├─ id: "crop_wheat"                                      │            │
│   │ │  ├─ label: "wheat"                                        │            │
│   │ │  └─ type: "crop"                                          │            │
│   │ └─ Rice:                                                    │            │
│   │    ├─ id: "crop_rice"                                       │            │
│   │    ├─ label: "rice"                                         │            │
│   │    └─ type: "crop"                                          │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   Create Relationships:                                                      │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ (Farmer: Rajesh) ──[LIVES_IN]──> (Village: Pune)           │            │
│   │ (Farmer: Rajesh) ──[GROWS]──> (Crop: Wheat)                │            │
│   │ (Farmer: Rajesh) ──[GROWS]──> (Crop: Rice)                 │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   Storage Options:                                                           │
│   ├─ Production: Amazon Neptune (Gremlin)                                   │
│   └─ Development: Local in-memory graph                                     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│ 7. STREAMLIT DASHBOARD VISUALIZATION                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   URL: http://localhost:8501                                                │
│                                                                               │
│   ┌──────────────────────────────────────────────────────────┐              │
│   │ 📊 OVERVIEW METRICS                                       │              │
│   │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                     │              │
│   │ │ 👨‍🌾 25 │ │ 🏘️ 5  │ │ 🌾 8  │ │ 📏 125│                     │              │
│   │ │Farmers│ │Village│ │ Crops│ │Acres │                     │              │
│   │ └──────┘ └──────┘ └──────┘ └──────┘                     │              │
│   └──────────────────────────────────────────────────────────┘              │
│                                                                               │
│   ┌──────────────────────────────────────────────────────────┐              │
│   │ 🕸️ KNOWLEDGE GRAPH NETWORK                                │              │
│   │                                                            │              │
│   │         ●Farmer1                                          │              │
│   │        /    \                                             │              │
│   │       /      \                                            │              │
│   │   ■Village  ◆Wheat                                       │              │
│   │       \      /                                            │              │
│   │        \    /                                             │              │
│   │         ●Farmer2                                          │              │
│   │                                                            │              │
│   │ Legend:                                                   │              │
│   │ ● Farmer (green)  ■ Village (blue)  ◆ Crop (orange)     │              │
│   └──────────────────────────────────────────────────────────┘              │
│                                                                               │
│   ┌──────────────────────────────────────────────────────────┐              │
│   │ 👨‍🌾 FARMERS TABLE                                          │              │
│   │ ┌────────┬────────┬──────────┬──────┬──────────┐        │              │
│   │ │ Name   │Village │ Crops    │ Land │ Phone    │        │              │
│   │ ├────────┼────────┼──────────┼──────┼──────────┤        │              │
│   │ │ Rajesh │ Pune   │wheat,rice│ 5    │ 9198765..│        │              │
│   │ │ Suresh │ Nashik │ cotton   │ 3    │ 9187654..│        │              │
│   │ └────────┴────────┴──────────┴──────┴──────────┘        │              │
│   │ [📥 Download CSV]                                        │              │
│   └──────────────────────────────────────────────────────────┘              │
│                                                                               │
│   ┌──────────────────────────────────────────────────────────┐              │
│   │ 🌾 CROP DISTRIBUTION                                      │              │
│   │ ┌─────────────┐  ┌─────────────┐                        │              │
│   │ │ Pie Chart   │  │ Bar Chart   │                        │              │
│   │ │ Farmers by  │  │ Land by     │                        │              │
│   │ │ Crop        │  │ Crop        │                        │              │
│   │ └─────────────┘  └─────────────┘                        │              │
│   └──────────────────────────────────────────────────────────┘              │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 8. QUERY CAPABILITIES                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   Query 1: Get Village Farmers                                              │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ knowledge_graph.get_village_farmers("Pune")                 │            │
│   │ Returns: [Rajesh, Amit, Priya, ...]                        │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   Query 2: Get Crop Farmers                                                 │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ knowledge_graph.get_crop_farmers("wheat")                   │            │
│   │ Returns: [Rajesh, Suresh, Amit, ...]                       │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   Query 3: Village Statistics                                               │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ knowledge_graph.get_village_statistics("Pune")              │            │
│   │ Returns: {                                                  │            │
│   │   "farmer_count": 10,                                       │            │
│   │   "total_land_acres": 50.5,                                │            │
│   │   "crops_grown": {"wheat": 7, "rice": 5}                   │            │
│   │ }                                                            │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
│   Query 4: Graph Summary                                                    │
│   ┌────────────────────────────────────────────────────────────┐            │
│   │ knowledge_graph.get_graph_summary()                         │            │
│   │ Returns: {                                                  │            │
│   │   "total_farmers": 25,                                      │            │
│   │   "total_villages": 5,                                      │            │
│   │   "total_crops": 8                                          │            │
│   │ }                                                            │            │
│   └────────────────────────────────────────────────────────────┘            │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Timeline

```
T+0s:  Farmer sends "Hi" to WhatsApp
T+1s:  Lambda detects new user
T+2s:  Sends welcome message + asks for name
       
T+10s: Farmer replies "मेरा नाम राजेश है"
T+11s: AI extracts name: "Rajesh"
T+12s: Saves to onboarding table
T+13s: Asks for crops

T+20s: Farmer replies "गेहूं और धान"
T+21s: AI extracts crops: "wheat, rice"
T+22s: Saves to onboarding table
T+23s: Asks for land size

T+30s: Farmer replies "5 एकड़"
T+31s: AI extracts land: "5"
T+32s: Saves to onboarding table
T+33s: Asks for village

T+40s: Farmer replies "पुणे"
T+41s: AI extracts village: "Pune"
T+42s: Saves complete profile to user-profiles table
T+43s: Adds farmer to knowledge graph
T+44s: Creates farmer node
T+45s: Creates/links village node
T+46s: Creates/links crop nodes
T+47s: Sends completion message

Total Time: ~47 seconds
```

## Cost Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│ MONTHLY COST (1000 farmers, 10 onboardings/day)             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ DynamoDB (2 tables)                                          │
│ ├─ kisaanmitra-onboarding: $0.10                            │
│ └─ kisaanmitra-user-profiles: $0.15                         │
│ Subtotal: $0.25                                             │
│                                                              │
│ Lambda (onboarding processing)                              │
│ ├─ Invocations: 300/month                                   │
│ ├─ Duration: 5s avg                                         │
│ └─ Cost: $0.20                                              │
│                                                              │
│ Bedrock (AI extraction)                                     │
│ ├─ Model: Nova Pro                                          │
│ ├─ Requests: 1,200/month (4 per onboarding)                │
│ └─ Cost: $0.50                                              │
│                                                              │
│ Neptune (optional - production)                             │
│ ├─ Instance: db.t3.medium                                   │
│ └─ Cost: $73.00                                             │
│                                                              │
│ TOTAL (Development): $0.95/month                            │
│ TOTAL (Production): $73.95/month                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Architecture Status**: Production Ready ✅  
**Last Updated**: 2026-02-26  
**Version**: 2.0.0
