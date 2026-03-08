# Budget Planning Feature - Testing Guide

## Quick Test

Send this message to WhatsApp: **"Sugarcane 50% of my land You know my location"**

## Expected Behavior

### 1. Routing
```
[AI] Routing selected: FINANCE ✅
[ROUTING] Selected agent: FINANCE ✅
[FINANCE AGENT] Sub-type: budget ✅
```

### 2. Response Format
You should receive a structured budget plan like:

```
💰 *Budget Plan: Sugarcane - 10 acres*
📍 Location: Sangli

*📊 COST BREAKDOWN*

*🌱 Input Costs:*
• Seeds/Seedlings: ₹[amount] (₹[rate]/acre)
• Fertilizers (NPK, Urea): ₹[amount]
• Pesticides/Fungicides: ₹[amount]
• Water/Irrigation: ₹[amount]

*👷 Labor Costs:*
• Land preparation: ₹[amount]
• Sowing/Planting: ₹[amount]
• Weeding & Maintenance: ₹[amount]
• Harvesting: ₹[amount]

*🚜 Other Costs:*
• Equipment rental: ₹[amount]
• Transportation: ₹[amount]

*💵 Total Investment: ₹[total]*

*📈 REVENUE PROJECTION*

• Expected Yield: [quantity] quintals (₹[yield]/acre)
• Current Market Price: ₹[price]/quintal
• *Gross Revenue: ₹[amount]*

*💚 PROFIT ANALYSIS*

• *Net Profit: ₹[amount]*
• *Profit Margin: [percentage]%*
• *ROI: [percentage]%*
• Break-even Yield: [quantity] quintals

*🎯 KEY RECOMMENDATIONS*

• [Specific cost-saving tip]
• [Yield improvement suggestion]
• [Market timing advice]

*💡 Pro Tips:*
• Best planting season: [months]
• Harvest time: [months after planting]
• Government schemes: [relevant scheme if applicable]
```

### 3. Data Validation

Check that the numbers are realistic:

**For Sugarcane (10 acres in Sangli):**
- Total Cost: ₹7,00,000 - ₹8,50,000 (₹70k-85k per acre)
- Expected Yield: 300-400 quintals (30-40 tons)
- Market Price: ₹300-400 per quintal
- Gross Revenue: ₹9,00,000 - ₹16,00,000
- Net Profit: ₹50,000 - ₹7,50,000
- **ROI: 40-60%** (NOT 200%+)

### 4. Profile Integration

The response should use your profile data:
- Name: Parth Nikam
- Village: Nandani
- District: Sangli
- Land: 20 acres (50% = 10 acres)
- Current Crops: sugarcane

## Check Logs

```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep -E "ROUTING|FINANCE|Budget"
```

## Other Test Queries

### Test 2: Direct Budget Request
```
Message: "Budget planning for wheat"
Expected: FINANCE → budget sub-type
```

### Test 3: Cost Query
```
Message: "What is the cost of growing tomato in 5 acres?"
Expected: FINANCE → budget sub-type
```

### Test 4: Profit Query
```
Message: "How much profit in onion farming?"
Expected: FINANCE → budget sub-type
```

### Test 5: Profile-Aware
```
Message: "Give me budget for my crop"
Expected: FINANCE → budget sub-type → Uses sugarcane from profile
```

## Success Criteria

✅ Routes to FINANCE agent (not GENERAL)
✅ Sub-type is "budget" (not "general")
✅ Response includes complete budget breakdown
✅ ROI is realistic (40-60% for sugarcane)
✅ Uses profile data (Sangli, 10 acres)
✅ WhatsApp formatting displays correctly
✅ All sections present: costs, revenue, profit, recommendations

## Troubleshooting

### If routing to GENERAL:
- Check AI routing prompt in `ai_service.py`
- Verify deployment was successful
- Check Lambda logs for routing decision

### If sub-type is "general":
- Check finance routing prompt in `finance_agent.py`
- Verify deployment included latest changes
- Check logs for sub-type detection

### If ROI is unrealistic (>100%):
- Check Claude prompt guidelines in `finance_agent.py`
- Verify realistic data ranges are in prompt
- Report specific numbers for adjustment

### If formatting is broken:
- Check WhatsApp markdown syntax
- Verify emojis display correctly
- Test on actual mobile device

## Deployment Info

- Function: `whatsapp-llama-bot`
- Region: `ap-south-1`
- Handler: `lambda_handler_v2.lambda_handler`
- Last Deployed: 2026-03-02 23:08 UTC
- Status: Active

## Contact

If issues persist:
1. Check CloudWatch logs
2. Verify Lambda deployment status
3. Test with different query variations
4. Report specific error messages
