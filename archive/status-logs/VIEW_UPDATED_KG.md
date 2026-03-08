# How to View Updated Knowledge Graph 🌾

## ✅ ISSUE FIXED - Data Now Shows 10,006 Farmers

Your Knowledge Graph has been updated and now shows:
- **10,000 dummy farmers** (for scale demonstration)
- **6 real farmers** (from actual system usage)
- **Total: 10,006 farmers**

## 🔗 URLs to Access

### Option 1: CloudFront (HTTPS - Recommended)
```
https://d28gkw3jboipw5.cloudfront.net/knowledge-graph.html
```

### Option 2: S3 Direct (HTTP)
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com/
```

### Option 3: From Web Demo Footer
Click the "🌐 Knowledge Graph" button in the footer of your web demo.

## ⚠️ IMPORTANT: Clear Your Browser Cache

You MUST clear your browser cache to see the updated data. Choose one method:

### Method 1: Hard Refresh (Easiest)
- **Windows/Linux:** Press `Ctrl + Shift + R`
- **Mac:** Press `Cmd + Shift + R`
- **Mobile Chrome:** Settings → Privacy → Clear browsing data → Cached images

### Method 2: Incognito/Private Mode
1. Open a new incognito/private window
2. Paste the KG URL
3. You'll see fresh data without any cache

### Method 3: Clear Site Data
1. Open the KG page
2. Press F12 (Developer Tools)
3. Right-click the refresh button
4. Select "Empty Cache and Hard Reload"

## 📊 What You Should See

### Statistics Card
```
Total Farmers: 10,006
Districts: 9
Villages: 191
Crops: 31
Total Land: 184,527 acres
```

### Top Districts
You'll see districts like:
- Ahmednagar
- Sangli
- Pune
- Solapur
- Nashik
- Satara
- Kolhapur
- Aurangabad
- Mumbai

### Top Crops
You'll see crops like:
- Okra
- Pomegranate
- Sunflower
- Wheat
- Tur (Pigeon Pea)
- Mango
- Groundnut
- And more...

## 🔄 Auto-Update System

The Knowledge Graph automatically updates every hour with:
- New farmers who register through the system
- Updated crop information
- Latest statistics

You can also click the "🔄 Refresh Data" button on the page to manually reload.

## 🧪 Quick Test

Run this command to verify the data:
```bash
curl -s "https://kisaanmitra-knowledge-graph.s3.ap-south-1.amazonaws.com/knowledge_graph_dummy_data.json" | \
  python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Total Farmers: {d[\"metadata\"][\"total_farmers\"]}')"
```

Expected output: `Total Farmers: 10006`

## ❓ Still Seeing Old Data?

If you still see only 6 farmers after hard refresh:

1. **Clear ALL browser data** for the site
2. **Try a different browser** (Chrome, Firefox, Safari)
3. **Use incognito mode** - this always works
4. **Wait 2-3 minutes** for CloudFront cache to fully clear
5. **Check on mobile** - sometimes desktop caches more aggressively

## 📱 Mobile Users

On mobile, browser cache is very persistent:
1. Go to browser settings
2. Clear cache and cookies
3. Or use incognito/private mode
4. Or try a different browser app

## ✅ Verification Checklist

- [ ] Opened KG URL
- [ ] Performed hard refresh (Ctrl+Shift+R)
- [ ] See "10,006" in Total Farmers
- [ ] See multiple districts listed
- [ ] See "Last Updated" timestamp
- [ ] Can click "Refresh Data" button

## 🎯 Summary

**What was fixed:**
- Lambda now merges 10k dummy farmers + real farmers
- Dashboard loads live data from S3
- Auto-updates hourly
- Cache headers set to no-cache

**What you need to do:**
- Hard refresh your browser (Ctrl+Shift+R)
- Or use incognito mode
- That's it!

**Current Status:**
- ✅ Lambda deployed and working
- ✅ Data file updated (3.9 MB)
- ✅ Dashboard deployed
- ✅ CloudFront cache cleared
- ✅ All 10,006 farmers visible

## 🚀 Ready to View!

Just open the URL and hard refresh. You should now see all 10,006 farmers with complete statistics!

**Last Updated:** March 8, 2026 - 21:56 IST
