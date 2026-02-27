# Quick Test Reference Card

## 🎯 Quick Start Testing

### Setup (5 min):
1. Open WhatsApp
2. Message bot number
3. Select language (English or Hindi)
4. Complete onboarding if new user

---

## ✅ Quick Validation Tests (10 min)

### Test 1: Language Persistence
```
1. Select English
2. Send: "My tomato leaves are yellow"
3. ✅ Response must be 100% English
4. Wait 5 minutes (cold start)
5. Send: "What is the price of onion?"
6. ✅ Still 100% English
```

### Test 2: Finance Agent Language
```
1. Select Hindi
2. Send: "मुझे टमाटर के लिए 2 एकड़ पुणे में बजट चाहिए"
3. ✅ Response must be 100% Hindi
4. Check for budget breakdown
5. ✅ All labels in Hindi
```

### Test 3: Routing Accuracy
```
1. Click "Budget Planning" menu
2. Send: "tomato 2 acre kolhapur"
3. ✅ Must generate budget (not crop advice)
4. ✅ Must show cost breakdown
```

### Test 4: Market Agent
```
1. Send: "बाजार भाव" (Hindi) or "market price" (English)
2. ✅ Must ask for crop name
3. Send: "onion"
4. ✅ Must show price with ₹ symbol
```

### Test 5: Greeting Behavior
```
1. Existing user sends: "Hi"
2. ✅ Must show main menu
3. ✅ Must NOT delete profile
4. Send: "reset"
5. ✅ Must restart onboarding
```

---

## 🔍 What to Check

### Every Response:
- [ ] Language matches selection (100%)
- [ ] No mixed language
- [ ] Clear and helpful
- [ ] Appropriate length (50-500 chars)
- [ ] Professional tone
- [ ] ₹ symbol (not $)

### Crop Agent:
- [ ] Disease/pest identification
- [ ] Treatment suggestions
- [ ] Actionable advice

### Market Agent:
- [ ] Price with ₹ symbol
- [ ] Location mentioned
- [ ] Source if available

### Finance Agent:
- [ ] Complete budget breakdown
- [ ] All cost categories
- [ ] Revenue and profit
- [ ] ROI if applicable
- [ ] Correct units (TON for sugarcane)

### General Agent:
- [ ] Friendly tone
- [ ] Offers help
- [ ] Guides to specific services

---

## 🚨 Red Flags

### FAIL if you see:
- ❌ Mixed language (English + Hindi)
- ❌ Wrong agent (budget → crop agent)
- ❌ $ symbol instead of ₹
- ❌ Response < 20 characters
- ❌ Response > 1000 characters
- ❌ Error messages
- ❌ Profile deleted on "Hi"
- ❌ Sugarcane in quintal (should be TON)

---

## 📊 Quick Test Matrix

| Agent | English Test | Hindi Test | Pass? |
|-------|-------------|------------|-------|
| Crop | "Yellow tomato leaves" | "टमाटर के पत्ते पीले" | [ ] |
| Market | "Onion price" | "प्याज का भाव" | [ ] |
| Finance | "Tomato budget 2 acres" | "टमाटर बजट 2 एकड़" | [ ] |
| General | "Hello" | "नमस्ते" | [ ] |

---

## 🎬 Test Sequence

### 5-Minute Smoke Test:
1. Language selection → Check persistence
2. Crop query → Check response quality
3. Market query → Check routing
4. Budget query → Check finance agent
5. General query → Check friendliness

### 30-Minute Core Test:
- 2 scenarios per agent per language
- Total: 16 tests
- Focus on critical paths

### Full Test Suite:
- All 80 scenarios
- 4-6 hours
- Complete documentation

---

## 📝 Quick Issue Template

```
Issue #___
Agent: Crop/Market/Finance/General
Language: English/Hindi
Input: "___"
Expected: "___"
Actual: "___"
Severity: Critical/High/Medium/Low
```

---

## 🔧 Quick Fixes

### If language mixing:
1. Check DynamoDB language_preference
2. Verify user_id matches
3. Check CloudWatch logs for language reads

### If wrong routing:
1. Check user state table
2. Verify AI orchestrator logs
3. Check conversation history

### If errors:
1. Check CloudWatch logs
2. Verify Lambda timeout (120s)
3. Check Bedrock throttling

---

## 📞 Quick Commands

### View Logs:
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

### Check Language:
```bash
aws dynamodb get-item \
  --table-name kisaanmitra-conversations \
  --key '{"user_id":{"S":"[PHONE]"},"timestamp":{"S":"language_preference"}}' \
  --region ap-south-1
```

### Check State:
```bash
aws dynamodb get-item \
  --table-name kisaanmitra-user-state \
  --key '{"user_id":{"S":"[PHONE]"}}' \
  --region ap-south-1
```

---

## ✅ Success Checklist

After testing, verify:
- [ ] All 4 agents respond correctly
- [ ] Language consistency 100%
- [ ] Routing accuracy 95%+
- [ ] Response quality good
- [ ] No errors or crashes
- [ ] Fast responses (< 5s)
- [ ] Good formatting
- [ ] Professional tone

---

## 🎯 Priority Tests

### Must Pass (Critical):
1. ✅ Language persistence
2. ✅ Finance agent Hindi support
3. ✅ Budget routing
4. ✅ No mixed language

### Should Pass (High):
5. ✅ Market price queries
6. ✅ Crop disease queries
7. ✅ General conversation
8. ✅ Greeting behavior

### Nice to Pass (Medium):
9. ✅ Response formatting
10. ✅ Emoji consistency
11. ✅ Source attribution
12. ✅ Error messages

---

**Print this card and keep it handy during testing!**

**Status:** Ready for Testing  
**Date:** February 27, 2026  
**Good luck! 🚀**
