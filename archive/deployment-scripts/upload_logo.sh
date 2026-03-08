#!/bin/bash

echo "📤 Uploading KisaanMitra Logo..."

# Check if logo exists
if [ ! -f "demo/kisaanmitra-logo.png" ]; then
    echo "❌ Error: demo/kisaanmitra-logo.png not found!"
    echo ""
    echo "Please save your logo image as: demo/kisaanmitra-logo.png"
    echo "Then run this script again."
    exit 1
fi

# Upload logo to S3
echo "Uploading logo to S3..."
aws s3 cp demo/kisaanmitra-logo.png s3://kisaanmitra-web-demo-1772974554/ \
    --content-type "image/png" \
    --region ap-south-1

# Upload updated HTML
echo "Uploading updated web chat..."
aws s3 cp demo/web-chat-demo.html s3://kisaanmitra-web-demo-1772974554/index.html \
    --content-type "text/html" \
    --region ap-south-1

echo ""
echo "✅ Upload complete!"
echo ""
echo "🌐 View your demo at:"
echo "   http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com"
echo ""
echo "Your logo will now appear in the header!"
