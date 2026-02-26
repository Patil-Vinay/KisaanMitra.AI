# 🚀 Deploy AI State Extraction + Web Scraping

## Quick Deploy

```bash
cd src/lambda && ./deploy_whatsapp.sh
```

---

## What This Deploys

### 1. AI State Extraction
- Removes 80+ hardcoded city mappings
- AI intelligently extracts state from ANY location
- Works for all Indian cities and states
- Smart default to Maharashtra

### 2. Re-Enabled Web Scraping
- Uses AI-extracted state for accurate scraping
- Enhanced HTML parsing (5 different patterns)
- Better browser mimicking
- Longer timeout (8 seconds)
- Enhanced debugging

### 3. Priority Order
1. Web scraping (1-3s, real-time) 🌐
2. AgMarkNet API (2-5s, real-time) 📡
3. Static data (instant, reliable) 📌

---

## Test After Deployment

### Test 1: Punjab Location

**Send WhatsApp**:
```
What is wheat price in Amritsar?
```

**Expected logs**:
```
[DEBUG] Using AI to extract state for market query...
[INFO] ✅ AI extracted state: Punjab
[DEBUG] 🌐 Scraping AgMarkNet for wheat in Punjab...
[DEBUG] HTML received: [large number] chars
[INFO] ✅ Extracted [number] valid prices
[INFO] ✅ Scraping successful: Avg ₹X, Trend: Y
```

**Expected response**:
```
📊 Wheat Market Prices

💰 Average Price: ₹X/quintal
📊 Range: ₹Y - ₹Z
📈 Trend: [trend]

🏪 Top Mandis:
1. [Punjab mandi]: ₹X
2. [Punjab mandi]: ₹Y
3. [Punjab mandi]: ₹Z

🌐 Source: AgMarkNet Website (Real-time)
```

---

### Test 2: Maharashtra Location

**Send WhatsApp**:
```
Give me onion budget in Kolhapur
```

**Expected logs**:
```
[DEBUG] Using AI to extract location and state...
[INFO] ✅ AI extracted state: Maharashtra
[DEBUG] ✅ Extracted city/location: Kolhapur
[DEBUG] 🌐 Scraping AgMarkNet for onion in Maharashtra...
[INFO] ✅ Scraping successful: Avg ₹X, Trend: Y
[INFO] ✅ AI generated detailed budget for onion in Kolhapur
```

**Expected response**:
```
🟢 Onion Cultivation Analysis
📍 Location: Kolhapur
🌾 Land: 1 acre

🎯 Feasibility: Highly Suitable
💬 Excellent climate for onion in Kolhapur
🌡️ Climate Match: Excellent

[... budget details ...]

📌 Data Sources:
- Market Price: AgMarkNet Website (Real-time)
- Costs: AI Estimate
```

---

### Test 3: No Location (Default)

**Send WhatsApp**:
```
What is wheat price?
```

**Expected logs**:
```
[DEBUG] Using AI to extract state for market query...
[INFO] ✅ AI extracted state: Maharashtra
[DEBUG] 🌐 Scraping AgMarkNet for wheat in Maharashtra...
```

**Expected**: Uses Maharashtra as smart default

---

### Test 4: Scraping Fails (Fallback)

**If scraping fails** (website down, HTML changed):

**Expected logs**:
```
[DEBUG] 🌐 Scraping AgMarkNet for wheat in Punjab...
[DEBUG] HTML received: 752 chars
[DEBUG] ❌ No prices found in HTML
[DEBUG] AgMarkNet API key not available, falling back to static
[INFO] ✅ Using static market data for wheat
```

**Expected response**:
```
📊 Wheat Market Prices
💰 Average Price: ₹2,450/quintal
📌 Source: Static Data (Weekly Update)
```

**Result**: Still works! Graceful fallback.

---

## Verification Checklist

After deployment, verify:

- [ ] Lambda deployed successfully
- [ ] Test with Punjab location (Amritsar)
- [ ] Test with Maharashtra location (Kolhapur)
- [ ] Test with Gujarat location (Ahmedabad)
- [ ] Test with no location (defaults to Maharashtra)
- [ ] Check logs show AI state extraction
- [ ] Check logs show scraping attempts
- [ ] Verify state-specific data returned
- [ ] Verify fallback works if scraping fails

---

## Watch Logs Live

```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

Keep this running while testing to see:
- AI state extraction in action
- Web scraping attempts
- HTML parsing results
- Fallback behavior

---

## Success Criteria

✅ **AI extraction working:**
- Logs show: `[INFO] ✅ AI extracted state: [State]`
- Correct state for each city
- Smart default when no location

✅ **Scraping working:**
- Logs show: `[INFO] ✅ Scraping successful`
- HTML > 10,000 chars received
- Valid prices extracted
- State-specific data returned

✅ **Fallback working:**
- If scraping fails, uses static data
- No errors or crashes
- Always get a response

---

## If Scraping Still Fails

### Scenario 1: Still Getting 752 Chars

**Possible causes:**
- Website requires cookies/session
- Website blocks automated requests
- Website changed structure

**Solution**: Fallback to static data works fine!

**Action**: Monitor success rate. If < 50%, consider disabling scraping again.

### Scenario 2: Wrong State Extracted

**Example**: "Amritsar" → "Maharashtra" (wrong!)

**Solution**: AI should get it right, but if not:
- Check AI prompt clarity
- Increase temperature slightly
- Add more examples to prompt

**Fallback**: Static data still works

### Scenario 3: Scraping Too Slow

**If scraping takes > 5 seconds:**

**Solution**: Reduce timeout or disable scraping
```python
# In scrape_agmarknet_website()
timeout=5.0  # Reduce from 8.0
```

---

## Cost Analysis

### Per Query Cost

**AI State Extraction:**
- Model: Nova Pro
- Input: ~100 tokens
- Output: ~10 tokens
- Cost: ~$0.0001

**Web Scraping:**
- HTTP request: Free
- Lambda time: ~1-3 seconds
- Cost: ~$0.00001

**Total per query**: ~$0.00011

**Monthly (1000 queries)**: ~$0.11

**Negligible!** Worth it for universal location support.

---

## Rollback Plan

If AI extraction or scraping causes issues:

### Disable AI Extraction

```python
def extract_state_with_ai(user_message, bedrock_client):
    # Quick disable
    return "Maharashtra"  # Always return default
```

### Disable Scraping

```python
def scrape_agmarknet_website(crop_name, state="Maharashtra"):
    # Quick disable
    return None  # Skip scraping
```

### Full Rollback

```bash
git checkout HEAD~1 src/lambda/lambda_whatsapp_kisaanmitra.py
git checkout HEAD~1 src/lambda/market_data_sources.py
./deploy_whatsapp.sh
```

---

## Summary

### Changes Made

1. ✅ Added `extract_state_with_ai()` function
2. ✅ Updated finance handler to use AI state
3. ✅ Updated market handler to use AI state
4. ✅ Re-enabled web scraping with AI state
5. ✅ Enhanced HTML parsing (5 patterns)
6. ✅ Better debugging logs
7. ✅ Removed 80+ hardcoded mappings

### Benefits

- 🌍 Universal location support (ANY city/state)
- 🎯 State-specific market data
- 🚀 Real-time prices via scraping
- 🧹 Cleaner code (100 lines removed)
- 🔧 Easier maintenance (no manual mapping)
- 💰 Minimal cost (~$0.11/month)

### Deploy Command

```bash
cd src/lambda && ./deploy_whatsapp.sh
```

### Test Commands

```
"What is wheat price in Amritsar?"
"Onion budget in Kolhapur"
"Rice price in Bangalore"
```

Watch logs to see AI extract states and scraping work!

