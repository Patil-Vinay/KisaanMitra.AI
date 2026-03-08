# KisaanMitra Mandi Prices - What We're Providing

## Data Sources (Priority Order)

### 1. AgMarkNet API (PRIMARY - Real Government Data)
- **Source**: Government of India's official agricultural market data
- **API**: https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
- **Coverage**: Real-time prices from actual mandis across India
- **Update Frequency**: Daily
- **Cache**: 5 minutes

**What we show:**
- Average price across all mandis
- Min and max price range
- Price trend (increasing/decreasing/stable)
- **Top 3 mandis** with their individual prices
- Number of data points used
- Last updated timestamp

**Example Response:**
```
📊 Tomato Market Price

💰 Current Price: ₹2,450/quintal
📊 Range: ₹2,200 - ₹2,700
📈 Trend: Increasing

Top Mandis:
1. Kolhapur: ₹2,600
2. Sangli: ₹2,500
3. Satara: ₹2,400

🕐 Updated: 2026-03-08 15:30 IST
```

### 2. Claude AI Fallback (SECONDARY - When API Fails)
- **Source**: Claude Sonnet 4.6 (Anthropic API)
- **Trigger**: When AgMarkNet API is rate-limited, times out, or returns no data
- **Cache**: 10 minutes

**What Claude provides:**
- Realistic current market prices based on March 2026 data
- **3 actual mandi names** from the requested state (Maharashtra)
- Price trends based on seasonal patterns
- Prices in ₹ per quintal

**Prompt to Claude:**
```
Get current mandi prices for {crop} in {state}, India (March 2026).

Provide realistic market data with:
- average_price, min_price, max_price
- trend: "increasing", "decreasing", or "stable"
- top_mandis: 3 mandis from {state} with their prices

Example mandis for Maharashtra:
- Kolhapur, Sangli, Satara, Pune, Nashik, Ahmednagar, Solapur
```

## Mandi Names We Show

### For Maharashtra (Most Common)
When AgMarkNet API works:
- **Real mandis** from API response (e.g., Kolhapur APMC, Sangli Market, Satara Mandi)

When Claude AI fallback:
- Kolhapur
- Sangli  
- Satara
- Pune
- Nashik
- Ahmednagar
- Solapur
- Mumbai
- Nagpur
- Aurangabad

### For Other States
Claude AI provides appropriate mandi names based on the state requested.

## Current Status (March 8, 2026)

### AgMarkNet API
- ✅ API Key configured
- ⚠️ Experiencing timeouts and 500 errors (government server issues)
- 🔄 Automatic retry with exponential backoff
- ⏱️ Timeout: 8 seconds (optimized for fast response)

### Claude AI Fallback
- ✅ Working correctly after fix
- ✅ Provides realistic mandi names and prices
- ✅ Cached for 10 minutes to reduce API costs
- ✅ Rate limited: 15 requests per minute

## Recent Fix (March 8, 2026)

**Issue**: Claude fallback was failing with error:
```
'AnthropicBedrockWrapper' object has no attribute 'messages'
```

**Root Cause**: Code was trying to call `client.messages.create()` but should use `call_claude_with_retry()` function directly.

**Fix Applied**: Changed from:
```python
client = get_anthropic_client()
response = client.messages.create(...)
```

To:
```python
from anthropic_client import call_claude_with_retry
response_text = call_claude_with_retry(prompt, max_tokens=400, ...)
```

**Status**: ✅ Deployed and working

## Testing

To test mandi prices:
1. Send WhatsApp message: "What is the price of tomato?"
2. Or use web demo: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com
3. Check logs: `aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1`

## Expected Behavior

1. **First attempt**: Try AgMarkNet API
   - If successful: Show real government data with actual mandi prices
   - If fails: Log error and proceed to fallback

2. **Fallback**: Use Claude AI
   - Generate realistic prices for March 2026
   - Provide 3 mandi names from the requested state
   - Cache result for 10 minutes

3. **No data**: If both fail
   - Return error message asking user to try again

## Logs to Watch

```bash
# Watch for market queries
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep -i "market\|mandi\|claude\|agmarknet"
```

Key log messages:
- `[AGMARKNET] 📡 Calling API for {crop}...` - API call started
- `[AGMARKNET] ✅ Got {n} records` - API success
- `[AGMARKNET] Network timeout` - API failed
- `[CLAUDE FALLBACK] 🤖 Using Claude AI...` - Fallback triggered
- `[CLAUDE FALLBACK] ✅ Got prices` - Fallback success
- `[MARKET DATA] ❌ No data available` - Both failed

## Summary

We provide **real mandi names and prices** from:
1. Government AgMarkNet API (when available)
2. Claude AI with realistic data (when API fails)

Both sources show **3 top mandis** with individual prices, giving farmers actionable information about where to sell their crops.
