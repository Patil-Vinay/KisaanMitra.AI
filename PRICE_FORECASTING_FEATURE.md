# 🔮 AI-Powered Price Forecasting System

## Overview
Advanced price forecasting system using AWS Bedrock AI, Agmarknet historical data, and supply-demand analysis to predict crop prices 7 days ahead.

## Features

### 1. Historical Data Collection
- Fetches 30+ days of price data from Agmarknet API
- Collects arrival quantities (supply data)
- Tracks prices across multiple mandis
- Builds comprehensive time series dataset

### 2. Supply-Demand Signal Analysis
- **Supply Signals**: Analyzes arrival quantities
  - High supply: Arrivals 20% above average
  - Low supply: Arrivals 20% below average
  - Normal supply: Within ±20% range

- **Demand Signals**: Derived from price movements + supply
  - High demand: Low supply + rising prices
  - Low demand: High supply + falling prices
  - Stable demand: Balanced supply-price relationship

- **Price Trends**: 
  - Increasing: >5% price rise
  - Decreasing: >5% price drop
  - Stable: Within ±5% range

### 3. AI-Powered Forecasting
- Uses AWS Bedrock Claude 3 Sonnet
- Analyzes historical patterns
- Considers supply/demand signals
- Generates 7-day price forecast
- Provides confidence level (high/medium/low)
- Explains key factors affecting prices
- Recommends action (sell now/wait/hold)

### 4. Intelligent Response
- Formatted in user's language (Hindi/English)
- Shows current vs forecasted price
- Displays trend indicators (📈📉➡️)
- Lists key market factors
- Provides actionable recommendations

## Architecture

```
User Query → Market Agent → Forecasting Engine
                                    ↓
                    1. Fetch Historical Data (Agmarknet API)
                                    ↓
                    2. Analyze Supply/Demand Signals
                                    ↓
                    3. AI Forecast (AWS Bedrock Claude)
                                    ↓
                    4. Format Response
                                    ↓
                            User receives forecast
```

## Sample Queries

### Hindi
- "गन्ने की कीमत अगले सप्ताह क्या होगी?"
- "प्याज का भाव आगे बढ़ेगा या घटेगा?"
- "गेहूं का पूर्वानुमान बताओ"

### English
- "What will be the price of sugarcane next week?"
- "Price forecast for onion"
- "Will wheat prices increase?"

## Sample Response

```
📊 *मूल्य पूर्वानुमान - Sugarcane*

💰 वर्तमान मूल्य: ₹3200/क्विंटल
🔮 7 दिन का पूर्वानुमान: ₹3350/क्विंटल
   (+₹150, +4.7%)

📈 रुझान: increasing
📦 आपूर्ति: low
📈 मांग: high
✅ विश्वास: high

💡 *सिफारिश*: wait

🔍 *मुख्य कारक*:
• कम आपूर्ति के कारण मांग बढ़ रही है
• मौसमी कारकों से उत्पादन प्रभावित
• चीनी मिलों की खरीद सक्रिय

📅 45 बाजार डेटा बिंदुओं के आधार पर
```

## Technical Implementation

### Files Created
1. `src/lambda/price_forecasting.py` - Core forecasting engine
2. `scripts/test/test_forecast_engine.py` - Direct testing
3. `scripts/test/test_price_forecasting.sh` - WhatsApp testing

### Files Modified
1. `src/lambda/agents/market_agent.py` - Integrated forecasting

### AWS Services Used
- **AWS Bedrock**: Claude 3 Sonnet for AI analysis
- **Agmarknet API**: Historical price data
- **Lambda**: Serverless execution

## How It Works

### Step 1: Query Detection
Market agent detects forecast keywords:
- forecast, prediction, future, next week
- पूर्वानुमान, भविष्य, अगले सप्ताह

### Step 2: Data Collection
```python
price_series = fetch_historical_prices(crop, state, days=30)
# Returns: [{date, price, arrival, market, district}, ...]
```

### Step 3: Signal Analysis
```python
signals = analyze_supply_demand_signals(price_series)
# Returns: {
#   current_avg_price, recent_avg_price,
#   price_change_pct, trend, supply_signal, demand_signal
# }
```

### Step 4: AI Forecast
```python
ai_forecast = generate_ai_forecast(crop, price_series, signals, language)
# Uses Bedrock Claude to analyze patterns
# Returns: {
#   forecast_7d, confidence, factors, recommendation, reasoning
# }
```

### Step 5: Response Formatting
```python
message = format_forecast_response(complete_forecast, language)
# Returns formatted WhatsApp message
```

## Testing

### Direct Engine Test
```bash
cd /path/to/project
python3 scripts/test/test_forecast_engine.py
```

### WhatsApp Integration Test
```bash
# Send test message
echo "गन्ने की कीमत अगले सप्ताह क्या होगी?" | # Send via WhatsApp

# Check logs
aws logs tail /aws/lambda/whatsapp-llama-bot --since 5m --region ap-south-1 | grep FORECAST
```

## Deployment

```bash
cd src/lambda
./deploy_v2.sh
```

The forecasting module is automatically included in the Lambda deployment.

## Benefits

1. **Data-Driven Decisions**: Farmers can plan when to sell
2. **Market Intelligence**: Understand supply-demand dynamics
3. **Risk Mitigation**: Avoid selling during price drops
4. **Profit Optimization**: Sell when prices are forecasted to peak
5. **AWS AI Showcase**: Demonstrates advanced AI/ML capabilities

## Future Enhancements

1. **Multi-week forecasts**: 14-day, 30-day predictions
2. **Seasonal patterns**: Incorporate festival/harvest cycles
3. **Weather integration**: Factor in weather impact on prices
4. **Cross-commodity analysis**: Related crop price movements
5. **Accuracy tracking**: Monitor and improve forecast accuracy

## Cost Considerations

- Agmarknet API: Free (government data)
- AWS Bedrock: ~$0.003 per forecast (Claude 3 Sonnet)
- Lambda execution: Minimal (covered by free tier)

**Estimated cost**: <$1 per 1000 forecasts

## Notes

- Requires Agmarknet API key in environment
- Minimum 7 data points needed for forecast
- Confidence decreases with data volatility
- Forecasts are probabilistic, not guaranteed
- Always labeled with confidence level

---

**Status**: ✅ Implemented and Ready for Testing
**AWS Services**: Bedrock, Lambda
**Data Source**: Agmarknet API
**Languages**: Hindi, English
