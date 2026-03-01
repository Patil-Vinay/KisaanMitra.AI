# AWS Bedrock Quota Increase Request

## Current Issue
Your bot is being throttled by AWS Bedrock with error:
```
ThrottlingException: Too many requests, please wait before trying again
```

## Why This Happens
- Free tier / default limits are very low (typically 5-10 requests per minute)
- Your bot makes 1-2 API calls per message
- With retries, this can be 3-6 calls per message
- Multiple users or rapid testing quickly exceeds limits

## Solution: Request Quota Increase

### Step 1: Open AWS Service Quotas Console
```bash
# Or visit: https://console.aws.amazon.com/servicequotas/
```

### Step 2: Navigate to Bedrock Quotas
1. Go to AWS Console → Service Quotas
2. Search for "Bedrock" in the service search
3. Select "Amazon Bedrock"

### Step 3: Find the Right Quota
Look for these quotas:
- **"Converse requests per minute"** - Increase to 100-200
- **"InvokeModel requests per minute"** - Increase to 100-200
- **"Claude 3.5 Sonnet requests per minute"** - Increase to 50-100

### Step 4: Request Increase
1. Click on the quota name
2. Click "Request quota increase"
3. Enter desired value (e.g., 100 for requests per minute)
4. Add justification: "Production WhatsApp chatbot for farmers serving agricultural queries"
5. Submit request

### Step 5: Wait for Approval
- Typical approval time: 1-3 business days
- You'll receive email notification
- Some increases are auto-approved instantly

## Alternative: Use Different Model

If you need immediate relief, switch to a cheaper/faster model:

### Option 1: Use Claude 3 Haiku (Faster, Cheaper)
```python
# In ai_orchestrator.py and lambda_whatsapp_kisaanmitra.py
modelId="anthropic.claude-3-haiku-20240307-v1:0"  # Instead of Sonnet
```

### Option 2: Use Amazon Nova (AWS Native, Higher Limits)
```python
modelId="amazon.nova-micro-v1:0"  # Faster, higher limits
```

## Temporary Workaround: Rate Limiting

Add a simple rate limiter to your code:

```python
import time

# Global rate limiter
_last_api_call = 0
_min_interval = 2  # 2 seconds between calls

def rate_limited_bedrock_call():
    global _last_api_call
    now = time.time()
    time_since_last = now - _last_api_call
    
    if time_since_last < _min_interval:
        time.sleep(_min_interval - time_since_last)
    
    _last_api_call = time.time()
    # Make Bedrock call here
```

## Monitor Your Usage

### Check Current Limits
```bash
aws service-quotas get-service-quota \
  --service-code bedrock \
  --quota-code L-3E8C36AF \
  --region us-east-1
```

### Monitor API Calls
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name InvocationCount \
  --dimensions Name=ModelId,Value=anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --start-time 2026-02-27T10:00:00Z \
  --end-time 2026-02-27T11:00:00Z \
  --period 300 \
  --statistics Sum \
  --region us-east-1
```

## Cost Considerations

### Current Model (Claude 3.5 Sonnet)
- Input: $3 per million tokens
- Output: $15 per million tokens
- ~$0.01-0.02 per message

### Alternative Models
- Claude 3 Haiku: $0.25/$1.25 per million tokens (80% cheaper)
- Amazon Nova Micro: $0.075/$0.30 per million tokens (95% cheaper)

## Recommended Action Plan

1. **Immediate (Now):**
   - Wait 10-15 minutes for rate limit to reset
   - Test with single messages, not rapid fire

2. **Short-term (Today):**
   - Request quota increase in AWS Console
   - Consider switching to Claude Haiku for testing

3. **Long-term (This Week):**
   - Implement response caching (already done ✅)
   - Add rate limiting between API calls
   - Monitor usage and costs

## Testing Best Practices

To avoid throttling during testing:
- Wait 5-10 seconds between messages
- Don't send multiple messages rapidly
- Use keyword-based queries (they skip AI calls)
- Test during off-peak hours

## Status Check

Run this to see if you're still throttled:
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --since 2m | grep -i throttl
```

If you see "Throttled" messages, wait longer. If not, you're clear to test.

---

**Current Status:** ⚠️ THROTTLED
**Action Needed:** Request quota increase OR wait 15 minutes
**ETA:** Quota increase approval: 1-3 days
