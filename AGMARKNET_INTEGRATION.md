# AgMarkNet API Integration - Data Source Transparency

## What's Deployed ✅

### 1. Hybrid Data System

**Market Prices** (when you ask "what's the price?"):
- **Primary**: AgMarkNet API (real-time) - if API key available
- **Fallback**: Static data (instant) - if API unavailable or fails
- **Indicator**: 📡 for real-time, 📌 for static

**Crop Budgets** (when you ask "what will it cost?"):
- **Costs**: AI-generated (Claude Sonnet 4) - no API exists for this
- **Market Price**: AgMarkNet API (if available) or AI estimate
- **Feasibility**: AI analysis
- **Indicators**: 📡 for AgMarkNet price, 🤖 for AI estimate

### 2. Data Source Labels

Every response now clearly shows where data comes from:

**Budget Response:**
```
💰 Mushroom Cultivation Analysis
📍 Location: Kolhapur
🌾 Land: 1 acre

🎯 Feasibility: Suitable
💬 Good climate match
🌡️ Climate Match: Good
📅 Best Season: Winter to Spring

📊 Cost Breakdown
• Seeds: ₹15,000
• Fertilizer: ₹25,000
...
💵 Total Cost: ₹105,000

📈 Expected Returns
• Yield: 80 quintal
• Market Price: ₹4,000/quintal 📡  ← Real-time from AgMarkNet
• Revenue: ₹320,000
✨ Net Profit: ₹215,000
💡 ROI: 204%

📌 Data Sources:
• Costs: AI Estimates
• Price: AgMarkNet  ← Shows if real data used
• Analysis: AI (Claude Sonnet 4)

💬 Verify with local suppliers
```

**Market Price Response:**
```
📊 Wheat Market Prices

💰 Average Price: ₹2,450/quintal
📊 Range: ₹2,200 - ₹2,600
➡️ Trend: Stable

🏪 Top Mandis:
1. Mumbai APMC: ₹2,500
2. Pune APMC: ₹2,450

📅 Updated: 2026-02-26
📡 Source: AgMarkNet (Real-time)  ← Shows data source

💡 Tip: Check multiple mandis before selling
```

### 3. How It Works

**When AgMarkNet API Key is Available:**
1. Market prices: Fetches from AgMarkNet (2-5 seconds)
2. Budget market price: Uses AgMarkNet data in AI prompt
3. Shows 📡 indicator for real-time data

**When AgMarkNet API Key is NOT Available:**
1. Market prices: Uses static data (instant)
2. Budget market price: AI estimates
3. Shows 📌 or 🤖 indicator for estimates

### 4. Confirmation in Logs

**Look for these log messages:**

**AgMarkNet Enabled:**
```
[DEBUG] AgMarkNet API key available, fetching real-time data...
[DEBUG] Calling AgMarkNet API for wheat in Maharashtra...
[DEBUG] AgMarkNet returned 10 records
[INFO] ✅ AgMarkNet data processed: Avg ₹2,450, Trend: stable
[INFO] ✅ Using AgMarkNet real-time data for wheat
[DEBUG] Using real market price from AgMarkNet: True
[DEBUG] Market price source: agmarknet
```

**AgMarkNet Disabled (Current):**
```
[DEBUG] AgMarkNet API key not available
[INFO] ✅ Using static market data for wheat
[DEBUG] Market price source: ai_estimate
```

## Current Status

**AgMarkNet API**: ❌ Not configured (key = "not_available")
**Fallback**: ✅ Static data working
**Data Source Labels**: ✅ Added to all responses
**Transparency**: ✅ Users know what's AI vs real data

## To Enable AgMarkNet Real-Time Data

### Step 1: Get API Key
Follow guide: `docs/GET_AGMARKNET_API_KEY.md`

### Step 2: Update Lambda Environment Variable
```bash
aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --environment "Variables={
    WHATSAPP_TOKEN=your_token,
    PHONE_NUMBER_ID=your_id,
    VERIFY_TOKEN=mySecret_123,
    AGMARKNET_API_KEY=your_actual_api_key,
    CROP_HEALTH_API_KEY=your_key,
    S3_BUCKET=kisaanmitra-images,
    CONVERSATION_TABLE=kisaanmitra-conversations
  }" \
  --region ap-south-1
```

### Step 3: Test
Send "wheat price" and check logs for:
```
[INFO] ✅ Using AgMarkNet real-time data for wheat
```

## What Data Comes From Where

| Data Type | Source | Can Be Real-Time? |
|-----------|--------|-------------------|
| Market Prices | AgMarkNet API ✅ or Static | YES (if API key) |
| Seeds Cost | AI (Claude) | NO (no API exists) |
| Fertilizer Cost | AI (Claude) | NO (no API exists) |
| Labor Cost | AI (Claude) | NO (no API exists) |
| Irrigation Cost | AI (Claude) | NO (no API exists) |
| Yield Estimate | AI (Claude) | NO (no API exists) |
| Feasibility | AI (Claude) | NO (no API exists) |
| Disease Detection | Kindwise API ✅ | YES (always real-time) |

## Important Notes

1. **Budget costs are ALWAYS AI-generated** - There's no public API in India that provides real-time cultivation costs

2. **Market prices CAN be real-time** - If you provide AgMarkNet API key

3. **Data source is always labeled** - Users know what's real vs estimated

4. **Fallback always works** - If AgMarkNet fails, static data is used

5. **Slower but accurate** - AgMarkNet adds 2-5 seconds but gives real prices

## Recommendation

**For Production:**
- Get AgMarkNet API key for real market prices
- Keep AI for budget costs (no alternative)
- Data source labels ensure transparency
- Users can verify with local sources

**Current State:**
- System works with or without AgMarkNet
- Clear labels show data sources
- Fallback ensures no failures
- Ready for API key when you get it

## Testing

**Without API Key (Current):**
- "wheat price" → Static data, shows "📌 Source: Static Data"
- "tomato budget" → AI costs, shows "🤖 AI Estimate"

**With API Key (Future):**
- "wheat price" → AgMarkNet, shows "📡 Source: AgMarkNet (Real-time)"
- "tomato budget" → AI costs + AgMarkNet price, shows "📡" for price

Check CloudWatch logs to confirm data source for each request!
