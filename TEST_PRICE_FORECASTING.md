# Price Forecasting - Quick Test Guide

## System Status
✅ DynamoDB table created with 5 crops
✅ Lambda deployed with price forecast detection
✅ IAM permissions configured
✅ Ready for testing

## Test Messages

Send these via WhatsApp to test price forecasting:

### Test 1: Week Forecast
```
week forecast for wheat
```
**Expected**: 7-day forecast with daily prices

### Test 2: 7-Day Prices
```
7 day prices for onion
```
**Expected**: 7-day forecast for onion

### Test 3: Simple Forecast
```
price forecast for rice
```
**Expected**: Today + tomorrow forecast

### Test 4: Future Price
```
future price of tomato
```
**Expected**: Today + tomorrow forecast

### Test 5: Unsupported Crop
```
price forecast for potato
```
**Expected**: Error message listing supported crops

## Supported Crops
1. Onion (₹1800/quintal base)
2. Rice (₹2500/quintal base)
3. Sugarcane (₹350/quintal base)
4. Tomato (₹1200/quintal base)
5. Wheat (₹2200/quintal base)

## Check Logs
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --since 5m --region ap-south-1 --format short | grep -i "price\|forecast"
```

## Verify DynamoDB Data
```bash
aws dynamodb get-item --table-name kisaanmitra-price-forecasts --key '{"commodity":{"S":"wheat"}}' --region ap-south-1
```

## Troubleshooting

### If forecast not working:
1. Check Lambda logs for errors
2. Verify DynamoDB table has data
3. Confirm environment variable PRICE_FORECAST_TABLE is set
4. Check IAM role has DynamoDB read permissions

### If routing to wrong agent:
1. Check logs for "[GENERAL AGENT] Detected price forecast query"
2. Verify general_agent.py has price forecast detection
3. Test with different query phrases

## Success Indicators
- ✅ Log shows: `[GENERAL AGENT] Detected price forecast query`
- ✅ Log shows: `[GENERAL AGENT] Extracted crop for forecast: wheat`
- ✅ Log shows: `[PRICE] ===== PRICE FORECAST HANDLER =====`
- ✅ User receives formatted forecast with prices
- ✅ Response includes 7-day data or today/tomorrow data

---

**Ready to test!** Send a message via WhatsApp and check the response.
