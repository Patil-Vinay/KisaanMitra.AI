# KisaanMitra Logo Upload Instructions

## Quick Upload

Save your logo image as `kisaanmitra-logo.png` in the `demo/` folder, then run:

```bash
# Upload logo to S3
aws s3 cp demo/kisaanmitra-logo.png s3://kisaanmitra-web-demo-1772974554/ --content-type "image/png" --region ap-south-1

# Upload updated HTML
aws s3 cp demo/web-chat-demo.html s3://kisaanmitra-web-demo-1772974554/index.html --content-type "text/html" --region ap-south-1
```

## What Changed

1. **Header Icon**: Now uses your KisaanMitra.AI logo image instead of emoji
2. **Title**: Updated to "KisaanMitra.AI" (with .AI)
3. **Fallback**: If logo fails to load, shows 🌾 emoji as backup
4. **Styling**: Logo fits perfectly in the rounded square with proper sizing

## Logo Specifications

- **File name**: `kisaanmitra-logo.png`
- **Recommended size**: 200x200px or larger (will be scaled to 56x56px)
- **Format**: PNG with transparent background (or JPG)
- **Location**: Same S3 bucket as the web demo

## After Upload

The logo will appear in:
- Web chat header (top left)
- Properly sized and styled with rounded corners
- Animated with subtle pulse effect

Your professional KisaanMitra.AI branding will be visible to all evaluators!
