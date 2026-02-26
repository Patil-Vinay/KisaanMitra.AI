#!/bin/bash

# Demo Market Agent - Shows WhatsApp-style responses

echo "📊 MARKET AGENT DEMO"
echo "===================="
echo ""

# Simulate farmer query
echo "👨‍🌾 Farmer: गेहूं का भाव क्या है?"
echo ""
sleep 1

# Run market agent
python3 << 'EOF'
import sys
sys.path.insert(0, 'src/market_agent')
from market_agent import get_crop_recommendation, analyze_price_trend, format_market_response

# Simulate market data
market_data = [
    {"market": "Pune", "modal_price": "2500"},
    {"market": "Mumbai", "modal_price": "2480"},
    {"market": "Nashik", "modal_price": "2420"}
]

trend = analyze_price_trend(market_data)
response = format_market_response("wheat", market_data, trend)

print("🤖 Market Agent:")
print(response)
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Second query
echo "👨‍🌾 Farmer: अभी कौन सी फसल लगाऊं?"
echo ""
sleep 1

python3 << 'EOF'
import sys
sys.path.insert(0, 'src/market_agent')
from market_agent import get_crop_recommendation

crops = get_crop_recommendation("Pune", "kharif")

print("🤖 Market Agent:")
print("*🌾 Recommended Crops (Kharif Season)*\n")
for i, crop in enumerate(crops, 1):
    print(f"{i}. {crop.title()}")
print("\n💡 Choose based on your soil type and water availability")
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
