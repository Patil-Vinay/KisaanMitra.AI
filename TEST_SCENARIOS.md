# WhatsApp Bot Test Scenarios

## 10 Test Questions to Validate All Features

### 1. Greeting Test (GREETING Agent)
**Message**: `Hi`

**Expected**:
- Agent: GREETING
- Response: Friendly welcome message
- Time: <1 second

---

### 2. Simple Crop Budget (FINANCE Agent)
**Message**: `I want to grow tomato`

**Expected**:
- Agent: FINANCE
- Crop detected: tomato
- Location: Maharashtra (default)
- Land: 1 acre (default)
- Response: Full budget breakdown with costs, yield, profit, ROI
- Time: 7-10 seconds

---

### 3. Crop Budget with Location (FINANCE Agent)
**Message**: `Give me potato budget in Punjab`

**Expected**:
- Agent: FINANCE
- Crop detected: potato
- Location: Punjab
- Land: 1 acre (default)
- Response: Budget specific to Punjab region
- Time: 7-10 seconds

---

### 4. Crop Budget with Land Size (FINANCE Agent)
**Message**: `Chilly farming cost for 5 acre`

**Expected**:
- Agent: FINANCE
- Crop detected: chilly
- Location: Maharashtra (default)
- Land: 5 acres
- Response: Budget scaled for 5 acres
- Time: 7-10 seconds

---

### 5. Complete Budget Query (FINANCE Agent)
**Message**: `I want mushroom cultivation budget for 2 acre in Kerala`

**Expected**:
- Agent: FINANCE
- Crop detected: mushroom
- Location: Kerala
- Land: 2 acres
- Response: Detailed mushroom budget for Kerala
- Time: 7-10 seconds

---

### 6. Market Price Query (MARKET Agent)
**Message**: `What is wheat price today?`

**Expected**:
- Agent: MARKET
- Crop detected: wheat
- Response: Current wheat prices with trend, range, top mandis
- Data source: Static (instant)
- Time: <2 seconds

---

### 7. Market Price - Different Crop (MARKET Agent)
**Message**: `onion mandi rate`

**Expected**:
- Agent: MARKET
- Crop detected: onion
- Response: Onion prices with Lasalgaon, Nashik mandis
- Time: <2 seconds

---

### 8. Crop Disease Query (CROP Agent)
**Message**: `My rice plants have brown spots on leaves`

**Expected**:
- Agent: CROP
- Response: Disease diagnosis and treatment advice
- Time: 2-3 seconds

---

### 9. Government Schemes (FINANCE Agent)
**Message**: `Tell me about government schemes for farmers`

**Expected**:
- Agent: FINANCE
- Response: PM-KISAN, PMFBY, KCC, and other schemes
- Time: 1-2 seconds

---

### 10. Loan Eligibility (FINANCE Agent)
**Message**: `I need a loan for farming`

**Expected**:
- Agent: FINANCE
- Response: KCC loan details with max amount, interest rate, EMI
- Time: 1-2 seconds

---

## Advanced Test Scenarios

### 11. Conversation Context Test
**Message 1**: `I want to grow cotton`
**Message 2**: `How much will it cost?`

**Expected**:
- Message 1: Cotton budget
- Message 2: Should remember "cotton" from context and provide budget
- Tests: Conversation memory

---

### 12. Uncommon Crop Test
**Message**: `Give me brinjal budget`

**Expected**:
- Agent: FINANCE
- Crop detected: brinjal (or eggplant)
- Response: AI-generated budget for brinjal
- Tests: AI flexibility for any crop

---

### 13. Regional Variation Test
**Message**: `Sugarcane cost in Maharashtra vs Tamil Nadu`

**Expected**:
- Agent: FINANCE
- Response: Should mention regional differences
- Tests: Location awareness

---

### 14. Mixed Query Test
**Message**: `I want to grow soybean, what's the market price and budget?`

**Expected**:
- Agent: FINANCE (budget keywords dominate)
- Response: Budget for soybean
- Follow-up: User can ask "what about price?" for market data

---

### 15. General Farming Advice (GENERAL Agent)
**Message**: `What is the best time to plant wheat?`

**Expected**:
- Agent: GENERAL
- Response: Farming advice about wheat planting season
- Time: 2-3 seconds

---

## What to Check in Logs

For each test, verify in CloudWatch:

1. ✅ **Agent Selection**: `[INFO] 🎯 SELECTED AGENT: {AGENT}`
2. ✅ **Crop Detection**: `[INFO] ✅ AI extracted crop: {crop}`
3. ✅ **Location Detection**: `[DEBUG] Location extracted: {location}`
4. ✅ **Budget Generation**: `[DEBUG] Budget parsing complete - Total Cost: ₹X, Profit: ₹Y`
5. ✅ **Response Time**: Check timestamps
6. ✅ **WhatsApp Delivery**: `[INFO] ✅ WhatsApp API response: 200`
7. ✅ **No Errors**: No `[ERROR]` tags

## Quick Test Command

```bash
# Watch logs while testing
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep -E "\[INFO\]|\[ERROR\]|AGENT"
```

## Success Criteria

- All 10 scenarios respond correctly
- Correct agent selected for each query
- Response times within expected ranges
- Zero errors in CloudWatch logs
- WhatsApp delivery 100% success rate
- Conversation memory working (context test)
- AI handles any crop name (not just hardcoded ones)

## Testing Order

**Recommended sequence:**
1. Start with Greeting (#1) - simplest
2. Test Market Agent (#6, #7) - fast responses
3. Test Finance Agent (#2, #3, #4, #5) - core functionality
4. Test Crop Agent (#8) - disease detection
5. Test schemes/loans (#9, #10) - finance variations
6. Test conversation memory (#11) - advanced feature
7. Test uncommon crops (#12) - AI flexibility

Happy testing! 🚀
