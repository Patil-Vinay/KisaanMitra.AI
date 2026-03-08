# KisaanMitra Live URLs 🚀

## ✅ Primary URL (CloudFront - HTTPS)
**Use this URL - Works on all devices including mobile:**
```
https://d28gkw3jboipw5.cloudfront.net/
```

### Features:
- ✅ HTTPS (secure)
- ✅ Works on all mobile networks
- ✅ Fast global CDN
- ✅ Image upload with preview
- ✅ Onboarding flow enabled
- ✅ All features working

## Alternative URLs

### S3 Direct (HTTPS)
```
https://kisaanmitra-web-demo-1772974554.s3.ap-south-1.amazonaws.com/index.html
```

### Knowledge Graph (LIVE DATA - 10,006 Farmers)
```
https://d28gkw3jboipw5.cloudfront.net/knowledge-graph.html
```
**OR**
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com/
```

**Data Stats:**
- 10,000 dummy farmers + 6 real farmers = 10,006 total
- 9 districts, 191 villages, 31 crops
- 184,527 acres total land
- Auto-updates hourly via Lambda
- Last updated: 2026-03-08T16:25:06

## What's Included

### 1. Image Upload with Preview ✅
- Click "📸 Upload Image"
- Select crop image
- Preview appears before sending
- Click "Send Image" to analyze
- Get AI disease detection results

### 2. Onboarding Flow ✅
- Enter phone number on first visit
- Answer onboarding questions:
  - Name
  - Location (village, district, state)
  - Farm size
  - Crops grown
- Profile saved in DynamoDB
- Personalized responses

### 3. AI Features ✅
- 🌱 Crop advice
- 📊 Market prices (live mandi data)
- 💰 Finance planning
- 🌤️ Weather updates
- 🔬 Disease detection
- 📈 Price forecasting

### 4. Knowledge Graph Dashboard ✅
- Live data from DynamoDB + dummy dataset
- Shows all 10,006 farmers
- Top districts and crops
- Real-time statistics
- Auto-refreshes hourly

## CloudFront Details
- **Distribution ID:** E17NCPEJL27P1L
- **Domain:** d28gkw3jboipw5.cloudfront.net
- **Status:** Deployed ✅
- **Cache:** Invalidated (latest version)
- **Origin:** S3 Website Endpoint
- **Protocol:** HTTPS with auto-redirect

## Testing Checklist

### New User:
1. ✅ Open CloudFront URL
2. ✅ Phone number modal appears
3. ✅ Enter 10-digit number
4. ✅ Click "Start Chatting"
5. ✅ Onboarding questions appear
6. ✅ Complete registration
7. ✅ Use all features

### Returning User:
1. ✅ Open CloudFront URL
2. ✅ Auto-login with stored number
3. ✅ Welcome back message
4. ✅ All features available

### Image Upload:
1. ✅ Click "📸 Upload Image"
2. ✅ Select crop image
3. ✅ Preview popup appears
4. ✅ Click "Send Image"
5. ✅ Get disease analysis

### Demo Mode:
1. ✅ Click "Skip (Demo Mode)"
2. ✅ No onboarding
3. ✅ Use features immediately
4. ✅ Data not saved

### Knowledge Graph:
1. ✅ Open KG URL
2. ✅ See 10,006 total farmers
3. ✅ View top districts and crops
4. ✅ Click refresh to update
5. ✅ Hard refresh (Ctrl+Shift+R) if cached

## Recent Updates

### Latest Deployment (March 8, 2026 - 21:56 IST)
1. ✅ Fixed Knowledge Graph data merge
2. ✅ Now shows 10,000 dummy + 6 real farmers
3. ✅ Created live KG dashboard with real-time data
4. ✅ Lambda auto-updates KG hourly
5. ✅ CloudFront cache invalidated
6. ✅ All URLs updated

### Previous Updates (March 8, 2026 - 21:27 IST)
1. ✅ Fixed onboarding flow in web demo
2. ✅ Added image preview before upload
3. ✅ CloudFront CDN deployed
4. ✅ Cache invalidated for latest version
5. ✅ HTTPS working on all devices

## Troubleshooting

### If CloudFront URL doesn't work:
1. Wait 1-2 minutes for cache invalidation
2. Clear browser cache (Ctrl+Shift+R)
3. Try incognito/private mode
4. Use S3 direct URL as backup

### If onboarding doesn't start:
1. Clear localStorage
2. Refresh page
3. Enter phone number again
4. Should see "What's your name?"

### If image upload doesn't work:
1. Check file size (< 5MB)
2. Use JPG/PNG format
3. Try sample image button
4. Check browser console for errors

### If Knowledge Graph shows old data:
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Open in incognito/private mode
3. Clear browser cache for the site
4. Wait for CloudFront cache to clear (1-2 min)
5. Click "Refresh Data" button on KG page

## API Endpoint
```
https://8zu6u7bc48.execute-api.ap-south-1.amazonaws.com/prod/chat
```

## Status: LIVE AND WORKING ✅

All features are deployed and working on both CloudFront and S3 URLs. CloudFront is the recommended URL for best performance and mobile compatibility. Knowledge Graph now shows live data with 10,006 farmers (10k dummy + 6 real).

**Last Updated:** March 8, 2026 - 21:56 IST
