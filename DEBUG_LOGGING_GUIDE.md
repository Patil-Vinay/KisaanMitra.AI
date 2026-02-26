# Debug Logging Guide - KisaanMitra

## Enhanced Debug Logs Deployed ✅

The Lambda function now includes comprehensive debug logging to track every step of execution.

## Log Levels

- `[DEBUG]` - Detailed execution flow and variable states
- `[INFO]` - Important milestones and successful operations (with emojis)
- `[ERROR]` - Errors with full tracebacks

## What's Logged

### 1. Lambda Invocation
```
[DEBUG] ======================================== 
[DEBUG] LAMBDA INVOCATION STARTED
[DEBUG] ========================================
[DEBUG] Event: {full event JSON}
[DEBUG] Lambda Memory: 2048 MB
[DEBUG] Lambda Timeout: 120 seconds remaining
```

### 2. Webhook Processing
```
[DEBUG] Webhook payload received
[DEBUG] Payload keys: ['messages', 'contacts', ...]
[INFO] 📱 Message from: +91XXXXXXXXXX
[INFO] 📝 Message type: text
[INFO] 📨 User message: "give me onion budget"
```

### 3. Agent Routing
```
[DEBUG] ===== ROUTING MESSAGE =====
[DEBUG] User ID: +91XXXXXXXXXX
[DEBUG] Message: "give me onion budget"
[DEBUG] LangGraph Available: False
[DEBUG] Using fallback keyword-based routing...
[INFO] ✅ Fallback routing selected: FINANCE
[INFO] 🎯 SELECTED AGENT: FINANCE
```

### 4. Finance Agent Execution
```
[DEBUG] ===== FINANCE AGENT =====
[DEBUG] Processing finance query: "give me onion budget"
[DEBUG] User ID: +91XXXXXXXXXX
[DEBUG] Fetching conversation history...
[DEBUG] Retrieved 3 conversation items from DynamoDB
[DEBUG] Building context from 3 history items
[DEBUG] Context built successfully, length: 450 chars
[DEBUG] Budget request detected: True
[DEBUG] Processing budget request...
```

### 5. Crop Extraction
```
[DEBUG] Extracting crop name using AI...
[DEBUG] Message: "give me onion budget"
[DEBUG] Has conversation context: True
[DEBUG] Calling Bedrock for crop extraction...
[INFO] ✅ AI extracted crop: onion
[DEBUG] Land size extracted: 1 acre(s)
[DEBUG] Location extracted: Maharashtra
```

### 6. Budget Generation
```
[INFO] 📊 Generating budget for onion, 1 acre(s) in Maharashtra
[DEBUG] Generating AI budget for crop: onion, land: 1 acre(s), location: Maharashtra
[DEBUG] Calling Bedrock for budget generation...
[DEBUG] Model: us.amazon.nova-pro-v1:0, MaxTokens: 2000, Temperature: 0.4
[INFO] ✅ AI generated detailed budget for onion in Maharashtra
[DEBUG] Budget text length: 850 chars
[DEBUG] Budget preview: Seeds: ₹3,500...
[DEBUG] Budget parsed successfully
```

### 7. Budget Parsing
```
[DEBUG] Parsing AI budget text...
[DEBUG] Extracted seeds: 3500
[DEBUG] Extracted fertilizer: 8000
[DEBUG] Extracted pesticides: 4500
[DEBUG] Extracted irrigation: 6000
[DEBUG] Extracted labor: 12000
[DEBUG] Extracted machinery: 5000
[DEBUG] Extracted total_cost: 39000
[DEBUG] Extracted expected_yield: 120
[DEBUG] Extracted expected_price: 1500
[DEBUG] Extracted expected_revenue: 180000
[DEBUG] Extracted expected_profit: 141000
[DEBUG] Budget parsing complete - Total Cost: ₹39,000, Profit: ₹141,000
```

### 8. Market Agent Execution
```
[DEBUG] ===== MARKET AGENT =====
[DEBUG] Processing market query: "wheat price"
[DEBUG] Searching for crop keywords in message...
[DEBUG] ✅ Detected crop: wheat
[DEBUG] Using FAST static market data for wheat
[DEBUG] get_fast_market_prices called for: wheat
[INFO] ✅ Using static market data for wheat
[DEBUG] Price: ₹2450, Trend: stable
[DEBUG] Market data retrieved successfully
[DEBUG] Average price: ₹2450, Trend: stable
[DEBUG] Formatting market response for: wheat
[DEBUG] Market response formatted successfully
```

### 9. Crop Agent Execution
```
[DEBUG] ===== CROP AGENT =====
[DEBUG] Processing crop query: "my wheat has yellow spots"
[DEBUG] Calling Bedrock - Model: us.amazon.nova-pro-v1:0
[DEBUG] Prompt length: 45 chars
[DEBUG] Context length: 0 chars
[DEBUG] System prompt: You are a helpful farming assistant...
[DEBUG] Sending request to Bedrock...
[DEBUG] Bedrock response received, length: 180 chars
[DEBUG] Crop agent response generated
```

### 10. Greeting Agent
```
[DEBUG] ===== GREETING AGENT =====
[DEBUG] Selected greeting: Hello! I'm Kisaan Mitra...
```

### 11. General Agent
```
[DEBUG] ===== GENERAL AGENT =====
[DEBUG] Processing general query: "how are you"
[DEBUG] General agent response generated
```

### 12. WhatsApp Delivery
```
[DEBUG] Sending WhatsApp message to: +91XXXXXXXXXX
[DEBUG] Message length: 450 chars
[DEBUG] Message preview: 💰 *Onion Budget Plan*...
[INFO] ✅ WhatsApp API response: 200
```

### 13. Conversation Saving
```
[DEBUG] Saving conversation - User: +91XXXXXXXXXX, Agent: finance
[DEBUG] Message length: 20 chars, Response length: 450 chars
[DEBUG] Conversation saved successfully to DynamoDB
```

### 14. Completion
```
[INFO] ✅ Request completed successfully
[DEBUG] ========================================
[DEBUG] LAMBDA INVOCATION COMPLETED
[DEBUG] ========================================
```

### 15. Error Handling
```
[ERROR] ❌ Lambda execution error: {error message}
[ERROR] Full traceback:
{complete stack trace}
```

## How to View Logs

### Real-time Streaming
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

### Last 5 Minutes
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --since 5m --region ap-south-1
```

### Filter by Log Level
```bash
# Only errors
aws logs tail /aws/lambda/whatsapp-llama-bot --filter-pattern "[ERROR]" --region ap-south-1

# Only info
aws logs tail /aws/lambda/whatsapp-llama-bot --filter-pattern "[INFO]" --region ap-south-1

# Agent routing
aws logs tail /aws/lambda/whatsapp-llama-bot --filter-pattern "SELECTED AGENT" --region ap-south-1
```

## Key Metrics to Track

1. **Agent Selection**: Look for `[INFO] 🎯 SELECTED AGENT: {AGENT_NAME}`
2. **Crop Detection**: Look for `[INFO] ✅ AI extracted crop: {crop_name}`
3. **Budget Generation**: Look for `[INFO] 📊 Generating budget for {crop}, {size} acre(s) in {location}`
4. **Response Time**: Check timestamps between "INVOCATION STARTED" and "COMPLETED"
5. **Errors**: Look for `[ERROR]` tags with full tracebacks

## Example Log Flow

```
16:54:00.123 [DEBUG] LAMBDA INVOCATION STARTED
16:54:00.125 [INFO] 📱 Message from: +91XXXXXXXXXX
16:54:00.126 [INFO] 📨 User message: "give me onion budget"
16:54:00.127 [DEBUG] ===== ROUTING MESSAGE =====
16:54:00.128 [INFO] ✅ Fallback routing selected: FINANCE
16:54:00.129 [INFO] 🎯 SELECTED AGENT: FINANCE
16:54:00.130 [DEBUG] ===== FINANCE AGENT =====
16:54:00.135 [DEBUG] Retrieved 3 conversation items from DynamoDB
16:54:00.140 [DEBUG] Budget request detected: True
16:54:00.145 [DEBUG] Extracting crop name using AI...
16:54:01.250 [INFO] ✅ AI extracted crop: onion
16:54:01.255 [INFO] 📊 Generating budget for onion, 1 acre(s) in Maharashtra
16:54:07.890 [INFO] ✅ AI generated detailed budget for onion in Maharashtra
16:54:07.895 [DEBUG] Budget parsing complete - Total Cost: ₹39,000, Profit: ₹141,000
16:54:07.900 [DEBUG] Sending WhatsApp message to: +91XXXXXXXXXX
16:54:08.120 [INFO] ✅ WhatsApp API response: 200
16:54:08.125 [INFO] ✅ Request completed successfully
16:54:08.130 [DEBUG] LAMBDA INVOCATION COMPLETED
```

## Troubleshooting with Logs

### Issue: Wrong agent selected
- Search for: `SELECTED AGENT`
- Check: Routing logic and keyword detection

### Issue: Crop not detected
- Search for: `AI extracted crop`
- Check: Crop extraction prompt and user message

### Issue: Budget generation fails
- Search for: `Budget generation error`
- Check: Bedrock API errors and parsing issues

### Issue: WhatsApp delivery fails
- Search for: `WhatsApp API response`
- Check: Status code and error response

### Issue: DynamoDB errors
- Search for: `Error fetching` or `Error saving`
- Check: Permissions and table names

## Status

✅ Debug logging deployed and active
✅ All agents instrumented
✅ Error tracking with full tracebacks
✅ Performance metrics included
✅ Ready for production monitoring
