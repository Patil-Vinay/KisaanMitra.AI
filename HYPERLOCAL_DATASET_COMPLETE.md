# Hyperlocal Knowledge Graph Dataset - Complete

## 📊 Dataset Overview

Successfully generated and deployed a comprehensive hyperlocal dataset for KisaanMitra.AI

### Statistics
- **Total Farmers:** 575
- **Districts:** 8 (Pune, Kolhapur, Nashik, Satara, Sangli, Solapur, Ahmednagar, Aurangabad)
- **Villages:** 54 (7-8 villages per district)
- **Unique Crops:** 24
- **Soil Types:** 6

## 🗺️ Hyperlocal Structure

### District → Village Hierarchy
```
Pune District
  ├── Baramati
  ├── Indapur
  ├── Malegaon
  ├── Shirur
  ├── Daund
  ├── Purandar
  ├── Bhor
  └── Velhe

Kolhapur District
  ├── Shahuwadi
  ├── Panhala
  ├── Radhanagari
  ├── Kagal
  ├── Hatkanangle
  ├── Shirol
  └── Karvir

... (6 more districts)
```

## 👨‍🌾 Farmer Data Fields

Each farmer has:
- **Name:** Indian first name + last name
- **Phone:** +91 format mobile number
- **District:** One of 8 Maharashtra districts
- **Village:** Specific village within district
- **Land Size:** 2-100 acres (varies by district)
- **Soil Type:** One of 6 soil types common in Maharashtra
  - Black Cotton Soil (Regur)
  - Red Soil
  - Laterite Soil
  - Alluvial Soil
  - Medium Black Soil
  - Shallow Black Soil
- **Crops Grown:** 1-4 crops per farmer (array)
- **Current Crop:** What they're growing right now
- **Current Crop Stage:** Sowing/Growing/Flowering/Harvesting/Post-Harvest
- **Experience:** 3-35 years
- **Success Rate:** 50-95% (based on experience)
- **Irrigation Method:** Drip/Sprinkler/Flood/Rainfed/Canal
- **Fertilizer Type:** Organic/Chemical/Mixed/Bio-fertilizer
- **Sowing Date:** Within last 6 months
- **Preferred Mandi:** District APMC

## 🌾 Crop Distribution

Top 10 crops by farmer count:
1. Gram - 60 farmers
2. Tur (Pigeon Pea) - 58 farmers
3. Orange - 55 farmers
4. Groundnut - 55 farmers
5. Pomegranate - 55 farmers
6. Soybean - 55 farmers
7. Wheat - 54 farmers
8. Sunflower - 53 farmers
9. Tomato - 53 farmers
10. Sugarcane - 51 farmers

## 🏛️ District Distribution

Farmers per district:
- Satara: 80
- Kolhapur: 78
- Solapur: 76
- Sangli: 75
- Pune: 72
- Ahmednagar: 69
- Aurangabad: 65
- Nashik: 60

## 🌱 Soil Type Distribution

- Red Soil: 109 farmers
- Shallow Black Soil: 99 farmers
- Black Cotton Soil (Regur): 98 farmers
- Laterite Soil: 95 farmers
- Alluvial Soil: 90 farmers
- Medium Black Soil: 84 farmers

## 🔧 Technical Implementation

### Files Updated
1. **demo/generate_large_dataset.py** - Dataset generation script
2. **demo/knowledge_graph_dummy_data.json** - 575 farmer records
3. **src/lambda/knowledge_graph_helper.py** - Added district functions
4. **dashboard/streamlit_app.py** - Updated KG page with district/village filters

### New Functions
- `get_district_farmers(district_name, crop_filter)` - Get farmers by district
- `get_all_districts()` - List all districts
- `get_all_villages()` - List all villages with districts

### Dashboard Features
- District and village dropdown filters
- Soil type distribution chart
- Current crop statistics
- Dynamic farmer count by location
- Export filtered data to CSV

## 🎯 Use Cases Enabled

1. **Hyperlocal Weather:** Use district for weather API calls
2. **Soil-Based Recommendations:** Suggest crops based on soil type
3. **Village Networking:** Connect farmers in same village
4. **District Analytics:** Compare performance across districts
5. **Crop Planning:** See what others are growing in same soil type
6. **Market Intelligence:** District-wise mandi prices

## 📱 WhatsApp Integration

The knowledge graph now supports:
- "Show me farmers in Baramati village"
- "Who grows sugarcane in Kolhapur district?"
- "Farmers with black cotton soil"
- "What crops are grown in Pune district?"

## 🚀 Deployment

Dataset deployed to:
- Lambda function: whatsapp-llama-bot
- Streamlit dashboard: localhost:8501
- Package size: ~50KB (compressed JSON)

## ✅ Validation

- All 575 farmers have valid phone numbers
- All have district + village
- All have soil type
- All have 1-4 crops
- All have current crop
- No duplicate phone numbers
- Realistic land sizes per district
- Experience-based success rates

## 📈 Future Enhancements

- Add GPS coordinates for villages
- Add elevation data
- Add water source information
- Add market distance
- Add cooperative membership
- Add insurance status
- Add loan information
