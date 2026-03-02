# Hyperlocal Disease Alert System - Live Demo

## 🎯 Demo Scenario: Vinay Reports Disease → Parth Gets Alert

### Setup:
- **Vinay**: Farmer in Nandani village, Sangli (Phone: +91-XXXX-VINAY)
- **Parth**: Farmer in Nandani village, Sangli (Phone: +91-9673-109542)
- **Distance**: Both in same village (~2 km apart)
- **Crop**: Both growing tomatoes

---

## 📱 Step 1: Vinay Sends Diseased Crop Photo

### Vinay's Action:
```
1. Open WhatsApp chat with KisaanMitra
2. Send a photo of tomato plant with late blight disease
   (Dark spots on leaves, wilting)
```

### Vinay Receives (within 3 seconds):
```
🔍 Disease Detection Result

Disease Identified: Tomato Late Blight
Confidence: 94%
Severity: High ⚠️

🎯 Recommended Treatments:

1. Mancozeb 75% WP
   • Dosage: 2.5g per liter
   • Application: Spray every 7-10 days
   • Cost: ₹500-800
   • Success Rate: 85%

2. Copper Oxychloride 50% WP
   • Dosage: 3g per liter
   • Application: Preventive spray
   • Cost: ₹400-600
   • Success Rate: 75%

3. Metalaxyl + Mancozeb
   • Dosage: 2g per liter
   • Application: Curative spray
   • Cost: ₹800-1200
   • Success Rate: 90%

💡 Immediate Actions:
• Remove and destroy infected leaves
• Improve air circulation between plants
• Avoid overhead watering
• Apply fungicide within 24 hours

🌾 Prevention Tips:
• Maintain 60cm plant spacing
• Use drip irrigation
• Apply preventive spray every 15 days
• Monitor daily for early symptoms

📊 Disease Report:
• Report ID: DR-2026-03-02-001
• Location: Nandani, Sangli
• Crop: Tomato
• Severity: High
• Status: Active

📢 Alert sent to 23 nearby farmers in 5km radius

⬅ Back | 🏠 Home | ❌ Cancel
```

---

## 🚨 Step 2: Parth Receives Automatic Alert (Simultaneously)

### Parth Receives (within 5 seconds of Vinay's report):
```
⚠️ DISEASE ALERT - YOUR AREA

📍 Location: Nandani village, Sangli
🌾 Crop: Tomato
🦠 Disease: Late Blight
📊 Severity: HIGH ⚠️
📏 Distance: 2 km from your farm

Reported by: Vinay Kumar (fellow farmer)
Time: 2 minutes ago

🎯 IMMEDIATE ACTION REQUIRED:

1. ✅ Inspect your tomato crop TODAY
2. 🔍 Look for these symptoms:
   • Dark brown/black spots on leaves
   • White fuzzy growth on leaf undersides
   • Wilting and yellowing
   • Stem lesions

3. 💊 Apply preventive treatment NOW:
   • Mancozeb 75% WP @ 2.5g/liter
   • Spray thoroughly on all plants
   • Repeat every 7 days

4. 🗑️ Remove any infected plants immediately

💊 RECOMMENDED TREATMENT:

Primary: Mancozeb 75% WP
• Dosage: 2.5g per liter water
• Coverage: 200 liters per acre
• Frequency: Every 7-10 days
• Cost: ₹500-800 per acre
• Where to buy: Local agri shop or cooperative

Alternative: Copper Oxychloride 50% WP
• Dosage: 3g per liter water
• Cost: ₹400-600 per acre

📊 AREA STATUS:

• Total cases: 1 confirmed
• Affected radius: 5 km
• Farmers alerted: 23
• Risk level: HIGH ⚠️
• Weather: Humid conditions favor spread

🌡️ WEATHER ALERT:
High humidity (75%) and moderate temperature (28°C) 
are ideal for disease spread. Take action immediately!

💡 PREVENTION TIPS:

• Avoid overhead watering (use drip irrigation)
• Improve air circulation (prune lower leaves)
• Don't work in wet fields
• Disinfect tools after use
• Monitor daily for next 7 days

📞 NEED HELP?
Reply with "treatment details" for more information
or call Kisan Helpline: 1800-180-1551

🔔 You're receiving this because:
• You're growing tomato in Nandani village
• Disease detected within 5km of your farm
• Early warning can save your crop

Stay vigilant! Early detection saves crops. 🌾

⬅ Back | 🏠 Home
```

---

## 📊 Step 3: System Behavior (Behind the Scenes)

### What Happens Automatically:

1. **Disease Detection** (Vinay's photo)
   - AI analyzes image using AWS Bedrock
   - Identifies disease: Late Blight
   - Confidence: 94%
   - Severity: High

2. **Profile Lookup** (Vinay)
   - User: Vinay Kumar
   - Village: Nandani
   - District: Sangli
   - Crop: Tomato
   - Land: 5 acres

3. **Hyperlocal Alert Trigger**
   ```python
   report_id, farmers_to_alert = hyperlocal_tracker.report_disease(
       user_id="vinay_phone",
       village="Nandani",
       district="Sangli",
       crop="tomato",
       disease_name="Late Blight",
       severity="high",
       symptoms="dark spots, wilting",
       send_alerts=True
   )
   ```

4. **Nearby Farmer Search** (5km radius)
   - Query DynamoDB for farmers in Nandani, Sangli
   - Filter by crop: tomato
   - Calculate distance: < 5km
   - Found: 23 farmers including Parth

5. **Alert Distribution**
   - Send WhatsApp message to all 23 farmers
   - Include: disease details, treatment, prevention
   - Personalized with distance from outbreak
   - Add weather context

6. **Database Updates**
   - Save disease report in DynamoDB
   - Update disease tracking table
   - Log alert distribution
   - Track acknowledgments

---

## 🎬 Live Demo Script (For Evaluators)

### Preparation (Before Demo):
1. Ensure both Parth and Vinay are registered
2. Both should have same village: Nandani, Sangli
3. Both should have tomato in their crops
4. Have a diseased tomato leaf photo ready

### Demo Steps (2 minutes):

**Step 1** (30 seconds):
- Show Vinay's WhatsApp chat
- Send diseased crop photo
- Wait for AI analysis

**Step 2** (30 seconds):
- Show Vinay receives disease detection result
- Point out "Alert sent to 23 farmers" message

**Step 3** (60 seconds):
- Switch to Parth's WhatsApp
- Show alert received automatically
- Highlight key features:
  - Distance: 2 km
  - Reporter name: Vinay Kumar
  - Immediate action steps
  - Treatment recommendations
  - Area status

**Key Talking Points:**
- ✅ Automatic community protection
- ✅ Real-time disease tracking
- ✅ Location-aware (5km radius)
- ✅ Crop-specific alerts
- ✅ Actionable treatment advice
- ✅ No manual intervention needed

---

## 🧪 Test Commands

### For Vinay (Disease Reporter):
```
1. Send photo of diseased tomato plant
   Expected: Disease detection + "Alert sent to X farmers"

2. Check logs:
   aws logs tail /aws/lambda/whatsapp-llama-bot --follow | grep "Hyperlocal"
   Expected: "Sent X disease alerts"
```

### For Parth (Alert Receiver):
```
1. Wait for automatic alert (within 5 seconds)
   Expected: Detailed disease alert message

2. Reply: "treatment details"
   Expected: More detailed treatment information

3. Reply: "show me nearby cases"
   Expected: Map of disease reports in area
```

---

## 📊 Expected Database Entries

### Disease Reports Table:
```json
{
  "report_id": "DR-2026-03-02-001",
  "user_id": "vinay_phone",
  "village": "Nandani",
  "district": "Sangli",
  "crop": "tomato",
  "disease_name": "Late Blight",
  "severity": "high",
  "confidence": 94,
  "symptoms": "dark spots, wilting",
  "timestamp": "2026-03-02T18:30:00Z",
  "location": {
    "lat": 16.8524,
    "lon": 74.5815
  },
  "alerts_sent": 23,
  "status": "active"
}
```

### Alert Log:
```json
{
  "alert_id": "AL-2026-03-02-001",
  "report_id": "DR-2026-03-02-001",
  "recipient_id": "919000000002",
  "recipient_name": "Parth Nikam",
  "distance_km": 2,
  "sent_at": "2026-03-02T18:30:05Z",
  "status": "delivered",
  "acknowledged": false
}
```

---

## 🎯 Demo Variations

### Variation 1: Multiple Reporters
```
1. Vinay reports Late Blight
2. Another farmer reports same disease 1 hour later
3. Parth receives updated alert: "2 cases now reported"
```

### Variation 2: Different Crops
```
1. Vinay reports tomato disease
2. Parth grows wheat (different crop)
3. Parth does NOT receive alert (crop-specific filtering)
```

### Variation 3: Distance Filter
```
1. Vinay in Nandani reports disease
2. Farmer in Pune (200km away) does NOT receive alert
3. Only farmers within 5km radius get alerts
```

### Variation 4: Severity Levels
```
Low Severity: "Monitor your crop, preventive spray recommended"
Medium Severity: "Inspect crop today, apply treatment if symptoms found"
High Severity: "IMMEDIATE ACTION REQUIRED, inspect and treat NOW"
```

---

## 🏆 Key Features Demonstrated

1. **Automatic Detection**: AI identifies disease from photo
2. **Community Protection**: Alerts sent to nearby farmers automatically
3. **Location-Aware**: Uses village/district from profiles
4. **Crop-Specific**: Only alerts farmers growing same crop
5. **Distance-Based**: 5km radius filtering
6. **Actionable**: Includes treatment, cost, prevention
7. **Real-Time**: Alerts sent within 5 seconds
8. **Contextual**: Includes weather, area status
9. **Scalable**: Can handle 1000+ farmers
10. **Zero Effort**: No manual reporting needed

---

## 📱 Quick Test (30 seconds)

**Vinay**: Send any tomato disease photo to KisaanMitra
**Parth**: Check WhatsApp - you'll receive alert automatically!

That's it! Community protection in action. 🚀🌾

---

## 🎤 Elevator Pitch

"When Vinay discovers a disease in his tomato crop and sends a photo to KisaanMitra, our AI not only diagnoses it instantly but automatically alerts 23 nearby farmers including Parth - all within 5 seconds. No app, no manual reporting, just WhatsApp. That's hyperlocal community intelligence powered by AWS."

---

**Demo Time**: 2 minutes
**Wow Factor**: 10/10 🌟
**Technical Complexity**: High (but looks simple!)
**Business Impact**: Prevents crop loss across entire communities
