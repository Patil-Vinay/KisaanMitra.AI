# AgMarkNet API Setup Guide

## Current Status

✅ **Code Integration**: Complete - Lambda is ready to use AgMarkNet API
⚠️ **API Key**: Placeholder added - needs your real API key

## What AgMarkNet API Does

The AgMarkNet API fetches the **latest 7 days** of real market prices and supplements your 5-year historical data. This ensures your forecasting model always trains on the most recent market conditions.

### Without API Key:
- Uses 5 years of historical data from CSV files (2021-2026)
- Data is static until you manually update CSV files

### With API Key:
- Uses 5 years of historical data PLUS latest 7 days from live API
- Automatically fetches fresh prices before each weekly training
- Ensures model sees most recent market trends

## How to Get Your API Key

### Step 1: Register on Data.gov.in

1. Visit: https://data.gov.in/
2. Click "Sign Up" (top right)
3. Fill in your details:
   - Name
   - Email
   - Organization (can be "Individual" or "KisaanMitra")
   - Purpose: "Agricultural price forecasting"
4. Verify your email
5. Log in

### Step 2: Get API Key for AgMarkNet Dataset

1. Once logged in, search for: **"AgMarkNet"**
2. Look for dataset: **"Daily Price of Various Commodities"**
   - Resource ID: `9ef84268-d588-465a-a308-a864a43d0070`
3. Click on the dataset
4. Click "API" tab
5. Your API key will be displayed
6. Copy the API key (looks like: `579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b`)

## How to Add API Key to Lambda

### Option 1: Using AWS CLI (Recommended)

```powershell
aws lambda update-function-configuration \
  --function-name kisaanmitra-sagemaker-forecaster \
  --region ap-south-1 \
  --environment "Variables={
    S3_BUCKET=kisaanmitra-ml-data,
    SAGEMAKER_ROLE_ARN=arn:aws:iam::482548785371:role/KisaanMitra-SageMaker-Role,
    DYNAMODB_TABLE=kisaanmitra-price-forecasts,
    USE_EXISTING_MODEL=false,
    AGMARKNET_API_KEY=YOUR_ACTUAL_API_KEY_HERE
  }"
```

Replace `YOUR_ACTUAL_API_KEY_HERE` with your real API key.

### Option 2: Using AWS Console

1. Go to AWS Lambda Console
2. Find function: `kisaanmitra-sagemaker-forecaster`
3. Go to "Configuration" tab
4. Click "Environment variables"
5. Click "Edit"
6. Find `AGMARKNET_API_KEY`
7. Replace `YOUR_API_KEY_HERE` with your real API key
8. Click "Save"

## Verify It's Working

After adding the API key, trigger the Lambda manually:

```powershell
aws lambda invoke \
  --function-name kisaanmitra-sagemaker-forecaster \
  --region ap-south-1 \
  output.json

# Check logs
aws logs tail /aws/lambda/kisaanmitra-sagemaker-forecaster \
  --region ap-south-1 \
  --since 5m
```

Look for these log messages:
```
📡 Fetching latest 7 days from AgMarkNet API...
✅ Fetched 35 new records from API
✅ Combined with 7 new API records
```

## What Happens When API Key is Added

### Before Each Training:
1. Load 5 years from S3 CSV files (1,820 days per crop)
2. Fetch latest 7 days from AgMarkNet API
3. Merge data (remove duplicates)
4. Upload combined data to S3
5. Start SageMaker training

### Example Data Flow:
```
Historical CSV: 2021-03-02 to 2026-03-02 (1,820 days)
AgMarkNet API:  2026-03-03 to 2026-03-09 (7 days)
Combined:       2021-03-02 to 2026-03-09 (1,827 days)
```

## API Rate Limits

- **Free Tier**: 1,000 requests per day
- **Our Usage**: 5 crops × 1 request = 5 requests per week
- **Well within limits!**

## Troubleshooting

### API Key Not Working?

Check logs for error messages:
```powershell
aws logs tail /aws/lambda/kisaanmitra-sagemaker-forecaster \
  --region ap-south-1 \
  --since 10m | Select-String "API"
```

Common issues:
- **Invalid API key**: Double-check you copied it correctly
- **API quota exceeded**: Wait 24 hours or upgrade plan
- **Network timeout**: API might be temporarily down

### Still Using CSV Data Only?

If you see this in logs:
```
⚠️ No AgMarkNet API key, skipping live data fetch
✅ Loaded 1820 days of data
```

This means:
- API key is not configured OR
- API key is still set to placeholder `YOUR_API_KEY_HERE`

## Cost

**AgMarkNet API**: FREE ✅
- No cost for API usage
- 1,000 requests/day free tier
- We use only 5 requests/week

## Summary

| Feature | Without API Key | With API Key |
|---------|----------------|--------------|
| Historical Data | 5 years (CSV) | 5 years (CSV) |
| Latest Data | None | Last 7 days (API) |
| Data Freshness | Manual updates | Auto-updated weekly |
| Training Accuracy | Good | Better |
| Cost | $0 | $0 |

## Next Steps

1. ✅ Register on data.gov.in
2. ✅ Get API key for AgMarkNet dataset
3. ✅ Add API key to Lambda environment variable
4. ✅ Test by invoking Lambda
5. ✅ Check logs to verify API is being called

---

**Current Status**: Placeholder API key added - waiting for your real key
**Documentation**: https://data.gov.in/
**Support**: Contact data.gov.in support if you have issues getting API key
