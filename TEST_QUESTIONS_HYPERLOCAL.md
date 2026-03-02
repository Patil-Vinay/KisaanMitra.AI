# KisaanMitra Test Questions - Hyperlocal Features

## 🎯 Complete System Test Flow

### Phase 1: Onboarding (Required First)
Start fresh by saying:
```
Hi
```

Then complete the 11-question onboarding:
1. Name: `Vinay Patil`
2. Village: `Nandani`
3. District: `Sangli`
4. Land Size: `50 acres`
5. Soil Type: `Black Cotton Soil`
6. Water Source: `Drip Irrigation`
7. Current Crops: `sugarcane`
8. Past Crops: `rice, soybean, sugarcane`
9. Experience: `15 years`
10. Challenges: `Pests`
11. Goals: `Increase yield`

---

## Phase 2: Test All Features

### 1. Weather (Auto-fetches from profile)
```
weather
```
or click "🌤️ Weather Forecast" button

**Expected**: Shows weather for Sangli (your district) automatically

---

### 2. Knowledge Graph (Village Farmers)
```
Who else in my village grows sugarcane?
```
or
```
Show me farmers in Nandani
```

**Expected**: List of farmers from your village with their crops

---

### 3. Market Prices
```
What's the price of sugarcane?
```
or
```
tomato price
```

**Expected**: Current market prices from nearby mandis

---

### 4. Budget Planning
```
Show me budget for wheat
```
or
```
I want to plan budget for 10 acres of rice
```

**Expected**: Detailed cost breakdown with Excel sheet

---

### 5. Crop Health (Send Image)
Send a crop disease image (any plant disease photo)

**Expected**: 
- AI diagnosis with confidence score
- **HYPERLOCAL BONUS**: Treatments that worked for nearby farmers!
- Alert if other farmers in your village reported same disease

---

### 6. General Farming Questions
```
How do I control pests in sugarcane?
```
or
```
Best time to harvest rice?
```

**Expected**: AI-powered farming advice

---

## 🌟 NEW HYPERLOCAL FEATURES TO TEST

### 7. Disease Alerts in Your Village
```
What diseases are affecting farmers in my village?
```
or
```
Show me disease reports in Nandani
```

**Expected**: List of recent diseases reported by farmers in your village

---

### 8. Treatment Recommendations
```
What treatment works for Red Rot?
```
or
```
How did other farmers cure Blast Disease?
```

**Expected**: 
- Treatments used by nearby farmers
- Effectiveness scores (1-10)
- Cost and duration
- Success notes

---

### 9. Best Practices from Community
```
Best practices for sugarcane farming
```
or
```
Show me tips for rice cultivation
```

**Expected**: 
- Community-shared farming techniques
- Upvote counts (popularity)
- Practical tips from local farmers

---

### 10. Specific Best Practice Categories
```
Pest control tips for cotton
```
or
```
Irrigation methods for wheat
```

**Expected**: Category-specific practices (pest control, irrigation, fertilizer, etc.)

---

## 🔥 Advanced Test Scenarios

### Scenario A: Disease Outbreak Detection
1. Send crop disease image (sugarcane)
2. System detects "Red Rot"
3. **Check response for**:
   - AI diagnosis
   - Treatments from nearby farmers (2-3 options with scores)
   - Alert: "X farmers in Nandani reported diseases in sugarcane"

### Scenario B: Community Knowledge Discovery
```
What are farmers in Sangli doing for pest control?
```

**Expected**: Best practices from your district with upvotes

### Scenario C: Treatment Success Stories
```
Show me successful treatments for Bollworm
```

**Expected**: 
- Neem oil spray (8/10, ₹300, 10 days)
- Bt cotton variety (9/10, ₹0, preventive)
- Pheromone traps (7/10, ₹400, 21 days)

---

## 📊 What Makes Responses "Hyperlocal"?

When you send a disease image, the response now includes:

**Before (Just AI)**:
```
🔍 Disease Detected: Red Rot
Confidence: 85%
Symptoms: Reddish discoloration...
Treatment: Use fungicide...
```

**After (AI + Hyperlocal)**:
```
🔍 Disease Detected: Red Rot
Confidence: 85%
Symptoms: Reddish discoloration...

──────────────────────────────
💊 Successful Treatments for Red Rot

Farmers in your area found these treatments effective:

1. Remove infected stalks immediately
   Effectiveness: 8/10 ⭐
   Cost: ₹0
   Duration: 7 days
   Note: Burn infected material, don't compost

2. Copper oxychloride spray
   Effectiveness: 7/10 ⭐
   Cost: ₹500
   Duration: 14 days
   Note: Preventive spray before monsoon

⚠️ Alert: 3 farmers in Nandani reported diseases in sugarcane.
```

---

## 🎭 Demo Script (For Presentation)

**1. Introduction** (30 sec)
"KisaanMitra is not just an AI assistant - it's a community-powered platform where farmers learn from each other."

**2. Show Onboarding** (1 min)
Complete quick onboarding with Nandani village, Sangli district, sugarcane crop.

**3. Basic Features** (1 min)
- Weather: Auto-fetches for Sangli
- Market: "sugarcane price"
- Knowledge Graph: "farmers in my village"

**4. Hyperlocal Magic** (2 min)
- Send disease image
- **Highlight**: "See how it shows treatments that worked for nearby farmers!"
- **Highlight**: "It even alerts if multiple farmers reported same disease!"

**5. Community Knowledge** (1 min)
- "Best practices for sugarcane"
- **Highlight**: "These are real tips from farmers in Maharashtra, ranked by popularity!"

**6. Impact** (30 sec)
"50 disease reports, 11 successful treatments, 11 best practices - all from the community. This creates a virtuous cycle where every farmer helps the next one."

---

## 🐛 Troubleshooting

### If hyperlocal features don't work:
1. Check Lambda logs: `aws logs tail /aws/lambda/whatsapp-llama-bot --follow`
2. Verify tables exist: `aws dynamodb list-tables --region ap-south-1`
3. Check data: `aws dynamodb scan --table-name kisaanmitra-disease-reports --region ap-south-1 | jq '.Items | length'`

### If no treatments show up:
- The disease name must match exactly (e.g., "Red Rot", "Blast Disease")
- Check seed data ran successfully
- Try: "What treatment works for Blast Disease?" (guaranteed to have data)

---

## 📈 Success Metrics

After testing, you should see:
- ✅ Disease automatically reported to hyperlocal DB
- ✅ Treatment recommendations from community
- ✅ Disease alerts if multiple reports
- ✅ Best practices with upvote counts
- ✅ All conversations saved to Streamlit dashboard

---

## 🎉 Key Differentiators

**Other AI Farming Apps**:
- Generic AI advice
- Same answer for everyone
- No community learning

**KisaanMitra Hyperlocal**:
- ✅ AI diagnosis + community treatments
- ✅ Village-specific disease alerts
- ✅ Learn from nearby farmers' successes
- ✅ Best practices ranked by community
- ✅ Builds collective intelligence over time

---

## Quick Test Checklist

- [ ] Onboarding completed (11 questions)
- [ ] Weather auto-fetches district
- [ ] Knowledge graph shows village farmers
- [ ] Market prices work
- [ ] Budget planning generates Excel
- [ ] Disease image shows hyperlocal treatments
- [ ] Disease alerts for village
- [ ] Best practices with upvotes
- [ ] All conversations in Streamlit

---

**Ready to test!** Start with "Hi" on WhatsApp: +1 (555) 141-1052
