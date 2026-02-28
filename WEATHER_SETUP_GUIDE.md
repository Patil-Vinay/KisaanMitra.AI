# Weather Integration Setup Guide

**Status**: Weather code is deployed but using MOCK data  
**Action Required**: Get OpenWeather API key

---

## Current Status

✅ Weather service is loaded and working  
✅ Weather integration added to crop queries  
⚠️ Using MOCK data (not real weather)  
❌ OpenWeather API key not configured

---

## How Weather Integration Works

### 1. For Text Crop Queries
When you ask crop-related questions like:
- "When should I plant wheat?"
- "Is it good time to spray pesticides?"
- "What crops are suitable for this season?"

The system will:
1. Detect your location from the message (or use default: Pune)
2. Fetch weather forecast for that location
3. Add weather context to the AI response
4. Provide weather-aware recommendations

### Example

**User**: "When should I plant tomatoes?"

**Response** (with weather):
```
Tomatoes are best planted in October-November or February-March.

🌤️ Weather Forecast - Pune
🌡️ Temperature: 18°C - 28°C
🌧️ Rain: No rain in next 3 days
☀️ Weather is favorable

You can start preparing the land now. Ensure proper drainage before planting.
```

### 2. For Weather Button
When you click the "Weather Forecast" button in the menu, you get a dedicated weather report.

---

## Get OpenWeather API Key (FREE)

### Step 1: Sign Up
1. Visit: https://openweathermap.org/api
2. Click "Sign Up" (top right)
3. Create a free account
4. Verify your email

### Step 2: Get API Key
1. Log in to your account
2. Go to: https://home.openweathermap.org/api_keys
3. Your default API key will be shown
4. Copy the API key (looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### Step 3: Add to Lambda
```bash
# Set the environment variable
aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --environment "Variables={
    OPENWEATHER_API_KEY=your_api_key_here,
    S3_BUCKET=kisaanmitra-images,
    CROP_HEALTH_API_KEY=YOUR_CROP_HEALTH_API_KEY,
    AGMARKNET_API_KEY=not_available,
    CONVERSATION_TABLE=kisaanmitra-conversations,
    PHONE_NUMBER_ID=1049535664900621,
    WA_TOKEN=YOUR_WHATSAPP_TOKEN,
    USE_ANTHROPIC_DIRECT=true,
    VERIFY_TOKEN=mySecret_123,
    WHATSAPP_TOKEN=YOUR_WHATSAPP_TOKEN,
    ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY
  }"
```

Or use the helper script:
```bash
# Create a script
cat > infrastructure/add_weather_key.sh << 'EOF'
#!/bin/bash
WEATHER_KEY=$1

if [ -z "$WEATHER_KEY" ]; then
    echo "Usage: ./add_weather_key.sh YOUR_API_KEY"
    exit 1
fi

aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --environment Variables="{OPENWEATHER_API_KEY=$WEATHER_KEY}" \
  --region ap-south-1

echo "✅ Weather API key added!"
EOF

chmod +x infrastructure/add_weather_key.sh

# Run it
./infrastructure/add_weather_key.sh YOUR_API_KEY_HERE
```

### Step 4: Verify
Send a crop query via WhatsApp:
- "When should I plant wheat?"
- Check logs: `aws logs tail /aws/lambda/whatsapp-llama-bot --follow`
- Should see: `[WEATHER] Fetching weather for Pune` (not "using mock data")

---

## Free Tier Limits

OpenWeather Free Tier:
- ✅ 60 calls per minute
- ✅ 1,000,000 calls per month
- ✅ 3-hour forecast data
- ✅ Current weather data
- ✅ More than enough for this use case!

---

## Testing Weather Integration

### Test 1: Text Crop Query
**Send via WhatsApp**: "When should I plant tomatoes?"

**Expected Response**:
```
Tomatoes are best planted in...

🌤️ Weather Forecast - Pune
🌡️ Temperature: 20°C - 30°C
🌧️ Rain: Yes, in 2 days
⚠️ Rain coming in 24 hours - spray pesticides now!

[Rest of crop advice]
```

### Test 2: Weather Button
**Action**: Click "Weather Forecast" button in menu

**Expected Response**:
```
🌤️ Weather Forecast - Maharashtra
🌡️ Temperature: 18°C - 28°C
🌧️ Rain: No rain in next 3 days

🌾 Farming Advice:
• ✅ Weather is favorable
```

### Test 3: Check Logs
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow | grep WEATHER
```

**Expected Output** (with API key):
```
[WEATHER] Using location: Pune
[WEATHER] Fetching weather for Pune
[WEATHER] Weather context added
```

**Current Output** (without API key):
```
[WEATHER] API key not available, using mock data
[WARNING] ⚠️⚠️⚠️  Using MOCK weather data
```

---

## Why Mock Data is Bad

Mock weather data:
- ❌ Always shows same temperature (28°C)
- ❌ Never predicts rain accurately
- ❌ Gives generic advice
- ❌ Can mislead farmers
- ❌ Reduces trust in the system

Real weather data:
- ✅ Accurate temperature forecasts
- ✅ Rain predictions (critical for farming)
- ✅ Specific, actionable advice
- ✅ Helps farmers make better decisions
- ✅ Builds trust and engagement

---

## Troubleshooting

### Issue: Still seeing "mock data" after adding key
**Solution**: 
1. Verify key is set: `aws lambda get-function-configuration --function-name whatsapp-llama-bot --query 'Environment.Variables.OPENWEATHER_API_KEY'`
2. Wait 1-2 minutes for Lambda to pick up new environment variable
3. Send a new message (don't retry old one)

### Issue: "Invalid API key" error
**Solution**:
1. Check if API key is activated (takes 10 minutes after signup)
2. Verify you copied the entire key (no spaces)
3. Check if you're using the correct key from https://home.openweathermap.org/api_keys

### Issue: Weather not showing in crop responses
**Solution**:
1. Make sure you're sending TEXT queries (not images)
2. Ask crop-related questions like "when to plant wheat"
3. Check logs for `[WEATHER]` messages

---

## Summary

**Current Status**: Weather integration is coded and deployed, but using mock data

**To Fix**: 
1. Get free OpenWeather API key (5 minutes)
2. Add to Lambda environment variables (1 minute)
3. Test with crop query (30 seconds)

**Total Time**: ~7 minutes to get real weather working!

---

**Next Step**: Get your API key from https://openweathermap.org/api
