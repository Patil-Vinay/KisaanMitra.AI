# 🔮 Price Forecasting - Quick Reference

## What It Does
Predicts crop prices 7 days ahead using AI + historical market data

## How to Use

### Sample Queries (Hindi)
- गन्ने की कीमत अगले सप्ताह क्या होगी?
- प्याज का भाव आगे बढ़ेगा या घटेगा?
- गेहूं का पूर्वानुमान बताओ

### Sample Queries (English)
- What will be the price of sugarcane next week?
- Price forecast for onion
- Will wheat prices increase?

## What You Get

```
📊 Price Forecast
💰 Current: ₹3,200/quintal
🔮 7-Day: ₹3,350/quintal (+4.7%)
📈 Trend: increasing
📦 Supply: low
📈 Demand: high
✅ Confidence: high
💡 Recommendation: wait
🔍 Key Factors: [3 bullet points]
```

## Technology Stack
- AWS Bedrock Claude 3 Sonnet (AI)
- Agmarknet API (historical data)
- Supply-demand analysis
- Time series forecasting

## Key Features
✅ 7-day price predictions
✅ Supply-demand signals
✅ Confidence levels
✅ Sell/wait/hold recommendations
✅ Explains reasoning
✅ Hindi + English
✅ Profile-aware

## Testing
```bash
# Via WhatsApp
Send: "गन्ने की कीमत अगले सप्ताह क्या होगी?"

# Check logs
aws logs tail /aws/lambda/whatsapp-llama-bot --since 5m --region ap-south-1 | grep FORECAST

# Direct test
python3 scripts/test/test_forecast_engine.py
```

## Files
- `src/lambda/price_forecasting.py` - Core engine
- `src/lambda/agents/market_agent.py` - Integration
- `PRICE_FORECASTING_FEATURE.md` - Full docs

## Status
✅ Deployed (2026-03-04 12:10 IST)
✅ Ready for demo
✅ Fully documented

## Demo Script
1. Show current market price query
2. Then ask: "What will be the price next week?"
3. Highlight: AI analysis, supply-demand, recommendation
4. Emphasize: Helps farmers maximize profits

## Cost
~₹0.25 per forecast (<₹250 per 1000 forecasts)
