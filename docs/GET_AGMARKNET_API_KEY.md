# How to Get AgMarkNet API Key from data.gov.in

## Step-by-Step Guide

### Step 1: Visit data.gov.in
Go to: https://data.gov.in/

### Step 2: Register/Login
1. Click **Sign Up** (top right corner)
2. Fill in details:
   - Full Name
   - Email
   - Mobile Number
   - Password
   - Organization (optional - can put "Individual" or "Farmer")
3. Verify email
4. Login with your credentials

### Step 3: Find AgMarkNet Dataset
1. Go directly to: https://data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
   
   OR
   
2. Search for "AgMarkNet" or "Mandi Prices" in the search bar
3. Click on **"Current Daily Price of Various Commodities from Various Markets (Mandi)"**

### Step 4: Request API Access
1. On the dataset page, look for **"API"** tab or **"API Access"** button
2. Click **"Request API Access"** or **"Get API Key"**
3. Fill in the API request form:
   - Purpose: "Agricultural price analysis for farmers"
   - Usage: "Mobile application for farmer assistance"
4. Submit the request

### Step 5: Get Your API Key
1. You'll receive an email with your API key (usually within 24 hours)
2. OR check your profile/dashboard on data.gov.in
3. Look for **"My API Keys"** or **"API Credentials"** section
4. Copy your API key

### Step 6: Add to AWS Lambda
1. Go to: https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/whatsapp-llama-bot
2. Click **Configuration** → **Environment variables** → **Edit**
3. Add:
   ```
   Key: AGMARKNET_API_KEY
   Value: [paste your API key here]
   ```
4. Click **Save**

## ⚡ RECOMMENDED: Use Without API Key (Deploy Now!)

**data.gov.in not working?** No problem! Deploy without it:

**Use this placeholder:**
```
AGMARKNET_API_KEY=not_available
```

**What happens:**
- ✅ Market agent will still work perfectly
- ✅ Uses Bedrock AI to provide market information
- ✅ Gives price trends and recommendations
- ✅ No real-time API data, but still helpful
- ✅ You can add real key later when site works

**This is the recommended approach for now!**

## API Key Format

Your API key will look something like:
```
579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b
```

## Troubleshooting

### Can't find API section on data.gov.in?
- The website layout changes sometimes
- Look for "Developer" or "API" in the menu
- Or email: data-support@gov.in

### API request taking too long?
- Usually approved within 24-48 hours
- Check spam folder for approval email
- Use test key in the meantime

### API key not working?
- Check if you copied the full key (no spaces)
- Verify key is active in your data.gov.in profile
- Check CloudWatch logs for specific error message

## API Usage Limits

**Free Tier:**
- 500 requests per day
- Sufficient for testing and small-scale use

**For Production:**
- Contact data.gov.in for higher limits
- Or implement caching (already done - 6 hour cache)

## Testing Your API Key

Once you have the key, test it:

```bash
curl -X GET "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=YOUR_API_KEY&format=json&limit=5&filters[commodity]=Wheat"
```

Expected response: JSON with wheat prices from various mandis

## Quick Reference

| Step | Action | Time |
|------|--------|------|
| 1 | Register on data.gov.in | 5 min |
| 2 | Find AgMarkNet dataset | 2 min |
| 3 | Request API access | 3 min |
| 4 | Wait for approval | 24-48 hrs |
| 5 | Add to Lambda | 1 min |

**Total active time: ~10 minutes**
**Total wait time: 1-2 days**

## For Immediate Testing

**Don't want to wait?** Use this approach:

1. Add placeholder key: `AGMARKNET_API_KEY=test_key_123`
2. Deploy and test other features (Finance agent, Crop agent)
3. Market agent will give AI-based responses (not real-time data)
4. Update to real key when you get it

The system is designed to work with or without the real API key!
