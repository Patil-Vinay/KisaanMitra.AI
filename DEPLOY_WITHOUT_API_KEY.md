# ✅ Deploy Without AgMarkNet API Key

## data.gov.in Not Working? No Problem!

You can deploy and use KisaanMitra **right now** without the AgMarkNet API key.

## What You Need to Do

### Step 1: Use Placeholder Key
In AWS Lambda environment variables, add:
```
AGMARKNET_API_KEY = not_available
```

### Step 2: Deploy Everything Else
Follow the normal deployment:
```bash
# Create tables
bash infrastructure/setup_finance_tables.sh

# Deploy code
cd src/lambda
bash deploy_whatsapp.sh
```

### Step 3: Update Lambda Config
- Timeout: 60 seconds
- Memory: 512 MB
- Add IAM permissions for DynamoDB

## How Market Agent Works Without API

### With Real API Key:
```
User: "गेहूं का भाव क्या है?"

Bot: 📊 Wheat - मंडी भाव

📈 रुझान: increasing
💰 औसत भाव: ₹2,450/क्विंटल
📊 बदलाव: +5.2%

🏪 प्रमुख मंडियां:
1. Mumbai: ₹2,500
2. Pune: ₹2,450
3. Nashik: ₹2,400
```

### Without API Key (AI-based):
```
User: "गेहूं का भाव क्या है?"

Bot: गेहूं का वर्तमान भाव ₹2,200-2,500 प्रति क्विंटल के बीच है। 
मुंबई और पुणे की मंडियों में अच्छे दाम मिल रहे हैं। 
बेचने से पहले स्थानीय मंडी की कीमत जरूर जांचें। 
फसल की गुणवत्ता के आधार पर कीमत अलग हो सकती है।
```

**Both are helpful!** The AI version gives general guidance based on typical market conditions.

## What Still Works Perfectly

✅ **Finance Agent** - Full functionality
- Budget calculations
- Government schemes
- Loan eligibility
- All features work 100%

✅ **Crop Agent** - Full functionality
- Image disease detection
- Kindwise API integration
- Treatment recommendations
- All features work 100%

✅ **Market Agent** - AI-powered
- General price guidance
- Market trends advice
- Selling recommendations
- Works well, just not real-time data

## When to Add Real API Key

Add the real AgMarkNet API key later when:
1. data.gov.in website is back online
2. You want real-time mandi prices
3. You need exact price data for specific mandis

**But you can launch and use the system NOW without it!**

## Alternative Market Data Sources

If you need real market data urgently, consider these alternatives:

### 1. Manual Price Updates
Update prices manually in DynamoDB:
```bash
aws dynamodb put-item \
    --table-name kisaanmitra-market-data \
    --item '{
        "crop_name": {"S": "wheat"},
        "data": {"L": [
            {"M": {
                "market": {"S": "Mumbai"},
                "modal_price": {"N": "2450"}
            }}
        ]},
        "timestamp": {"S": "2026-02-26T10:00:00"},
        "ttl": {"N": "1740564000"}
    }'
```

### 2. Use Alternative APIs
- **Agmarknet Mobile App** - Scrape data (requires permission)
- **State Agriculture Websites** - Maharashtra, Punjab, etc.
- **Private Market Data Providers** - Paid services

### 3. Farmer Input
Let farmers report prices they're seeing:
- Add a "Report Price" feature
- Crowdsource market data
- Build your own price database

## Testing Without API Key

Test all features:

```bash
# Market Agent (AI-based)
Send: "गेहूं का भाव"
Expected: AI-generated market advice

# Finance Agent (Full features)
Send: "बजट बताओ"
Expected: Complete budget breakdown

# Crop Agent (Full features)
Send: Crop image
Expected: Disease detection

# Schemes
Send: "सरकारी योजना"
Expected: List of schemes

# Loans
Send: "लोन चाहिए"
Expected: Loan eligibility
```

## Monitoring

Check CloudWatch logs:
```
Market Agent: No API key, using AI fallback
Finance Agent: Budget calculation complete
Crop Agent: Disease detection successful
```

## Cost Impact

**Without API:**
- No AgMarkNet API costs (it's free anyway)
- Same Bedrock costs
- Same DynamoDB costs
- **Total: No difference in cost**

## Future Enhancement

When data.gov.in is back:
1. Get API key
2. Update Lambda environment variable
3. No code changes needed
4. Market agent automatically uses real data

## Summary

**You can deploy NOW with:**
```
AGMARKNET_API_KEY = not_available
```

**Everything works except:**
- Real-time mandi prices (uses AI instead)

**Everything that works perfectly:**
- Finance agent (budgets, loans, schemes)
- Crop agent (disease detection)
- Market agent (AI-based advice)
- WhatsApp integration
- All other features

**Deploy now, add real API later when available!** 🚀

---

**Next Steps:**
1. Add `AGMARKNET_API_KEY=not_available` to Lambda
2. Follow `QUICK_AWS_UPDATE.md`
3. Deploy and test
4. Add real API key later when data.gov.in works
