# Manual Test Execution Guide

## Date: February 27, 2026
## Status: Ready for Testing
## Total Tests: 80 (40 English + 40 Hindi)

---

## CRITICAL FIXES APPLIED ✅

1. ✅ Added language parameter to finance agent
2. ✅ Updated finance agent call to pass language
3. ✅ Added bilingual system prompts to all agents
4. ✅ Added strict language enforcement ("CRITICAL: Respond ONLY in...")
5. ✅ All syntax checks passed

---

## TEST EXECUTION INSTRUCTIONS

### Prerequisites:
1. Deploy latest code to Lambda
2. Have WhatsApp test number ready
3. Clear any existing language preferences
4. Prepare to screenshot responses

### Test Format:
```
Test ID: [agent]_[lang]_[number]
Input: [user message]
Expected: [what should happen]
Actual: [what actually happened]
Status: PASS/FAIL
Issues: [any problems found]
```

---

## CROP AGENT TESTS (20 total)

### English Tests (10)

#### Test: crop_en_1
**Input:** "My tomato leaves are turning yellow"
**Expected:**
- Response in English only
- Mentions possible causes (nitrogen deficiency, overwatering, disease)
- Suggests treatment or next steps
- 2-4 sentences
- No Hindi words

**How to Test:**
1. Select English language
2. Send message
3. Check response language
4. Verify content quality
5. Record result

**Pass Criteria:**
- ✅ 100% English
- ✅ Helpful diagnosis
- ✅ Actionable advice
- ✅ Appropriate length

---

#### Test: crop_en_2
**Input:** "White spots on wheat crop"
**Expected:**
- Identifies as fungal disease (powdery mildew)
- Suggests fungicide treatment
- English only

---

#### Test: crop_en_3
**Input:** "Cotton leaves have holes"
**Expected:**
- Identifies pest problem (bollworm/caterpillar)
- Suggests pesticide or organic control
- English only

---

#### Test: crop_en_4
**Input:** "Sugarcane turning brown"
**Expected:**
- Identifies disease or nutrient issue
- Suggests investigation steps
- English only

---

#### Test: crop_en_5
**Input:** "Rice plants not growing well"
**Expected:**
- Lists possible causes (nutrients, water, soil)
- Asks for more details or suggests checks
- English only

---

#### Test: crop_en_6
**Input:** "Black spots on potato leaves"
**Expected:**
- Identifies late blight (urgent)
- Suggests immediate fungicide application
- English only

---

#### Test: crop_en_7
**Input:** "Onion bulbs rotting"
**Expected:**
- Identifies root rot or storage issue
- Suggests drainage improvement
- English only

---

#### Test: crop_en_8
**Input:** "Chilli plants wilting"
**Expected:**
- Identifies wilt disease or water stress
- Suggests diagnosis steps
- English only

---

#### Test: crop_en_9
**Input:** "Soybean leaves curling"
**Expected:**
- Identifies virus or pest
- Suggests control measures
- English only

---

#### Test: crop_en_10
**Input:** "Maize cobs have worms"
**Expected:**
- Identifies corn borer
- Suggests timing for control
- English only

---

### Hindi Tests (10)

#### Test: crop_hi_1
**Input:** "मेरे टमाटर के पत्ते पीले हो रहे हैं"
**Expected:**
- हिंदी में जवाब
- संभावित कारण (नाइट्रोजन की कमी, अधिक पानी, रोग)
- उपचार सुझाव
- कोई अंग्रेजी शब्द नहीं

---

#### Test: crop_hi_2
**Input:** "गेहूं की फसल पर सफेद धब्बे"
**Expected:**
- फंगल रोग पहचान
- फफूंदनाशक सुझाव
- केवल हिंदी

---

#### Test: crop_hi_3
**Input:** "कपास के पत्तों में छेद हैं"
**Expected:**
- कीट समस्या पहचान
- कीटनाशक सुझाव
- केवल हिंदी

---

#### Test: crop_hi_4
**Input:** "गन्ना भूरा हो रहा है"
**Expected:**
- रोग या पोषक तत्व की कमी
- जांच के कदम
- केवल हिंदी

---

#### Test: crop_hi_5
**Input:** "धान के पौधे अच्छे से नहीं बढ़ रहे"
**Expected:**
- संभावित कारण
- जांच सुझाव
- केवल हिंदी

---

#### Test: crop_hi_6
**Input:** "आलू के पत्तों पर काले धब्बे"
**Expected:**
- लेट ब्लाइट पहचान
- तत्काल उपचार
- केवल हिंदी

---

#### Test: crop_hi_7
**Input:** "प्याज सड़ रहा है"
**Expected:**
- जड़ सड़न पहचान
- जल निकासी सुधार
- केवल हिंदी

---

#### Test: crop_hi_8
**Input:** "मिर्च के पौधे मुरझा रहे हैं"
**Expected:**
- विल्ट रोग या पानी की कमी
- निदान कदम
- केवल हिंदी

---

#### Test: crop_hi_9
**Input:** "सोयाबीन के पत्ते मुड़ रहे हैं"
**Expected:**
- वायरस या कीट पहचान
- नियंत्रण उपाय
- केवल हिंदी

---

#### Test: crop_hi_10
**Input:** "मक्का में कीड़े लग गए हैं"
**Expected:**
- कॉर्न बोरर पहचान
- नियंत्रण समय
- केवल हिंदी

---

## MARKET AGENT TESTS (20 total)

### English Tests (10)

#### Test: market_en_1
**Input:** "What is tomato price today?"
**Expected:**
- Current price with ₹ symbol
- Trend if available
- Source mentioned
- English only

---

#### Test: market_en_2
**Input:** "Onion market rate in Pune"
**Expected:**
- Pune-specific price
- Market location
- English only

---

#### Test: market_en_3
**Input:** "Wheat mandi bhav"
**Expected:**
- Mandi price
- MSP if applicable
- English only

---

#### Test: market_en_4
**Input:** "Cotton selling price"
**Expected:**
- Current rate
- Unit (quintal)
- English only

---

#### Test: market_en_5
**Input:** "Rice market rate today"
**Expected:**
- Current price
- Date mentioned
- English only

---

#### Test: market_en_6
**Input:** "Sugarcane price per ton"
**Expected:**
- FRP/SAP price
- Unit is TON
- English only

---

#### Test: market_en_7
**Input:** "Potato wholesale price"
**Expected:**
- Wholesale rate
- Market location
- English only

---

#### Test: market_en_8
**Input:** "Soybean market rate in Maharashtra"
**Expected:**
- Maharashtra price
- Multiple mandis if available
- English only

---

#### Test: market_en_9
**Input:** "Chilli price today"
**Expected:**
- Current rate
- Variety if available
- English only

---

#### Test: market_en_10
**Input:** "Maize selling rate"
**Expected:**
- Current price
- Usage type if available
- English only

---

### Hindi Tests (10)

#### Test: market_hi_1
**Input:** "टमाटर का भाव क्या है?"
**Expected:**
- वर्तमान कीमत ₹ के साथ
- रुझान यदि उपलब्ध हो
- केवल हिंदी

---

#### Test: market_hi_2
**Input:** "प्याज की कीमत पुणे में"
**Expected:**
- पुणे विशिष्ट कीमत
- बाजार स्थान
- केवल हिंदी

---

#### Test: market_hi_3
**Input:** "गेहूं का मंडी भाव"
**Expected:**
- मंडी कीमत
- MSP यदि लागू हो
- केवल हिंदी

---

#### Test: market_hi_4
**Input:** "कपास की बिक्री दर"
**Expected:**
- वर्तमान दर
- इकाई (क्विंटल)
- केवल हिंदी

---

#### Test: market_hi_5
**Input:** "चावल का बाजार भाव आज"
**Expected:**
- वर्तमान कीमत
- तारीख उल्लेख
- केवल हिंदी

---

#### Test: market_hi_6
**Input:** "गन्ने की कीमत प्रति टन"
**Expected:**
- FRP/SAP कीमत
- इकाई टन है
- केवल हिंदी

---

#### Test: market_hi_7
**Input:** "आलू का थोक भाव"
**Expected:**
- थोक दर
- बाजार स्थान
- केवल हिंदी

---

#### Test: market_hi_8
**Input:** "सोयाबीन का बाजार भाव महाराष्ट्र में"
**Expected:**
- महाराष्ट्र कीमत
- कई मंडियां यदि उपलब्ध हों
- केवल हिंदी

---

#### Test: market_hi_9
**Input:** "मिर्च की कीमत आज"
**Expected:**
- वर्तमान दर
- किस्म यदि उपलब्ध हो
- केवल हिंदी

---

#### Test: market_hi_10
**Input:** "मक्का की बिक्री दर"
**Expected:**
- वर्तमान कीमत
- उपयोग प्रकार यदि उपलब्ध हो
- केवल हिंदी

---

## FINANCE AGENT TESTS (20 total)

### English Tests (10)

#### Test: finance_en_1
**Input:** "I need tomato budget for 2 acres in Pune"
**Expected:**
- Complete budget breakdown
- All cost categories
- Revenue and profit
- ₹ symbol used
- English only

---

#### Test: finance_en_2
**Input:** "What is the cost of growing wheat on 5 acres?"
**Expected:**
- Detailed cost analysis
- Per-acre and total
- English only

---

#### Test: finance_en_3
**Input:** "Cotton cultivation budget for 3 acres in Nagpur"
**Expected:**
- Location-specific budget
- Climate suitability
- English only

---

#### Test: finance_en_4
**Input:** "Sugarcane farming cost 1 acre Kolhapur"
**Expected:**
- Budget with TON unit
- Not quintal
- English only

---

#### Test: finance_en_5
**Input:** "Rice cultivation expenses for 4 acres"
**Expected:**
- Complete expense breakdown
- Season mentioned
- English only

---

#### Test: finance_en_6
**Input:** "Onion farming budget 2 acres Mumbai"
**Expected:**
- Budget with market proximity
- Storage costs
- English only

---

#### Test: finance_en_7
**Input:** "Potato cultivation cost analysis 3 acres"
**Expected:**
- Detailed cost-benefit
- ROI calculated
- English only

---

#### Test: finance_en_8
**Input:** "Soybean farming budget 5 acres Maharashtra"
**Expected:**
- State-specific budget
- MSP mentioned
- English only

---

#### Test: finance_en_9
**Input:** "Chilli cultivation expenses 1 acre"
**Expected:**
- High-value crop budget
- Labor costs highlighted
- English only

---

#### Test: finance_en_10
**Input:** "Maize farming cost 2 acres Nashik"
**Expected:**
- Location-specific budget
- Irrigation costs
- English only

---

### Hindi Tests (10)

#### Test: finance_hi_1
**Input:** "मुझे टमाटर के लिए 2 एकड़ पुणे में बजट चाहिए"
**Expected:**
- पूर्ण बजट विवरण
- सभी लागत श्रेणियां
- राजस्व और लाभ
- ₹ प्रतीक
- केवल हिंदी

---

#### Test: finance_hi_2
**Input:** "5 एकड़ में गेहूं उगाने की लागत क्या है?"
**Expected:**
- विस्तृत लागत विश्लेषण
- प्रति एकड़ और कुल
- केवल हिंदी

---

#### Test: finance_hi_3
**Input:** "नागपुर में 3 एकड़ कपास की खेती का बजट"
**Expected:**
- स्थान विशिष्ट बजट
- जलवायु उपयुक्तता
- केवल हिंदी

---

#### Test: finance_hi_4
**Input:** "कोल्हापुर में 1 एकड़ गन्ने की खेती की लागत"
**Expected:**
- टन इकाई के साथ बजट
- क्विंटल नहीं
- केवल हिंदी

---

#### Test: finance_hi_5
**Input:** "4 एकड़ धान की खेती का खर्च"
**Expected:**
- पूर्ण खर्च विवरण
- मौसम उल्लेख
- केवल हिंदी

---

#### Test: finance_hi_6
**Input:** "मुंबई में 2 एकड़ प्याज की खेती का बजट"
**Expected:**
- बाजार निकटता के साथ बजट
- भंडारण लागत
- केवल हिंदी

---

#### Test: finance_hi_7
**Input:** "3 एकड़ आलू की खेती की लागत विश्लेषण"
**Expected:**
- विस्तृत लागत-लाभ
- ROI गणना
- केवल हिंदी

---

#### Test: finance_hi_8
**Input:** "महाराष्ट्र में 5 एकड़ सोयाबीन की खेती का बजट"
**Expected:**
- राज्य विशिष्ट बजट
- MSP उल्लेख
- केवल हिंदी

---

#### Test: finance_hi_9
**Input:** "1 एकड़ मिर्च की खेती का खर्च"
**Expected:**
- उच्च मूल्य फसल बजट
- श्रम लागत हाइलाइट
- केवल हिंदी

---

#### Test: finance_hi_10
**Input:** "नाशिक में 2 एकड़ मक्का की खेती की लागत"
**Expected:**
- स्थान विशिष्ट बजट
- सिंचाई लागत
- केवल हिंदी

---

## GENERAL AGENT TESTS (20 total)

### English Tests (10)

#### Test: general_en_1
**Input:** "Hello, how are you?"
**Expected:**
- Friendly greeting
- Offer to help
- English only

---

#### Test: general_en_2
**Input:** "What can you do?"
**Expected:**
- List of services
- Clear capabilities
- English only

---

#### Test: general_en_3
**Input:** "Tell me about farming"
**Expected:**
- General farming info
- Offer specific help
- English only

---

#### Test: general_en_4
**Input:** "What is the weather like?"
**Expected:**
- Weather info or ask location
- Helpful response
- English only

---

#### Test: general_en_5
**Input:** "I need help with my farm"
**Expected:**
- Ask for specifics
- Guiding questions
- English only

---

#### Test: general_en_6
**Input:** "Thank you for your help"
**Expected:**
- Acknowledgment
- Offer more help
- English only

---

#### Test: general_en_7
**Input:** "What is agriculture?"
**Expected:**
- Brief definition
- Practical context
- English only

---

#### Test: general_en_8
**Input:** "How do I start farming?"
**Expected:**
- Basic guidance
- Ask for details
- English only

---

#### Test: general_en_9
**Input:** "What is organic farming?"
**Expected:**
- Explanation
- Benefits
- English only

---

#### Test: general_en_10
**Input:** "Tell me about irrigation"
**Expected:**
- Irrigation methods
- Ask crop type
- English only

---

### Hindi Tests (10)

#### Test: general_hi_1
**Input:** "नमस्ते, आप कैसे हैं?"
**Expected:**
- मित्रवत अभिवादन
- मदद की पेशकश
- केवल हिंदी

---

#### Test: general_hi_2
**Input:** "आप क्या कर सकते हैं?"
**Expected:**
- सेवाओं की सूची
- स्पष्ट क्षमताएं
- केवल हिंदी

---

#### Test: general_hi_3
**Input:** "मुझे खेती के बारे में बताएं"
**Expected:**
- सामान्य खेती जानकारी
- विशिष्ट मदद की पेशकश
- केवल हिंदी

---

#### Test: general_hi_4
**Input:** "मौसम कैसा है?"
**Expected:**
- मौसम जानकारी या स्थान पूछें
- सहायक प्रतिक्रिया
- केवल हिंदी

---

#### Test: general_hi_5
**Input:** "मुझे अपने खेत में मदद चाहिए"
**Expected:**
- विशिष्टताओं के लिए पूछें
- मार्गदर्शक प्रश्न
- केवल हिंदी

---

#### Test: general_hi_6
**Input:** "आपकी मदद के लिए धन्यवाद"
**Expected:**
- स्वीकृति
- अधिक मदद की पेशकश
- केवल हिंदी

---

#### Test: general_hi_7
**Input:** "कृषि क्या है?"
**Expected:**
- संक्षिप्त परिभाषा
- व्यावहारिक संदर्भ
- केवल हिंदी

---

#### Test: general_hi_8
**Input:** "मैं खेती कैसे शुरू करूं?"
**Expected:**
- बुनियादी मार्गदर्शन
- विवरण के लिए पूछें
- केवल हिंदी

---

#### Test: general_hi_9
**Input:** "जैविक खेती क्या है?"
**Expected:**
- व्याख्या
- लाभ
- केवल हिंदी

---

#### Test: general_hi_10
**Input:** "सिंचाई के बारे में बताएं"
**Expected:**
- सिंचाई विधियां
- फसल प्रकार पूछें
- केवल हिंदी

---

## TEST RESULTS TEMPLATE

```
Test ID: _______
Date: _______
Tester: _______
Status: PASS / FAIL / BLOCKED

Input: _______
Expected: _______
Actual: _______

Issues Found:
1. _______
2. _______

Screenshots: _______
Notes: _______
```

---

## SUMMARY TEMPLATE

```
Total Tests: 80
Passed: ___
Failed: ___
Blocked: ___

Pass Rate: ___%

Critical Issues: ___
High Issues: ___
Medium Issues: ___
Low Issues: ___

Language Consistency: ___%
Routing Accuracy: ___%
Response Quality: ___%
```

---

## NEXT STEPS AFTER TESTING

1. Document all failures
2. Categorize issues by severity
3. Create fix tickets
4. Implement fixes
5. Re-test failed scenarios
6. Update documentation
7. Deploy to production

---

**Status:** Ready for Manual Testing
**Date:** February 27, 2026
**Estimated Time:** 4-6 hours for complete testing
