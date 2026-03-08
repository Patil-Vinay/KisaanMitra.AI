# Fix WhatsApp Token Issue

## Problem
```
[ERROR] WhatsApp API error: "The access token could not be decrypted"
```

Your WhatsApp access token has expired. Everything else is working perfectly:
- ✅ Lambda receiving messages
- ✅ Price forecasting system working
- ✅ DynamoDB has all forecasts
- ❌ Can't send WhatsApp responses (token expired)

## Solution: Update Token

### Step 1: Get New Token

1. Go to https://developers.facebook.com/apps
2. Select your WhatsApp Business app
3. Click "WhatsApp" in left sidebar
4. Click "API Setup"
5. Copy the "Temporary access token"

### Step 2: Update Lambda (Choose One Method)

#### Method A: Using PowerShell Script (Easiest)
```powershell
.\scripts\update_whatsapp_token.ps1
```
Paste your new token when prompted.

#### Method B: Using AWS CLI Directly
```bash
aws lambda update-function-configuration \
  --function-name whatsapp-llama-bot \
  --environment "Variables={
    WHATSAPP_TOKEN=YOUR_NEW_TOKEN_HERE,
    PHONE_NUMBER_ID=1049535664900621,
    VERIFY_TOKEN=mySecret_123,
    USE_ANTHROPIC_DIRECT=true,
    ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY,
    OPENWEATHER_API_KEY=YOUR_OPENWEATHER_API_KEY,
    AGMARKNET_API_KEY=YOUR_AGMARKNET_API_KEY,
    CROP_HEALTH_API_KEY=YOUR_CROP_HEALTH_API_KEY,
    S3_BUCKET=kisaanmitra-images,
    CONVERSATION_TABLE=kisaanmitra-conversations,
    PRICE_FORECAST_TABLE=kisaanmitra-price-forecasts
  }" \
  --region ap-south-1
```

#### Method C: AWS Console
1. Go to AWS Lambda Console
2. Open function: `whatsapp-llama-bot`
3. Go to Configuration > Environment variables
4. Edit `WHATSAPP_TOKEN`
5. Paste new token
6. Save

### Step 3: Test

Send "Hi" to your WhatsApp number. You should get the main menu.

## For Production: Get Permanent Token

Temporary tokens expire every 24 hours. For production:

1. Go to Meta Business Suite
2. Settings > System Users
3. Create a System User
4. Generate Token with these permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
5. This token never expires
6. Update Lambda with permanent token

## Verify It's Working

### Check Logs
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --since 2m --region ap-south-1
```

Look for:
- ✅ `[WHATSAPP] API response: 200` (good)
- ❌ `[WHATSAPP] API response: 401` (token still invalid)

### Test Queries
1. "Hi" - Should show main menu
2. "week forecast for wheat" - Should show 7-day forecast
3. "price forecast for onion" - Should show today/tomorrow prices

## Everything Else is Working!

Your system is fully functional:
- ✅ Lambda deployed and running
- ✅ Price forecasting integrated
- ✅ DynamoDB has 5 crops with 30-day forecasts
- ✅ Prophet models trained on 1800+ records
- ✅ General agent detecting price queries
- ✅ Daily training script ready

Only issue: WhatsApp token expired (common, happens every 24 hours with temp tokens)

---

**Quick Fix**: Run `.\scripts\update_whatsapp_token.ps1` and paste your new token!
