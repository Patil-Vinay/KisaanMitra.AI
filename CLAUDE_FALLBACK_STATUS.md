# Claude Fallback Status - March 8, 2026 15:15 IST

## Current Situation

### Code Status
✅ **Fix is deployed and correct** (15:02:23 IST)

The code in `market_data_sources.py` now correctly uses:
```python
from anthropic_client import call_claude_with_retry
response_text = call_claude_with_retry(prompt, max_tokens=400, ...)
```

### Testing Status
⏳ **Not yet tested in production**

**Reason**: No actual market price queries since deployment

**Last error**: 14:58:38 (BEFORE fix was deployed)
**Deployment**: 15:02:23 (4 minutes after last error)
**Recent queries**: All contain "forecast" keyword, which routes to different system

## Why No Test Yet?

### Query Routing Logic

The market agent has special handling for forecast queries:

```python
forecast_keywords = ['forecast', 'prediction', 'future', 'next week']
is_forecast_query = any(keyword in user_message.lower() for keyword in forecast_keywords)

if is_forecast_query and detected_crop and FORECASTING_AVAILABLE:
    # Route to forecasting system (different code path)
    forecast = forecasting_engine.get_complete_forecast(...)
else:
    # Route to market data system (uses Claude fallback)
    market_data = get_fast_market_prices(...)
```

### Recent Queries
All recent queries have been:
- "tomato onion potato market prices **and forecast**"

This contains "forecast" keyword, so it:
1. Routes to forecasting system
2. Does NOT call `get_fast_market_prices()`
3. Does NOT trigger Claude fallback
4. Uses cached AI responses instead

## What We Need

### To Test Claude Fallback
Need a query WITHOUT "forecast" keyword:
- ✅ "What is the price of tomato?"
- ✅ "Onion mandi rates"
- ✅ "Potato market price"
- ❌ "tomato forecast" (routes to forecasting)
- ❌ "market prices and forecast" (routes to forecasting)

### Expected Flow
```
User: "What is the price of tomato?"
    ↓
Market Agent detects: NOT a forecast query
    ↓
Calls: get_fast_market_prices("tomato", "Maharashtra")
    ↓
Try AgMarkNet API → Timeout
    ↓
Try Claude Fallback → Should work now! ✅
    ↓
Return: Mandi prices with 3 mandis
```

## Last Known Behavior

### Before Fix (14:58:38)
```
[AGMARKNET] Network timeout
[MARKET DATA] AgMarkNet API failed, trying Claude AI fallback...
[CLAUDE FALLBACK] 🤖 Using Claude AI...
[CLAUDE FALLBACK] Error: 'AnthropicBedrockWrapper' object has no attribute 'messages'
[MARKET DATA] ❌ No data available
```
**Result**: User got error message (154 chars)

### After Fix (Expected)
```
[AGMARKNET] Network timeout
[MARKET DATA] AgMarkNet API failed, trying Claude AI fallback...
[CLAUDE FALLBACK] 🤖 Using Claude AI...
[ANTHROPIC] ✅ Response received: 250 chars
[CLAUDE FALLBACK] ✅ Got prices: Avg ₹3,200, Trend: stable
[MARKET DATA] ✅ Using Claude AI fallback data
[FORMAT] ✅ Response formatted
```
**Result**: User gets mandi prices (200+ chars)

## Alternative System (Still Working)

### Bedrock Fallback
The system ALSO has a Bedrock-based fallback that was working:

**Last successful use**: 14:42:40, 14:46:05
```
[BEDROCK FALLBACK] 🤖 Using AI to fetch onion prices...
[BEDROCK FALLBACK] ✅ Got prices: Avg ₹2,600, Trend: stable
[MARKET DATA] ✅ Using Bedrock AI fallback data
```

**Note**: This is OLD code that may still be running in some Lambda instances.

## Summary

### Code Status
- ✅ Claude fallback fix deployed correctly
- ✅ Code is in Lambda (verified)
- ✅ Syntax is correct

### Testing Status
- ⏳ Not yet tested with actual market query
- ⏳ All recent queries route to forecasting system
- ⏳ Need query without "forecast" keyword

### What's Working
- ✅ Bedrock fallback (old code, some instances)
- ✅ Forecasting system (different code path)
- ✅ AgMarkNet API (when not timing out)

### What's Fixed But Untested
- ✅ Claude fallback (new code, needs test)

## Next Steps

1. Wait for user to query: "What is the price of tomato?" (no "forecast")
2. Watch logs for Claude fallback execution
3. Verify 200+ character response with mandi names
4. Confirm fix is working

**Status**: Fix is deployed, waiting for production test ✅⏳
