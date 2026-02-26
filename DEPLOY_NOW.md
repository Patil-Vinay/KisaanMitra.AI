# 🚀 Deploy Now - Copy & Paste Commands

## Quick Deploy (Recommended)

```bash
cd src/lambda && ./deploy_whatsapp.sh
```

That's it! The script handles everything.

---

## What Happens During Deployment

```
🚀 Deploying KisaanMitra WhatsApp Lambda...
📦 Including dependencies...
✅ Package created
⏳ Waiting for update to complete...
✅ Deployment complete!
```

**Time**: 30-60 seconds

---

## After Deployment - Test Commands

### Test 1: Check Lambda Status

```bash
aws lambda get-function \
  --function-name whatsapp-llama-bot \
  --region ap-south-1 \
  --query 'Configuration.[FunctionName,LastModified,State]' \
  --output table
```

**Expected**: Shows function updated with recent timestamp

---

### Test 2: View Live Logs

```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

**Keep this running** while you test with WhatsApp messages

---

### Test 3: Send WhatsApp Test Message

**Message 1**: Market Price Query
```
What is wheat price?
```

**Expected Response**:
```
📊 Wheat Market Prices

📈 Trend: Stable
💰 Average Price: ₹2,450/quintal
📊 Range: ₹2,200 - ₹2,600

🏪 Top Mandis:
1. Mumbai APMC: ₹2,500
2. Pune APMC: ₹2,450
3. Nashik: ₹2,400

📅 Updated: 2026-02-26
📌 Source: Static Data

💡 Tip: Check multiple mandis before selling
```

**Expected Logs**:
```
[DEBUG] get_fast_market_prices called for: wheat, state: Maharashtra
[DEBUG] AgMarkNet API key not available, using static data
[INFO] ✅ Using static market data for wheat
[DEBUG] Price: ₹2,450, Trend: stable
```

✅ **Success indicators**:
- Response in < 1 second
- Shows 📌 Static Data label
- No scraping failure messages
- Clean logs

---

**Message 2**: Budget Query
```
Give me wheat budget for 1 acre in Mumbai
```

**Expected Response**:
```
🌾 Wheat Crop Budget (1 acre)

💰 COSTS:
Seeds: ₹3,500 🤖
Fertilizer: ₹8,000 🤖
Labor: ₹12,000 🤖
Irrigation: ₹4,000 🤖
Total Cost: ₹27,500

📊 REVENUE:
Expected Yield: 25 quintals
Market Price: ₹2,450/quintal 📌
Total Revenue: ₹61,250

💵 PROFIT: ₹33,750

🎯 FEASIBILITY: HIGHLY SUITABLE 🟢
✓ Climate compatible
✓ Good market demand
✓ Proven in region

📅 Best Season: Rabi (Oct-Mar)

📌 Data Sources:
- Market Price: Static Data (weekly update)
- Costs: AI Estimate (verify locally)
```

**Expected Logs**:
```
[INFO] 🎯 SELECTED AGENT: finance
[INFO] ✅ AI extracted crop: wheat
[DEBUG] get_fast_market_prices called for: wheat
[INFO] ✅ Using static market data for wheat
[DEBUG] Market price source: static_data
[INFO] ✅ AI generated detailed budget for wheat
```

✅ **Success indicators**:
- Response in 6-8 seconds
- Shows feasibility analysis
- Shows data source labels
- All costs present
- No errors in logs

---

## Verification Checklist

After testing, verify:

- [ ] Lambda deployed successfully
- [ ] Market price query works (< 1s response)
- [ ] Budget query works (6-8s response)
- [ ] Logs are clean (no scraping failures)
- [ ] Data source labels show (📌 for static)
- [ ] Feasibility analysis included
- [ ] No error messages

---

## If Something Goes Wrong

### Problem: Deployment fails

**Check AWS credentials:**
```bash
aws sts get-caller-identity
```

**Check Lambda exists:**
```bash
aws lambda list-functions --region ap-south-1 | grep whatsapp
```

---

### Problem: No response from WhatsApp

**Check Lambda logs:**
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

**Check WhatsApp token:**
```bash
aws lambda get-function-configuration \
  --function-name whatsapp-llama-bot \
  --region ap-south-1 \
  --query 'Environment.Variables.WHATSAPP_TOKEN'
```

---

### Problem: Slow responses

**Check memory allocation:**
```bash
aws lambda get-function-configuration \
  --function-name whatsapp-llama-bot \
  --region ap-south-1 \
  --query 'MemorySize'
```

**Should be**: 2048 MB

**If not, update:**
```bash
aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --memory-size 2048 \
  --region ap-south-1
```

---

### Problem: Bedrock errors

**Check Bedrock permissions:**
```bash
aws lambda get-function \
  --function-name whatsapp-llama-bot \
  --region ap-south-1 \
  --query 'Configuration.Role'
```

**Update permissions** (already in deploy script):
```bash
# Run the deploy script again
cd src/lambda && ./deploy_whatsapp.sh
```

---

## Success Criteria

Your deployment is successful when:

✅ Lambda shows recent update timestamp
✅ Market price query responds in < 1 second
✅ Budget query responds in 6-8 seconds
✅ Logs show clean output (no scraping failures)
✅ Data source labels appear correctly
✅ No error messages in CloudWatch
✅ All test scenarios pass

---

## Next Steps After Deployment

### 1. Monitor for 24 Hours

```bash
# Watch logs for any issues
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

### 2. Test All Crops

Send test messages for all 8 crops:
- Wheat
- Rice
- Cotton
- Onion
- Potato
- Tomato
- Sugarcane
- Soybean

### 3. Schedule Weekly Updates

**Every Monday** (5 minutes):
1. Visit AgMarkNet website
2. Note average prices
3. Update `STATIC_MARKET_PRICES` in code
4. Run `./deploy_whatsapp.sh`

### 4. Optional: Get API Key

If you want real-time data:
1. Register at https://data.gov.in
2. Get API key (free)
3. Add to Lambda:
   ```bash
   aws lambda update-function-configuration \
     --function-name whatsapp-llama-bot \
     --environment Variables="{AGMARKNET_API_KEY=your_key_here}" \
     --region ap-south-1
   ```

---

## Documentation Reference

**Quick Start:**
- `DEPLOY_NOW.md` (this file)
- `QUICK_FIX_SUMMARY.md`

**Technical Details:**
- `SCRAPING_REALITY_CHECK.md`
- `SCRAPING_FIX_DEPLOYED.md`
- `BEFORE_AFTER_COMPARISON.md`

**Features:**
- `FEASIBILITY_ANALYSIS_UPGRADE.md`
- `DEBUG_LOGGING_GUIDE.md`
- `TEST_SCENARIOS.md`

**Data Sources:**
- `DATA_SOURCES_EXPLAINED.md`
- `DATA_SOURCE_REALITY.md`

---

## One-Line Deploy

```bash
cd src/lambda && ./deploy_whatsapp.sh && aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

This will:
1. Deploy the updated code
2. Automatically start watching logs
3. Show you real-time output

**Now send a test WhatsApp message and watch it work!** 🎉

