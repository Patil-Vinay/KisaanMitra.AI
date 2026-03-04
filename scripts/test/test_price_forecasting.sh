#!/bin/bash

# Test Price Forecasting Feature
echo "🔮 Testing Price Forecasting System..."
echo ""

# Test 1: Forecast query in Hindi
echo "Test 1: गन्ने की कीमत अगले सप्ताह क्या होगी?"
curl -X POST https://graph.facebook.com/v17.0/YOUR_PHONE_ID/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "919000000002",
    "type": "text",
    "text": {
      "body": "गन्ने की कीमत अगले सप्ताह क्या होगी?"
    }
  }'

echo ""
echo "Test 2: What will be the price of sugarcane next week?"
echo ""
echo "✅ Tests sent! Check WhatsApp for responses."
