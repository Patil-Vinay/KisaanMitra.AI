# 👥 KisaanMitra - All Registered Users

## Total Users: 3

---

## User 1: Vinay Patil
- **Phone:** +91 9000000001
- **Location:** Nandani, Sangli, Maharashtra
- **Current Crops:** Sugarcane
- **Past Crops:** Rice, Soybean, Sugarcane
- **Land:** 50 acres
- **Experience:** 15 years
- **Soil Type:** Black Cotton Soil
- **Water Source:** Drip Irrigation
- **Challenges:** Pest infestations
- **Status:** ✅ Profile Complete
- **Registered:** March 2, 2026

### Profile Summary
Experienced farmer with 50 acres of land in Sangli district, specializing in sugarcane cultivation. Uses modern drip irrigation and has been farming for 15 years.

---

## User 2: Aditya
- **Phone:** +91 9000000003
- **Location:** Alibaug, Mumbai, Maharashtra
- **Current Crops:** Mango
- **Land:** 5 acres
- **Status:** ✅ Profile Complete
- **Registered:** March 2026

### Profile Summary
Mango farmer with 5 acres in Alibaug, Mumbai district. Focused on fruit cultivation.

---

## User 3: Parth Nikam
- **Phone:** +91 9000000002
- **Location:** Nandani, Sangli, Maharashtra
- **Current Crops:** Sugarcane
- **Past Crops:** Rice, Wheat, Sugarcane
- **Land:** 20 acres
- **Experience:** 10 years
- **Soil Type:** Black Cotton Soil
- **Water Source:** Drip Irrigation
- **Challenges:** Water management, Market price fluctuations
- **Status:** ✅ Profile Complete
- **Registered:** March 1, 2026

### Profile Summary
Experienced sugarcane farmer with 20 acres in Sangli district. Uses drip irrigation and has 10 years of farming experience.

---

## Geographic Distribution

### By District
- **Sangli:** 2 users (Vinay Patil, Parth Nikam)
- **Mumbai:** 1 user (Aditya)

### By Village
- **Nandani, Sangli:** 2 users
- **Alibaug, Mumbai:** 1 user

---

## Crop Distribution

### Current Crops
- **Sugarcane:** 2 farmers (66.7%)
- **Mango:** 1 farmer (33.3%)

### Total Land Under Cultivation
- **Total:** 75 acres
- **Average:** 25 acres per farmer
- **Range:** 5-50 acres

---

## Farming Experience

- **Vinay Patil:** 15 years
- **Parth Nikam:** 10 years
- **Aditya:** Not specified

**Average Experience:** 12.5 years (among those who specified)

---

## Technology Adoption

### Irrigation Methods
- **Drip Irrigation:** 2 farmers (Vinay, Parth)
- **Not specified:** 1 farmer

### Soil Types
- **Black Cotton Soil:** 2 farmers (Vinay, Parth)
- **Not specified:** 1 farmer

---

## Common Challenges

1. **Pest Infestations** (Vinay Patil)
2. **Water Management** (Parth Nikam)
3. **Market Price Fluctuations** (Parth Nikam)

---

## User Engagement

### Profile Completion
- **Complete Profiles:** 3/3 (100%)
- **All users have completed onboarding**

### Registration Timeline
- **March 1, 2026:** Parth Nikam
- **March 2, 2026:** Vinay Patil, Aditya

---

## Test Users for Demo

### Primary Test User
**Parth Nikam** - +91 9000000002
- Most active user
- Complete profile with detailed information
- Sugarcane farmer in Sangli

### Secondary Test User
**Vinay Patil** - +91 9000000001
- Large-scale farmer (50 acres)
- Experienced (15 years)
- Also in Sangli district

### Additional Test User
**Aditya** - +91 9000000003
- Different crop (Mango)
- Different location (Mumbai)
- Smaller farm (5 acres)

---

## Quick Commands

### List All Users
```bash
./scripts/list_all_users.sh
```

### Get User Count
```bash
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --select COUNT
```

### Get Specific User
```bash
aws dynamodb get-item \
    --table-name kisaanmitra-farmer-profiles \
    --key '{"user_id": {"S": "919000000002"}}' \
    --region ap-south-1
```

### Export All Users to JSON
```bash
aws dynamodb scan \
    --table-name kisaanmitra-farmer-profiles \
    --region ap-south-1 \
    --output json > all_users.json
```

---

## Dashboard Access

### Streamlit Dashboard
View all users in the dashboard:
```bash
cd dashboard
streamlit run streamlit_app.py
```

Then navigate to the "Users" page to see:
- Complete user list
- Profile details
- Export to CSV
- Real-time data from DynamoDB

### Knowledge Graph
View user relationships:
```
http://kisaanmitra-knowledge-graph.s3-website.ap-south-1.amazonaws.com
```

---

## User Statistics

### Demographics
- **Total Farmers:** 3
- **Total Land:** 75 acres
- **Average Land:** 25 acres
- **Districts Covered:** 2 (Sangli, Mumbai)
- **Villages Covered:** 2 (Nandani, Alibaug)

### Crop Diversity
- **Crop Types:** 2 (Sugarcane, Mango)
- **Sugarcane Farmers:** 2 (66.7%)
- **Fruit Farmers:** 1 (33.3%)

### Technology Adoption
- **Drip Irrigation:** 66.7%
- **Profile Completion:** 100%

---

## Contact Information

### For Testing/Demo

**Primary Contact:**
- Name: Parth Nikam
- Phone: +91 9000000002
- WhatsApp: Available

**Secondary Contact:**
- Name: Vinay Patil
- Phone: +91 9000000001
- WhatsApp: Available

**Additional Contact:**
- Name: Aditya
- Phone: +91 9000000003
- WhatsApp: Available

---

## Notes

- All users have completed the onboarding process
- All profiles are verified and complete
- Users are from Maharashtra state
- Mix of large-scale (50 acres) and small-scale (5 acres) farmers
- Good representation of different crops and locations
- Active WhatsApp engagement

---

**Last Updated:** March 8, 2026  
**Data Source:** DynamoDB (kisaanmitra-farmer-profiles)  
**Region:** ap-south-1