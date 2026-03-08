#!/bin/bash

echo "🎨 Uploading KisaanMitra.AI Logo..."

# Check if logo exists
if [ ! -f "demo/kisaanmitra-logo.png" ]; then
    echo "❌ Error: demo/kisaanmitra-logo.png not found!"
    echo ""
    echo "Please save your logo image as: demo/kisaanmitra-logo.png"
    echo "Then run this script again."
    exit 1
fi

# Upload logo to S3
echo "📤 Uploading to S3..."
aws s3 cp demo/kisaanmitra-logo.png s3://kisaanmitra-web-demo-1772974554/kisaanmitra-logo.png \
    --content-type "image/png" \
    --region ap-south-1 \
    --acl public-read

# Also commit to GitHub
echo "📦 Committing to GitHub..."
git add demo/kisaanmitra-logo.png
git commit -m "Add KisaanMitra.AI logo"
git push

echo ""
echo "✅ Logo uploaded successfully!"
echo ""
echo "🌐 Logo URL:"
echo "   S3: https://kisaanmitra-web-demo-1772974554.s3.ap-south-1.amazonaws.com/kisaanmitra-logo.png"
echo "   GitHub: https://raw.githubusercontent.com/parth-nikam/KisaanMitra.AI/main/demo/kisaanmitra-logo.png"
echo ""
echo "🎯 Web Demo:"
echo "   http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com"
echo ""
echo "Refresh the page (Ctrl+F5) to see your logo!"
