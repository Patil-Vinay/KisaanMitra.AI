# Anthropic API Key Issue - CRITICAL

## Problem
The market price system is failing because the Anthropic API key is **INVALID**.

## Error Details
```
HTTP Error 401: {"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}
```

## Current Invalid Key
```
YOUR_ANTHROPIC_API_KEY
```

## Impact
- AgMarkNet API times out (government server issue)
- Claude AI fallback fails with 401 authentication error
- Users receive generic AI responses with NO mandi data
- Market price feature is completely broken

## Solution Required

### Step 1: Get Valid Anthropic API Key
1. Go to: https://console.anthropic.com/
2. Sign in or create account
3. Navigate to API Keys section
4. Create new API key
5. Copy the key (starts with `sk-ant-api03-`)

### Step 2: Update Lambda Environment Variable
```bash
aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --environment Variables="{
    ANTHROPIC_API_KEY=<YOUR_NEW_KEY>,
    AGMARKNET_API_KEY=$(aws lambda get-function-configuration --function-name whatsapp-llama-bot --region ap-south-1 --query 'Environment.Variables.AGMARKNET_API_KEY' --output text),
    WHATSAPP_TOKEN=$(aws lambda get-function-configuration --function-name whatsapp-llama-bot --region ap-south-1 --query 'Environment.Variables.WHATSAPP_TOKEN' --output text),
    VERIFY_TOKEN=$(aws lambda get-function-configuration --function-name whatsapp-llama-bot --region ap-south-1 --query 'Environment.Variables.VERIFY_TOKEN' --output text)
  }" \
  --region ap-south-1
```

### Step 3: Update .env File
```bash
# Edit .env file
nano .env

# Replace the ANTHROPIC_API_KEY line with your new key
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_NEW_KEY_HERE
```

### Step 4: Test
```bash
# Test the market price query
# Send "What is the current price of tomato?" to WhatsApp bot
```

## Expected Output After Fix
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

## System Flow
1. User asks for market price
2. System tries AgMarkNet API (times out)
3. System falls back to Claude AI
4. Claude AI returns realistic mandi data with 3 mandi names
5. User sees formatted response with prices

## Files Involved
- `src/lambda/anthropic_client.py` - API client
- `src/lambda/market_data_sources.py` - Market data with Claude fallback
- `src/lambda/agents/market_agent.py` - Market agent handler
- `.env` - Environment variables

## Status: BLOCKED
Cannot proceed without valid Anthropic API key.
