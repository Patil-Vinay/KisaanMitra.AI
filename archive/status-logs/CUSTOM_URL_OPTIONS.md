# Custom URL Options for KisaanMitra AI

## Current URL
```
https://d28gkw3jboipw5.cloudfront.net/
```

## Problem
The CloudFront URL is random and doesn't include "kisaan" or "ai" in it, making it hard to remember and share.

## Solutions

### Option 1: Purchase Custom Domain (Recommended for Production)
**Cost:** ~$12/year for `.ai` domain or ~$10/year for `.com`

**Steps:**
1. Purchase domain: `kisaanmitra.ai` or `kisaan.ai`
2. Add to Route 53
3. Get SSL certificate from ACM
4. Update CloudFront with custom domain
5. **Result:** `https://kisaanmitra.ai` or `https://kisaan.ai`

**Time:** 30 minutes
**Cost:** $10-15/year

### Option 2: Use URL Shortener (Free, Immediate)
**Cost:** Free

Use a service like:
- **bit.ly:** Create `bit.ly/kisaanai` → redirects to CloudFront
- **tinyurl.com:** Create `tinyurl.com/kisaanai` → redirects to CloudFront
- **rebrandly.com:** Create custom short URL

**Steps:**
1. Go to bit.ly or tinyurl.com
2. Enter CloudFront URL: `https://d28gkw3jboipw5.cloudfront.net/`
3. Create custom short URL: `kisaanai`
4. **Result:** `https://bit.ly/kisaanai` or `https://tinyurl.com/kisaanai`

**Time:** 2 minutes
**Cost:** Free

### Option 3: AWS Amplify (Not Ideal)
**Cost:** Free

Amplify gives you: `https://main.d3coqjwjjdb218.amplifyapp.com`
- Still has random ID
- Doesn't include "kisaan"
- Not better than CloudFront URL

### Option 4: GitHub Pages (Free, but Limited)
**Cost:** Free

Create: `https://parth-nikam.github.io/kisaanmitra/`
- Includes your GitHub username
- Not as clean as custom domain
- Requires GitHub Pages setup

## Recommended Solution

### For Hackathon/Demo (Immediate):
**Use URL Shortener (Option 2)**

1. Go to https://bit.ly
2. Sign up (free)
3. Create short link:
   - Long URL: `https://d28gkw3jboipw5.cloudfront.net/`
   - Custom back-half: `kisaanai`
4. Get: `https://bit.ly/kisaanai`

**Benefits:**
- ✅ Free
- ✅ Immediate (2 minutes)
- ✅ Easy to remember
- ✅ Easy to share
- ✅ Includes "kisaan"

### For Production (Long-term):
**Purchase Custom Domain (Option 1)**

Buy `kisaanmitra.ai` or `kisaan.ai` and configure with Route 53.

## Quick Setup: URL Shortener

### Using bit.ly:
```
1. Visit: https://bit.ly
2. Sign up (free account)
3. Click "Create"
4. Paste: https://d28gkw3jboipw5.cloudfront.net/
5. Customize: kisaanai
6. Save
7. Share: https://bit.ly/kisaanai
```

### Using TinyURL:
```
1. Visit: https://tinyurl.com
2. Paste: https://d28gkw3jboipw5.cloudfront.net/
3. Customize: kisaanai
4. Create
5. Share: https://tinyurl.com/kisaanai
```

## Updated URLs Document

Once you create the short URL, update all documentation to use:

**Primary URL:** `https://bit.ly/kisaanai` (or your chosen short URL)
**Direct URL:** `https://d28gkw3jboipw5.cloudfront.net/` (backup)

## Cost Comparison

| Option | Cost | Time | URL Example |
|--------|------|------|-------------|
| URL Shortener | Free | 2 min | bit.ly/kisaanai |
| Custom Domain | $10-15/year | 30 min | kisaanmitra.ai |
| CloudFront (current) | Free | 0 min | d28gkw3jboipw5.cloudfront.net |
| Amplify | Free | 15 min | d3coqjwjjdb218.amplifyapp.com |

## Recommendation

**For your hackathon submission, use a URL shortener immediately.** It's free, takes 2 minutes, and gives you a clean, memorable URL like `bit.ly/kisaanai`.

For production after the hackathon, purchase a custom domain like `kisaanmitra.ai` for a professional look.

**Next Step:** Create a bit.ly account and set up `bit.ly/kisaanai` pointing to your CloudFront URL.
