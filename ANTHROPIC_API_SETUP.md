# Anthropic Claude API Integration Guide

## Overview

We've integrated direct Anthropic Claude API to replace AWS Bedrock for budget generation. This provides:

✅ **Better Accuracy** - Claude 3.5 Sonnet is more reliable than Nova Lite  
✅ **Higher Rate Limits** - Anthropic API has better rate limits than Bedrock  
✅ **Realistic Outputs** - Combined with validation layer for perfect results  
✅ **Cost Effective** - Pay only for what you use  

## Step 1: Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in with your account
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy the API key (starts with `sk-ant-`)
6. Keep it secure!

**Pricing:** https://www.anthropic.com/pricing
- Claude 3.5 Sonnet: $3 per million input tokens, $15 per million output tokens
- Much cheaper than you think (a budget request costs ~$0.01)

## Step 2: Deploy Updated Lambda Code

Deploy the Lambda with Anthropic client integration:

```bash
cd src/lambda
bash deploy_whatsapp.sh
```

This will:
- Include the new `anthropic_client.py` module
- Update Lambda code to support both Bedrock and Anthropic
- Keep validation layer for double protection

## Step 3: Add API Key to Lambda

Run the setup script:

```bash
cd infrastructure
bash add_anthropic_key.sh
```

It will:
1. Prompt you for your Anthropic API key
2. Add it to Lambda environment variables
3. Enable `USE_ANTHROPIC_DIRECT=true` flag
4. Update Lambda configuration

**Manual Method (if script fails):**

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --region ap-south-1 \
    --environment Variables="{
        ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE,
        USE_ANTHROPIC_DIRECT=true,
        ...other existing vars...
    }"
```

## Step 4: Test

Send a budget request via WhatsApp:

```
I need onion budget for 20 acres in jalgaon
```

Check logs to verify it's using Anthropic:

```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep ANTHROPIC
```

You should see:
```
[INIT] Using direct Anthropic Claude API
[ANTHROPIC] Calling Claude API: claude-3-5-sonnet-20241022
[ANTHROPIC] ✅ Response received: 1234 chars
```

## How It Works

### Architecture

```
User Request
    ↓
Lambda Handler
    ↓
Check USE_ANTHROPIC_DIRECT flag
    ↓
┌─────────────────┬──────────────────┐
│  If TRUE        │  If FALSE        │
│  (Anthropic)    │  (Bedrock)       │
├─────────────────┼──────────────────┤
│ anthropic_      │ boto3.client     │
│ client.py       │ (bedrock)        │
│     ↓           │     ↓            │
│ Direct HTTPS    │ AWS Bedrock      │
│ to Anthropic    │ API              │
│     ↓           │     ↓            │
│ Claude 3.5      │ Nova Lite        │
│ Sonnet          │                  │
└─────────────────┴──────────────────┘
    ↓
Validation Layer (crop_yield_database.py)
    ↓
Corrected Budget Response
```

### Code Changes

**1. anthropic_client.py** (NEW)
- Direct HTTP client for Anthropic API
- Bedrock-compatible wrapper for easy migration
- Retry logic with exponential backoff
- Error handling

**2. lambda_whatsapp_kisaanmitra.py** (UPDATED)
- Check `USE_ANTHROPIC_DIRECT` environment variable
- Use `anthropic_client` if enabled, else use Bedrock
- Dynamic model selection based on API type
- Backward compatible

**3. crop_yield_database.py** (EXISTING)
- Validates yields and costs
- Corrects unrealistic AI outputs
- Works with both Anthropic and Bedrock

## Configuration

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Your Anthropic API key |
| `USE_ANTHROPIC_DIRECT` | `true` | Enable direct Anthropic API |

### Switch Back to Bedrock

If you want to switch back to Bedrock:

```bash
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --region ap-south-1 \
    --environment Variables="{USE_ANTHROPIC_DIRECT=false,...}"
```

Or remove the environment variable entirely.

## Expected Results

### Before (Nova Lite + Validation)
```
Onion 20 acres:
- Cost: ₹6,200/acre → Corrected to ₹55,000/acre
- Yield: 150 quintals/acre → Corrected to 130 quintals/acre
- ROI: 2319% → Corrected to ~100%
```

### After (Claude 3.5 Sonnet + Validation)
```
Onion 20 acres:
- Cost: ₹52,000/acre (realistic from start)
- Yield: 120 quintals/acre (realistic from start)
- ROI: 85% (realistic from start)
- Minimal corrections needed
```

## Monitoring

### Check API Usage

View logs to see Anthropic API calls:

```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --since 1h --region ap-south-1 | grep -E "ANTHROPIC|VALIDATION"
```

### Cost Tracking

Monitor your Anthropic API usage:
1. Go to https://console.anthropic.com/
2. Check **Usage** section
3. View costs per day/month

Typical costs:
- Budget request: ~1,500 tokens input + 500 tokens output = $0.01
- 100 requests/day = $1/day = $30/month

## Troubleshooting

### Error: "ANTHROPIC_API_KEY environment variable not set"

**Solution:** Run `bash infrastructure/add_anthropic_key.sh`

### Error: "401 Unauthorized"

**Solution:** Check your API key is correct and active

### Error: "429 Rate Limit"

**Solution:** Anthropic has rate limits. The client has retry logic, but if persistent:
- Upgrade your Anthropic plan
- Or switch back to Bedrock temporarily

### Still Getting Unrealistic Numbers

**Check:**
1. Logs show `[ANTHROPIC]` messages (confirming it's using Claude)
2. Validation layer is running (look for `[VALIDATION]` logs)
3. API key is valid

## Fallback Strategy

The system is designed with fallback:

1. **Primary:** Anthropic Claude API (best accuracy)
2. **Validation:** crop_yield_database.py (catches errors)
3. **Fallback:** Can switch back to Bedrock anytime

## Files Modified

1. `src/lambda/anthropic_client.py` - NEW
2. `src/lambda/lambda_whatsapp_kisaanmitra.py` - Updated client initialization
3. `src/lambda/deploy_whatsapp.sh` - Include anthropic_client.py
4. `infrastructure/add_anthropic_key.sh` - NEW setup script

## Next Steps

1. ✅ Deploy updated Lambda code
2. ✅ Add Anthropic API key
3. ✅ Test with budget request
4. ✅ Monitor logs and costs
5. ✅ Enjoy accurate budgets!

## Support

If you encounter issues:
1. Check logs: `aws logs tail /aws/lambda/whatsapp-llama-bot --follow`
2. Verify API key is set: `aws lambda get-function-configuration --function-name whatsapp-llama-bot --query 'Environment.Variables.ANTHROPIC_API_KEY'`
3. Test API key directly: `curl https://api.anthropic.com/v1/messages -H "x-api-key: YOUR-KEY"`
