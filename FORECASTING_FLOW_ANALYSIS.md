# 🔍 Price Forecasting Flow Analysis - From Logs

## Recent Query Analysis (Last Hour)

### Query 1: "What will be the price of soyabean next week?"
**User**: 919000000002 (Parth)  
**Time**: 2026-03-05 04:30:22 IST  
**Language**: English (auto-detected)

**Flow**:
```
1. WhatsApp Message Received
   └─> Message: "What will be the price of soyabean next week?"

2. Language Detection
   └─> Detected: English

3. AI Routing (Claude Sonnet 4)
   └─> Selected Agent: MARKET

4. Market Agent Processing
   ├─> Extract crop: "soybean"
   └─> State: Maharashtra (default)

5. Forecasting Engine
   ├─> Check DynamoDB for "soybean"
   ├─> Result: NOT FOUND ❌
   └─> Fallback: AI-only forecast

6. AI-Only Forecast Generation (AWS Bedrock Claude)
   ├─> Input: Crop=soybean, State=Maharashtra
   ├─> AI generates estimate based on general knowledge
   └─> Output: ₹45,000 → ₹47,000 (7-day forecast)

7. Response Sent
   └─> WhatsApp API: 200 OK
```

**APIs Called**:
1. ✅ Claude API (Anthropic) - Language detection
2. ✅ Claude API (Anthropic) - Agent routing
3. ✅ Claude API (Anthropic) - Crop extraction
4. ✅ DynamoDB GetItem - Check for forecast (NOT FOUND)
5. ✅ AWS Bedrock Claude - Generate AI-only forecast
6. ✅ WhatsApp API - Send response

**Why AI-Only?**:
- Soybean is NOT in DynamoDB forecasts
- Only 5 crops have pre-computed forecasts: onion, rice, sugarcane, tomato, wheat
- System falls back to AI-only estimation

---

### Query 2: "Week forecast for tomato"
**User**: 919000000001 (Vinay)  
**Time**: 2026-03-05 04:30:30 IST  
**Language**: English (auto-detected)

**Flow**:
```
1. WhatsApp Message Received
   └─> Message: "Week forecast for tomato"

2. Language Detection
   └─> Detected: English

3. AI Routing (Claude Sonnet 4)
   └─> Selected Agent: GENERAL

4. General Agent Processing
   ├─> Profile loaded: Vinay Patil from Nandani, Sangli
   ├─> Detected: Price forecast query
   └─> Route to: Price handler

5. Price Handler Attempt
   ├─> Extract crop: "tomato"
   └─> ERROR: ModuleNotFoundError ❌

6. Error Response
   └─> Generic error message sent
```

**APIs Called**:
1. ✅ Claude API (Anthropic) - Language detection
2. ✅ Claude API (Anthropic) - Agent routing
3. ✅ Claude API (Anthropic) - Query classification
4. ✅ Claude API (Anthropic) - Crop extraction
5. ❌ Price forecasting - FAILED (module error)
6. ✅ WhatsApp API - Send error response

**Error Found**:
```python
ModuleNotFoundError: No module named 'lambda_whatsapp_kisaanmitra'
File: /var/task/agents/general_agent.py, line 186
Code: from lambda_whatsapp_kisaanmitra import handle_price_forecast_query
```

**Issue**: General agent trying to import old module that doesn't exist

---

## System Architecture (From Logs)

### 1. Entry Point
```
WhatsApp Webhook
    ↓
Lambda: whatsapp-llama-bot
    ↓
Handler: lambda_handler_v2.py
```

### 2. Language Detection
```
Input: User message
    ↓
Claude API (Anthropic)
    ↓
Output: Language (english/hindi)
```

### 3. Agent Routing
```
Input: User message + language
    ↓
Claude API (Anthropic) - Routing decision
    ↓
Output: Agent selection (MARKET/GENERAL/CROP/FINANCE/WEATHER)
```

### 4. Market Agent (Price Forecasting)
```
Input: User query
    ↓
Step 1: Load user profile (DynamoDB)
    ├─> Village, District
    └─> Map district to state
    ↓
Step 2: Extract crop name (Claude API)
    ↓
Step 3: Check for forecast keywords
    ├─> forecast, prediction, future, next week
    ├─> पूर्वानुमान, भविष्य, अगले सप्ताह
    └─> If found: Route to forecasting
    ↓
Step 4: Forecasting Engine
    ├─> Priority 1: Check DynamoDB
    │   ├─> Table: kisaanmitra-price-forecasts
    │   ├─> Key: commodity (lowercase)
    │   └─> If found: Return Statistical forecast ✅
    │
    ├─> Priority 2: SageMaker (if available)
    │   └─> Status: BLOCKED (quota = 0) ❌
    │
    └─> Priority 3: AI-Only Fallback
        ├─> Call AWS Bedrock Claude
        ├─> Generate estimate without data
        └─> Return AI forecast ⚠️
```

### 5. Response Delivery
```
Forecast Data
    ↓
Format response (english/hindi)
    ↓
Save conversation (DynamoDB)
    ↓
Send to WhatsApp API
    ↓
Send interactive menu
```

---

## APIs Used (In Order)

### For Soybean Query (Working)
1. **Claude API** (Anthropic) - Language detection
   - Model: claude-sonnet-4-6
   - Input: User message
   - Output: Language code

2. **Claude API** (Anthropic) - Agent routing
   - Model: claude-sonnet-4-6
   - Input: Message + context
   - Output: MARKET

3. **DynamoDB GetItem** - User profile
   - Table: kisaanmitra-users
   - Key: phone_number
   - Output: User profile data

4. **Claude API** (Anthropic) - Crop extraction
   - Model: claude-sonnet-4-6
   - Input: User message
   - Output: "soybean"

5. **DynamoDB GetItem** - Check forecast
   - Table: kisaanmitra-price-forecasts
   - Key: commodity="soybean"
   - Output: NOT FOUND

6. **AWS Bedrock Claude** - AI-only forecast
   - Model: claude-3-sonnet
   - Input: Crop + state + constraints
   - Output: Price forecast (₹45,000 → ₹47,000)

7. **DynamoDB PutItem** - Save conversation
   - Table: kisaanmitra-conversations
   - Data: User query + response

8. **WhatsApp API** - Send message
   - Endpoint: Meta WhatsApp Business API
   - Response: 200 OK

### For Tomato Query (Failed)
1-4: Same as above
5. **General Agent** - Price handler
   - ERROR: Module not found
   - Missing: lambda_whatsapp_kisaanmitra module

---

## DynamoDB Tables Used

### 1. kisaanmitra-price-forecasts
**Purpose**: Store pre-computed forecasts

**Structure**:
```json
{
  "commodity": "tomato",  // Primary key
  "model": "Statistical Trend Analysis",
  "forecasts": [
    {
      "date": "2026-03-06",
      "price": 2160.87,
      "lower": 866.76,
      "upper": 3454.98
    }
    // ... 29 more days
  ],
  "last_updated": "2026-03-05T02:22:23"
}
```

**Current Data**:
- ✅ onion (30 days)
- ✅ rice (30 days)
- ✅ sugarcane (30 days)
- ✅ tomato (30 days)
- ✅ wheat (30 days)
- ❌ soybean (not available)

### 2. kisaanmitra-users
**Purpose**: Store user profiles

**Structure**:
```json
{
  "phone_number": "919000000002",
  "name": "Parth Nikam",
  "village": "Sangli",
  "district": "Sangli",
  "crops": ["Sugarcane"]
}
```

### 3. kisaanmitra-conversations
**Purpose**: Store conversation history

**Structure**:
```json
{
  "user_id": "919000000002",
  "timestamp": "2026-03-05T04:30:26",
  "agent": "market",
  "query": "What will be the price of soyabean next week?",
  "response": "..."
}
```

---

## Issue Found: General Agent Error

### Problem
```python
File: /var/task/agents/general_agent.py, line 186
Error: ModuleNotFoundError: No module named 'lambda_whatsapp_kisaanmitra'
Code: from lambda_whatsapp_kisaanmitra import handle_price_forecast_query
```

### Impact
- Tomato forecast query failed
- User received generic error message
- Should have checked DynamoDB and returned Statistical forecast

### Root Cause
General agent has old import statement for deprecated module

### Solution Needed
Update general_agent.py to use market_agent directly:
```python
# OLD (broken)
from lambda_whatsapp_kisaanmitra import handle_price_forecast_query

# NEW (should be)
from agents.market_agent import MarketAgent
result = MarketAgent.handle(user_message, language, user_id)
```

---

## Current System Status

### Working ✅
1. **Soybean query** - AI-only forecast
   - No DynamoDB data
   - Falls back to AI estimation
   - Response: ₹45,000 → ₹47,000

2. **Market agent** - Direct routing
   - Works when routed directly to MARKET agent
   - Checks DynamoDB first
   - Falls back to AI if not found

### Broken ❌
1. **Tomato query via General agent**
   - General agent has import error
   - Cannot route to price forecasting
   - Returns generic error

2. **SageMaker forecasts**
   - Model trained but quota blocked
   - Cannot generate forecasts
   - Waiting for AWS approval

### Available in DynamoDB ✅
- Onion: Statistical Trend Analysis
- Rice: Statistical Trend Analysis
- Sugarcane: Statistical Trend Analysis
- Tomato: Statistical Trend Analysis
- Wheat: Statistical Trend Analysis

### Not Available ❌
- Soybean: No forecast data
- Cotton: No forecast data
- Other crops: No forecast data

---

## Recommendations

### Immediate Fix
1. **Fix General Agent Import**
   - Update general_agent.py line 186
   - Use market_agent directly
   - Deploy updated Lambda

2. **Add More Crops to DynamoDB**
   - Generate forecasts for soybean
   - Add cotton, maize, etc.
   - Run statistical forecasting script

### After SageMaker Approval
1. **Run Batch Transform**
   - Generate SageMaker forecasts
   - Replace Statistical forecasts
   - Update DynamoDB

2. **Compare Accuracy**
   - Statistical vs SageMaker
   - Decide which to use long-term

---

## Summary

**How It Works**:
1. User sends WhatsApp message
2. Claude API detects language and routes to agent
3. Market agent extracts crop name
4. System checks DynamoDB for pre-computed forecast
5. If found: Return Statistical forecast (5 crops available)
6. If not found: Generate AI-only estimate (like soybean)
7. Response sent via WhatsApp API

**APIs Called** (per query):
- Claude API: 3-4 calls (routing, extraction)
- DynamoDB: 2-3 calls (profile, forecast, conversation)
- AWS Bedrock: 0-1 calls (only if AI-only fallback)
- WhatsApp API: 2 calls (message + menu)

**Issue Found**:
- General agent has broken import
- Tomato queries via General agent fail
- Direct Market agent queries work fine

**Fix Needed**:
- Update general_agent.py import statement
- Deploy to Lambda
