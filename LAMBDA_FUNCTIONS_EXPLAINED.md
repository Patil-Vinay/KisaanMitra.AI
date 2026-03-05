# 🔧 KisaanMitra Lambda Functions

## Overview

You have **3 active Lambda functions** running your system:

---

## 1️⃣ whatsapp-llama-bot (Main Bot)

### Basic Info
- **Function Name**: `whatsapp-llama-bot`
- **Runtime**: Python 3.14
- **Handler**: `lambda_handler_v2.lambda_handler`
- **Size**: 610 KB
- **Code File**: `src/lambda/lambda_whatsapp_kisaanmitra.py`

### What It Does
This is your **MAIN WhatsApp bot** - handles ALL farmer interactions.

### Responsibilities

#### 1. Message Reception
- Receives WhatsApp webhook events
- Handles text messages, images, buttons, lists
- Manages webhook verification

#### 2. AI-Powered Routing
- Uses Claude AI to route messages to agents
- No hardcoded keywords
- Understands intent in Hindi/English

#### 3. All 3 Agents (Built-In)
✅ **Crop Agent** (Line 415)
- Hyperlocal disease detection
- Weather-aware crop advice
- Community treatments

✅ **Market Agent** (Line 619)
- Real mandi prices (AgMarkNet API)
- Price trend analysis
- Multi-mandi comparison

✅ **Finance Agent** (Line 1706)
- Budget planning
- Government schemes
- Loan eligibility

#### 4. Additional Features
- Language detection (Hindi/English)
- Conversation history
- User profile management
- Onboarding flow
- Interactive menus (buttons/lists)
- Image analysis (crop disease photos)
- Price forecasts (queries DynamoDB)
- Disease alerts
- Navigation controls

### Key Integrations
- **AWS Bedrock** → Claude AI for routing and responses
- **DynamoDB** → User profiles, conversation history, forecasts
- **S3** → Image storage
- **AgMarkNet API** → Real market prices
- **OpenWeather API** → Weather forecasts
- **WhatsApp Business API** → Message sending

### Trigger
- **API Gateway** → Webhook from WhatsApp
- Runs on every message from farmers

---

## 2️⃣ kisaanmitra-crop-agent (Standalone Crop Agent)

### Basic Info
- **Function Name**: `kisaanmitra-crop-agent`
- **Runtime**: Python 3.11
- **Handler**: `lambda_crop_agent.lambda_handler`
- **Size**: 16.3 MB (largest)
- **Code File**: `src/lambda/lambda_crop_agent.py`

### What It Does
This is a **STANDALONE crop agent** - separate from the main bot.

### Purpose
- Can be invoked independently (not through WhatsApp)
- Useful for:
  - Direct API calls
  - Testing crop advice
  - Integration with other systems
  - Batch processing

### Functionality
Similar to the Crop Agent in main bot:
- Crop disease detection
- Treatment recommendations
- Image analysis
- AI-powered advice

### Trigger
- **Manual invocation** or API call
- NOT connected to WhatsApp webhook

### Status
⚠️ **Note**: This is a duplicate of the crop functionality already in `whatsapp-llama-bot`. You might not need this if all crop queries come through WhatsApp.

---

## 3️⃣ kisaanmitra-sagemaker-forecaster (Price Forecasting)

### Basic Info
- **Function Name**: `kisaanmitra-sagemaker-forecaster`
- **Runtime**: Python 3.11
- **Handler**: `lambda_sagemaker_forecaster.lambda_handler`
- **Size**: 1.2 MB
- **Code File**: `src/lambda/lambda_sagemaker_forecaster.py`

### What It Does
Trains **SageMaker AutoML models** for price forecasting.

### Responsibilities

#### 1. Data Preparation
- Fetches 5 years of historical price data from S3
- Optionally fetches latest 7 days from AgMarkNet API
- Formats data for SageMaker (timestamp + price)

#### 2. Model Training
- Creates SageMaker AutoML job
- Tests 6 algorithms: ARIMA, ETS, Prophet, NPTS, DeepAR+, CNN-QR
- Picks best performing model
- Training takes ~90 minutes

#### 3. Current Limitation
⚠️ **CRITICAL**: Currently only trains models, does NOT generate forecasts or store in DynamoDB.

### Trigger
- **EventBridge Rule**: `kisaanmitra-weekly-forecast-training`
- Schedule: Every Sunday at 2 AM IST
- Can also be invoked manually

### Data Sources
- **S3 Bucket**: `s3://kisaanmitra-ml-data/historical-prices/`
  - Onion.csv (5 years)
  - Rice.csv (5 years)
  - Sugarcane.csv (5 years)
  - Tomato.csv (5 years)
  - Wheat.csv (5 years)
- **AgMarkNet API**: Latest 7 days (when API key configured)

### Output
- Trained model in SageMaker
- ⚠️ **Missing**: Forecast generation and DynamoDB storage

---

## 🔄 How They Work Together

### Farmer Asks About Crop Disease
```
1. WhatsApp message → whatsapp-llama-bot
2. AI Router → Crop Agent (built-in)
3. Queries hyperlocal DB + weather
4. Responds via WhatsApp
```

### Farmer Asks About Market Price
```
1. WhatsApp message → whatsapp-llama-bot
2. AI Router → Market Agent (built-in)
3. Calls AgMarkNet API
4. Responds via WhatsApp
```

### Farmer Asks About Budget
```
1. WhatsApp message → whatsapp-llama-bot
2. AI Router → Finance Agent (built-in)
3. AI generates budget
4. Responds via WhatsApp
```

### Farmer Asks About Price Forecast
```
1. WhatsApp message → whatsapp-llama-bot
2. Queries DynamoDB (kisaanmitra-price-forecasts)
3. ⚠️ Currently returns empty (no forecasts generated)
4. Responds via WhatsApp
```

### Weekly Price Forecast Training
```
1. EventBridge (Sunday 2 AM) → kisaanmitra-sagemaker-forecaster
2. Fetches data from S3 + AgMarkNet
3. Starts SageMaker AutoML training
4. ⚠️ Training completes but forecasts NOT generated
5. ⚠️ DynamoDB NOT updated
```

---

## 📊 Lambda Function Comparison

| Feature | whatsapp-llama-bot | kisaanmitra-crop-agent | kisaanmitra-sagemaker-forecaster |
|---------|-------------------|------------------------|----------------------------------|
| **Purpose** | Main WhatsApp bot | Standalone crop agent | Price forecasting training |
| **Trigger** | WhatsApp webhook | Manual/API | EventBridge (weekly) |
| **Agents** | All 3 (Crop, Market, Finance) | Crop only | None (training only) |
| **User Facing** | ✅ Yes | ❌ No | ❌ No |
| **Runtime** | Python 3.14 | Python 3.11 | Python 3.11 |
| **Size** | 610 KB | 16.3 MB | 1.2 MB |
| **Status** | ✅ Active | ⚠️ Duplicate | ⚠️ Incomplete |

---

## 🎯 Key Points

### 1. Main Bot Handles Everything
The `whatsapp-llama-bot` Lambda is your **primary function** that:
- Receives all WhatsApp messages
- Routes to appropriate agent (Crop/Market/Finance)
- Handles all farmer interactions
- Manages conversation flow

### 2. All Agents Are Built-In
You don't have separate Lambda functions for each agent. All 3 agents (Crop, Market, Finance) are **built into the main bot**:
- Crop Agent: Lines 415-550
- Market Agent: Lines 619-685
- Finance Agent: Lines 1706-1850

### 3. Standalone Crop Agent
The `kisaanmitra-crop-agent` is a **duplicate** of the crop functionality. It's not used by WhatsApp bot. You can:
- Keep it for API integrations
- Delete it to save costs (if not needed)

### 4. Forecaster Needs Work
The `kisaanmitra-sagemaker-forecaster` trains models but doesn't generate forecasts. This is why farmers get empty responses when asking about price predictions.

---

## 🔧 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         FARMER                               │
│                      (WhatsApp User)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Sends message
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   WhatsApp Business API                      │
│                    (Meta/Facebook)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Webhook POST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│                   (AWS Endpoint)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Triggers
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Lambda: whatsapp-llama-bot                      │
│              (Main Bot - Python 3.14)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         AI Router (Claude via Bedrock)             │    │
│  │    Analyzes message → Picks agent                  │    │
│  └──────────┬──────────────┬──────────────┬───────────┘    │
│             │              │              │                 │
│    ┌────────▼─────┐  ┌────▼─────┐  ┌────▼─────┐          │
│    │ Crop Agent   │  │  Market  │  │ Finance  │          │
│    │ (Line 415)   │  │  Agent   │  │  Agent   │          │
│    │              │  │(Line 619)│  │(Line 1706)│          │
│    │• Hyperlocal  │  │• AgMarkNet│ │• Budget  │          │
│    │• Weather     │  │• Prices   │ │• Schemes │          │
│    │• AI advice   │  │• Trends   │ │• Loans   │          │
│    └──────────────┘  └───────────┘  └───────────┘          │
│                                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Sends response
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   WhatsApp Business API                      │
│                  (Delivers to Farmer)                        │
└─────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│              Lambda: kisaanmitra-crop-agent                  │
│              (Standalone - Python 3.11)                      │
│              NOT connected to WhatsApp                       │
│              Can be invoked via API                          │
└─────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│                     EventBridge Rule                         │
│           (Every Sunday 2 AM IST)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Triggers weekly
                         ▼
┌─────────────────────────────────────────────────────────────┐
│       Lambda: kisaanmitra-sagemaker-forecaster               │
│              (Training - Python 3.11)                        │
│                                                              │
│  1. Fetch data from S3 (5 years)                            │
│  2. Fetch latest from AgMarkNet API                         │
│  3. Start SageMaker AutoML training                         │
│  4. ⚠️ Training completes (90 min)                          │
│  5. ⚠️ Forecasts NOT generated                              │
│  6. ⚠️ DynamoDB NOT updated                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Recommendations

### 1. Keep whatsapp-llama-bot
This is your core function - handles all farmer interactions.

### 2. Consider Removing kisaanmitra-crop-agent
It's a duplicate. Unless you need standalone crop API, you can delete it to:
- Save Lambda costs
- Reduce maintenance
- Avoid confusion

### 3. Fix kisaanmitra-sagemaker-forecaster
Add forecast generation logic so farmers can get price predictions.

### 4. Monitor Costs
- Main bot: Runs on every message (high frequency)
- Forecaster: Runs weekly (low frequency but expensive SageMaker)
- Crop agent: Rarely used (if at all)

---

## 📝 Summary

**One Lambda does all the work**: `whatsapp-llama-bot`
- Handles WhatsApp messages
- Routes to 3 built-in agents (Crop, Market, Finance)
- Manages entire conversation flow

**One Lambda trains models**: `kisaanmitra-sagemaker-forecaster`
- Runs weekly
- Trains price forecasting models
- ⚠️ Needs forecast generation added

**One Lambda is standalone**: `kisaanmitra-crop-agent`
- Not used by WhatsApp bot
- Can be deleted if not needed
