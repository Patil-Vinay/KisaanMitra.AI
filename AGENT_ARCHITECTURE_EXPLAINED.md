# 🤖 KisaanMitra Agent Architecture

## Overview

Your WhatsApp bot uses an **AI-powered multi-agent system** where messages are intelligently routed to specialized agents. No hardcoded keywords - everything uses Claude AI for smart routing.

---

## 🎯 How Message Routing Works

### Step 1: Message Arrives
When a farmer sends a WhatsApp message, it goes through:

```
WhatsApp → Webhook → Lambda Handler → AI Router → Specialized Agent
```

### Step 2: AI-Based Routing (`route_message` function)
- **Location**: Line 374 in `lambda_whatsapp_kisaanmitra.py`
- **How it works**: Claude AI analyzes the message and picks the right agent
- **No keywords**: Instead of checking for words like "price" or "disease", AI understands intent

```python
# AI analyzes: "मेरे टमाटर में पत्ते पीले हो रहे हैं"
# AI decides: "crop" agent (understands it's about crop health)
```

**Available Agents**:
- `greeting` - Simple greetings (hi, hello, namaste)
- `crop` - Crop health, diseases, pests
- `market` - Market prices, mandi rates
- `finance` - Budget, loans, schemes
- `general` - Everything else

---

## 🌿 Agent 1: Crop Agent

**Function**: `handle_crop_query` (Line 415)

### What It Does
Helps farmers with crop diseases, pests, and treatments.

### How It Works

#### Priority 1: Hyperlocal Data (Community Intelligence)
```
1. Check if farmer has profile (village + crops)
2. Query hyperlocal disease database
3. Find disease reports from same village/district
4. Return community-verified treatments
```

**Example**:
```
Farmer: "मेरे टमाटर में पत्ते पीले हो रहे हैं"
System checks: Village = Kolhapur, Crop = Tomato
Finds: 3 farmers reported "Leaf Curl" in last 30 days
Returns: Treatments that worked for those farmers
```

#### Priority 2: Weather Context
- Fetches 3-day weather forecast for farmer's location
- Adds temperature, rain predictions
- Provides weather-based farming advice

#### Priority 3: AI Fallback
If no hyperlocal data available:
- Uses Claude AI with farmer's profile context
- Provides general crop advice
- Responds in farmer's language (Hindi/English)

### Key Features
- ✅ Uses real disease reports from farmer's village
- ✅ Weather-aware recommendations
- ✅ Bilingual (Hindi/English)
- ✅ Profile-aware (knows farmer's crops and location)

---

## 📊 Agent 2: Market Agent

**Function**: `handle_market_query` (Line 619)

### What It Does
Provides real-time market prices and trends.

### How It Works

#### Step 1: Extract Crop Name (AI)
```python
# User: "टमाटर का भाव क्या है?"
# AI extracts: "tomato"
```

#### Step 2: Extract Location (AI or Profile)
```python
# Option 1: From user profile (village → state)
# Option 2: AI extracts from message
# Example: "कोल्हापुर में प्याज का रेट?" → "Maharashtra"
```

#### Step 3: Fetch Real Market Data
- Queries AgMarkNet API (government mandi data)
- Gets prices from multiple mandis in that state
- Calculates average, min, max prices
- Analyzes price trend (rising/falling/stable)

#### Step 4: Format Response
```
🏪 टमाटर - महाराष्ट्र मंडी भाव

📊 औसत भाव: ₹1,450/quintal
📈 रुझान: बढ़ रहा है (+12%)

💰 मंडी भाव:
• कोल्हापुर: ₹1,500
• पुणे: ₹1,420
• नासिक: ₹1,380
```

### Key Features
- ✅ Real government mandi data (AgMarkNet API)
- ✅ AI extracts crop and location (no keywords)
- ✅ Price trend analysis
- ✅ Multiple mandi comparison
- ✅ Bilingual responses

---

## 💰 Agent 3: Finance Agent

**Function**: `handle_finance_query` (Line 1706)

### What It Does
Handles budget planning, loans, and government schemes.

### How It Works

#### Step 1: AI Sub-Routing
Finance agent has its own AI router that categorizes queries:

```python
# AI analyzes message and picks sub-type:
- "schemes" → Government schemes, subsidies
- "budget" → Budget planning, cost calculation
- "loan" → Loan applications, credit
- "general" → Other finance questions
```

#### Step 2: Handle Based on Type

**A. Government Schemes**
```
User: "टमाटर के लिए कौन सी सरकारी योजना है?"

Response includes:
• PM-KISAN (₹6,000/year)
• Kisan Credit Card (₹3 lakh at 7%)
• Crop Insurance (PMFBY)
• Soil Health Card
• Crop-specific schemes
```

**B. Budget Planning**
```
User: "2 एकड़ में टमाटर लगाने का खर्च?"

System:
1. Extracts: Crop=Tomato, Land=2 acres, Location=from profile
2. Uses AI to generate detailed budget
3. Includes: Seeds, fertilizer, labor, irrigation, pesticides
4. Calculates total cost
5. Suggests government schemes
6. Calculates loan eligibility
```

**C. Loan Queries**
```
User: "मुझे लोन चाहिए"

Response:
• Kisan Credit Card details
• Eligibility criteria
• Interest rates
• Application process
• Required documents
```

### Key Features
- ✅ AI-based sub-routing (no keywords)
- ✅ Detailed budget calculations
- ✅ Government scheme recommendations
- ✅ Loan eligibility calculation
- ✅ Profile-aware (uses farmer's land, crops, location)
- ✅ Bilingual responses

---

## 🔄 Complete Flow Example

### Example 1: Crop Disease Query

```
1. Farmer sends: "मेरे टमाटर में पत्ते पीले हो रहे हैं"

2. AI Router analyzes → Routes to "crop" agent

3. Crop Agent:
   - Checks profile: Village=Kolhapur, Crops=Tomato
   - Queries hyperlocal DB: Finds 3 "Leaf Curl" reports
   - Fetches weather: 28°C, no rain expected
   - Returns: Community treatments + weather advice

4. Response sent in Hindi (farmer's language)
```

### Example 2: Market Price Query

```
1. Farmer sends: "onion price in pune?"

2. AI Router analyzes → Routes to "market" agent

3. Market Agent:
   - AI extracts: Crop="onion", State="Maharashtra"
   - Calls AgMarkNet API
   - Gets prices from 10 mandis
   - Calculates average: ₹2,150/quintal
   - Trend: Rising (+8%)

4. Response sent in English (farmer's language)
```

### Example 3: Budget Planning Query

```
1. Farmer sends: "मुझे 2 एकड़ में टमाटर लगाना है बजट बताओ"

2. AI Router → "finance" agent

3. Finance Agent:
   - AI sub-router → "budget" type
   - AI extracts: Crop=Tomato, Land=2 acres
   - Gets location from profile: Kolhapur
   - Generates detailed budget with AI
   - Calculates: ₹1,20,000 total cost
   - Suggests: PM-KISAN, KCC loan
   - Loan eligibility: ₹90,000

4. Response with full budget breakdown in Hindi
```

---

## 🎨 Key Design Principles

### 1. AI-First Routing
- No hardcoded keywords
- Claude AI understands intent
- Works in any language
- Handles typos and variations

### 2. Context-Aware
- Uses farmer profile (village, crops, land)
- Remembers conversation history
- Adds weather context
- Location-aware responses

### 3. Data-Driven
- Hyperlocal disease reports (community data)
- Real government mandi prices (AgMarkNet)
- Weather forecasts (OpenWeather)
- Government schemes database

### 4. Bilingual
- Detects language automatically
- Responds in same language
- Supports Hindi and English
- No language mixing

### 5. Fallback Strategy
```
Priority 1: Real data (hyperlocal, market, weather)
Priority 2: AI with context (profile, history)
Priority 3: General AI response
```

---

## 📊 Agent Comparison

| Feature | Crop Agent | Market Agent | Finance Agent |
|---------|-----------|--------------|---------------|
| **Primary Data** | Hyperlocal disease reports | AgMarkNet API | AI + Schemes DB |
| **AI Usage** | Fallback only | Extract crop/state | Primary + Sub-routing |
| **Context Used** | Village, crops, weather | State, profile | Land, crops, location |
| **Response Time** | Fast (DB query) | Medium (API call) | Slow (AI generation) |
| **Accuracy** | High (community data) | High (govt data) | Medium (AI estimates) |

---

## 🔧 Technical Details

### Language Detection
```python
# Automatic language detection from message
language = get_user_language(user_id, message_text)
# Stores preference in DynamoDB
```

### Conversation History
```python
# Last 3-10 messages stored per user
history = get_conversation_history(user_id, limit=3)
# Used for context in AI responses
```

### Profile Integration
```python
# Farmer profile from onboarding
profile = onboarding_manager.get_user_profile(user_id)
# Contains: name, village, district, crops, land_acres
```

### Weather Integration
```python
# 3-day forecast for farmer's location
forecast = get_weather_forecast(location)
analysis = analyze_weather_for_farming(forecast)
# Provides: temp, rain prediction, farming advice
```

---

## 🚀 Why This Architecture Works

### 1. Scalable
- Each agent is independent
- Easy to add new agents
- No keyword maintenance

### 2. Accurate
- Uses real data sources
- AI understands intent
- Context-aware responses

### 3. Fast
- Hyperlocal data cached
- Market data cached (5 min)
- AI routing is quick

### 4. User-Friendly
- Natural language queries
- No specific format needed
- Works in farmer's language

### 5. Maintainable
- No hardcoded keywords
- AI handles variations
- Easy to update agents

---

## 📝 Summary

Your WhatsApp bot uses a **3-agent system**:

1. **Crop Agent** → Disease detection + treatments (hyperlocal data + AI)
2. **Market Agent** → Real mandi prices (AgMarkNet API + AI extraction)
3. **Finance Agent** → Budget + loans + schemes (AI generation + schemes DB)

All routing is **AI-powered** (no keywords), responses are **bilingual**, and the system uses **real data** wherever possible with AI as intelligent fallback.

The architecture is designed for **Indian farmers** with focus on:
- Local language support
- Community-driven data
- Government data integration
- Context-aware responses
- Simple, natural queries
