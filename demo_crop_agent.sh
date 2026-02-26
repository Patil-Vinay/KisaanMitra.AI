#!/bin/bash

# Demo Crop Agent - Shows WhatsApp-style responses

echo "🌾 CROP AGENT DEMO"
echo "=================="
echo ""

# Simulate farmer sending image
echo "👨‍🌾 Farmer: [Sends crop image]"
echo ""
sleep 1

# Show analysis message
echo "🤖 Crop Agent:"
echo "🔍 आपकी फसल की तस्वीर का विश्लेषण कर रहे हैं, कृपया प्रतीक्षा करें..."
echo ""
sleep 2

# Run actual crop engine test
python3 << 'EOF'
import sys
sys.path.insert(0, 'src/crop_agent')
from crop_health_api import analyze_crop_image, format_crop_result
from dotenv import load_dotenv

load_dotenv('.env')

# Test with actual image
with open('assets/test_images/2.jpg', 'rb') as f:
    image_bytes = f.read()

result = analyze_crop_image(image_bytes, latitude=18.5204, longitude=73.8567)
formatted = format_crop_result(result, language="hi")

print("🤖 Crop Agent:")
print(formatted)
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
