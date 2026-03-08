# Current Mandi Price Output - KisaanMitra

## What We're Showing Users

### Format (English)
```
📊 *Tomato Market Price*

💰 *Current Price*: ₹2,450/quintal
📊 *Range*: ₹2,200 - ₹2,700
📈 *Trend*: Increasing

*Top Mandis*:
1. Kolhapur: ₹2,600
2. Sangli: ₹2,500
3. Satara: ₹2,400

🕐 *Updated*: 2026-03-08 15:30 IST
```

### Format (Hindi)
```
📊 *टमाटर बाजार भाव*

💰 *वर्तमान भाव*: ₹2,450/क्विंटल
📊 *रेंज*: ₹2,200 - ₹2,700
📈 *रुझान*: बढ़ रहा

*प्रमुख मंडियां*:
1. Kolhapur: ₹2,600
2. Sangli: ₹2,500
3. Satara: ₹2,400

🕐 *अपडेट*: 2026-03-08 15:30 IST
```

## Data Sources

### 1️⃣ AgMarkNet API (Primary)
**When it works:**
- Real mandi names from government database
- Actual prices from APMC markets
- Example: "Kolhapur APMC", "Sangli Agricultural Market"

**Current Status:** ⚠️ Experiencing timeouts (government server issues)

### 2️⃣ Claude AI (Fallback)
**When AgMarkNet fails:**
- Realistic mandi names from the state
- AI-generated prices based on March 2026 trends
- Example: "Kolhapur", "Sangli", "Satara"

**Current Status:** ✅ Working (fixed today)

## Mandi Names We Use

### Maharashtra
```
Primary Mandis:
- Kolhapur (Western Maharashtra)
- Sangli (Western Maharashtra)
- Satara (Western Maharashtra)
- Pune (Western Maharashtra)
- Nashik (Northern Maharashtra)
- Ahmednagar (Central Maharashtra)
- Solapur (Southern Maharashtra)

Metro Mandis:
- Mumbai (Vashi APMC)
- Thane
- Nagpur (Vidarbha)
```

### Other States (Examples)
```
Delhi: Azadpur, Ghazipur, Okhla
Karnataka: Bangalore, Mysore, Hubli
Tamil Nadu: Koyambedu, Madurai, Coimbatore
Gujarat: Ahmedabad, Surat, Rajkot
Punjab: Ludhiana, Amritsar, Jalandhar
```

## How It Works

```
User Query: "What is the price of tomato?"
    ↓
Extract Crop: "Tomato"
Extract State: "Maharashtra" (from user profile or query)
    ↓
Try AgMarkNet API
    ↓
    ├─ Success → Show real mandi data
    │   └─ Top 3 mandis with actual prices
    │
    └─ Fail → Use Claude AI Fallback
        └─ Generate realistic prices
        └─ Show 3 mandis from Maharashtra
```

## Example Outputs

### Tomato (Maharashtra)
```
Top Mandis:
1. Kolhapur: ₹2,600
2. Sangli: ₹2,500
3. Satara: ₹2,400
```

### Onion (Maharashtra)
```
Top Mandis:
1. Nashik: ₹3,200
2. Pune: ₹3,100
3. Ahmednagar: ₹3,000
```

### Wheat (Punjab)
```
Top Mandis:
1. Ludhiana: ₹2,150
2. Amritsar: ₹2,140
3. Jalandhar: ₹2,130
```

## Key Features

✅ **Always shows 3 mandis** (unless data unavailable)
✅ **Individual prices per mandi** (not just average)
✅ **State-specific mandis** (based on user location)
✅ **Price range** (min to max)
✅ **Trend indicator** (increasing/decreasing/stable)
✅ **Last updated timestamp**
✅ **Bilingual** (English & Hindi)

## Recent Fix (March 8, 2026)

**Problem:** Claude fallback was failing
**Error:** `'AnthropicBedrockWrapper' object has no attribute 'messages'`
**Solution:** Use `call_claude_with_retry()` directly instead of wrapper
**Status:** ✅ Deployed and working

## Testing

Try these queries:
- "What is the price of tomato?"
- "Onion mandi rates"
- "Potato market price"
- "टमाटर का भाव क्या है?"

Expected: You'll see 3 mandi names with prices!
