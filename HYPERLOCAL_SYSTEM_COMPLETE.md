# Hyperlocal Disease Tracking & Best Practices System

## Overview

The Hyperlocal System enables farmers to:
1. **See what diseases are affecting nearby farmers** in their village/district
2. **Learn what treatments worked** for other farmers
3. **Share and discover best practices** from their community

This creates a **community-driven knowledge base** where farmers help each other.

---

## Architecture

### DynamoDB Tables

1. **kisaanmitra-disease-reports**
   - Tracks disease reports by village
   - Fields: report_id, user_id, village, district, crop, disease_name, severity, symptoms, image_url, timestamp, status
   - Index: village-timestamp-index (query diseases by location and time)

2. **kisaanmitra-treatment-success**
   - Records successful treatments
   - Fields: success_id, report_id, user_id, disease_type, treatment_method, effectiveness_score (1-10), cost_rupees, duration_days, notes
   - Index: disease-effectiveness-index (find best treatments by disease)

3. **kisaanmitra-best-practices**
   - Community farming tips and techniques
   - Fields: practice_id, user_id, village, crop_type, category, title, description, season, upvotes
   - Index: crop-upvotes-index (find popular practices by crop)

---

## Setup Instructions

### 1. Create DynamoDB Tables

```bash
chmod +x infrastructure/setup_hyperlocal_tables.sh
bash infrastructure/setup_hyperlocal_tables.sh
```

This creates all 3 tables with proper indexes.

### 2. Seed Demo Data

```bash
cd demo
python3 seed_hyperlocal_data.py
```

This creates:
- 50+ disease reports across 5 villages
- 40+ successful treatment records
- 15+ community best practices
- Realistic data for rice, wheat, sugarcane, cotton, tomato

### 3. Deploy to Lambda

The hyperlocal module is automatically included in Lambda deployment:

```bash
cd src/lambda
./deploy_whatsapp.sh
```

---

## Features

### 1. Automatic Disease Reporting

When a farmer sends a crop image:
1. AI detects the disease
2. System automatically reports it to the hyperlocal database
3. Links it to farmer's village/district from their profile

```python
# Happens automatically after image analysis
hyperlocal_tracker.report_disease(
    user_id=from_number,
    village=village,
    district=district,
    crop=crop,
    disease_name=disease_name,
    severity=severity,
    symptoms=symptoms
)
```

### 2. Treatment Recommendations

After disease detection, farmers see:
- **What treatments worked** for other farmers with the same disease
- **Effectiveness scores** (1-10 rating)
- **Cost** in rupees
- **Duration** to resolve
- **Notes** from farmers who tried it

Example output:
```
💊 Successful Treatments for Blast Disease

Farmers in your area found these treatments effective:

1. Tricyclazole fungicide spray
   Effectiveness: 9/10 ⭐
   Cost: ₹800
   Duration: 14 days
   Note: Spray every 7 days, 2-3 applications

2. Carbendazim + Mancozeb
   Effectiveness: 8/10 ⭐
   Cost: ₹600
   Duration: 10 days
   Note: Mix both and spray in evening
```

### 3. Disease Alerts

Farmers get alerts if multiple farmers in their village report the same disease:

```
⚠️ Disease Alert in Nandani

In the last 7 days for sugarcane:

🔴 Red Rot: 3 farmers affected
🔴 Wilt Disease: 2 farmers affected

💡 Type 'treatment' to see what worked for others
```

### 4. Best Practices Discovery

Farmers can discover proven techniques from their community:

```python
# Get best practices for a crop
practices = hyperlocal_tracker.get_best_practices(
    crop_type="rice",
    category="pest_control",  # Optional filter
    min_upvotes=5
)
```

Categories:
- `pest_control` - Organic and chemical pest management
- `irrigation` - Water management techniques
- `fertilizer` - Soil nutrition methods
- `planting` - Sowing and planting techniques
- `harvesting` - Harvest timing and methods

### 5. Community Upvoting

Farmers can upvote practices that worked for them:

```python
hyperlocal_tracker.upvote_practice(practice_id)
```

Most upvoted practices appear first.

---

## API Reference

### HyperlocalDiseaseTracker Class

#### report_disease()
```python
report_id = hyperlocal_tracker.report_disease(
    user_id="919000000001",
    village="Nandani",
    district="Sangli",
    crop="sugarcane",
    disease_name="Red Rot",
    severity="high",  # low/medium/high
    symptoms="Reddish discoloration of stalks",
    image_url="s3://bucket/image.jpg"  # Optional
)
```

#### get_nearby_diseases()
```python
reports = hyperlocal_tracker.get_nearby_diseases(
    village="Nandani",
    district="Sangli",
    days=30,  # Look back period
    crop="sugarcane"  # Optional filter
)
```

Returns list of disease reports with all details.

#### record_treatment_success()
```python
success_id = hyperlocal_tracker.record_treatment_success(
    report_id="abc-123",
    user_id="919000000001",
    disease_name="Red Rot",
    treatment_method="Copper oxychloride spray",
    effectiveness_score=8,  # 1-10
    cost=500,  # Rupees
    duration_days=14,
    notes="Preventive spray before monsoon"
)
```

#### get_successful_treatments()
```python
treatments = hyperlocal_tracker.get_successful_treatments(
    disease_name="Red Rot",
    min_score=7  # Minimum effectiveness
)
```

Returns treatments sorted by effectiveness (highest first).

#### add_best_practice()
```python
practice_id = hyperlocal_tracker.add_best_practice(
    user_id="919000000001",
    village="Nandani",
    crop_type="rice",
    category="pest_control",
    title="Neem Cake Application",
    description="Mix 250kg neem cake per acre...",
    season="kharif"  # Optional
)
```

#### get_best_practices()
```python
practices = hyperlocal_tracker.get_best_practices(
    crop_type="rice",
    category="pest_control",  # Optional
    min_upvotes=5
)
```

Returns practices sorted by upvotes (most popular first).

#### Format Functions

```python
# Disease alert message
msg = hyperlocal_tracker.format_disease_alert(
    village="Nandani",
    crop="sugarcane",
    language='english'  # or 'hindi'
)

# Treatment recommendations
msg = hyperlocal_tracker.format_treatment_recommendations(
    disease_name="Red Rot",
    language='english'
)
```

---

## Integration with WhatsApp Bot

### Automatic Integration

The system is automatically integrated into the disease detection flow:

1. Farmer sends crop image
2. AI detects disease
3. **System reports disease to hyperlocal DB**
4. **System fetches successful treatments from nearby farmers**
5. **Response includes both AI diagnosis + community treatments**

### Manual Queries

Farmers can also ask:
- "What diseases are affecting farmers in my village?"
- "Show me treatments for red rot"
- "Best practices for rice farming"

The AI router will detect these queries and use hyperlocal data.

---

## Data Privacy

- User IDs are phone numbers (already shared via WhatsApp)
- Village/district info comes from onboarding profile
- No personal information beyond what's in profile
- Farmers can see aggregated data (disease counts, treatment success rates)
- Individual farmer names are NOT shared in disease reports

---

## Benefits

### For Individual Farmers
- ✅ Learn from neighbors' experiences
- ✅ Save money by using proven treatments
- ✅ Get early warnings about disease outbreaks
- ✅ Discover local best practices

### For Community
- ✅ Build collective knowledge base
- ✅ Reduce crop losses through early detection
- ✅ Share successful innovations
- ✅ Strengthen farmer networks

### For System
- ✅ Improve AI recommendations with real-world data
- ✅ Track disease patterns geographically
- ✅ Identify most effective treatments
- ✅ Validate agricultural advice

---

## Future Enhancements

1. **Expert Verification**
   - Agricultural experts can verify treatments
   - Verified treatments get a ✓ badge

2. **Seasonal Patterns**
   - Track which diseases appear in which seasons
   - Predictive alerts before disease season

3. **Success Rate Tracking**
   - Track how many farmers tried each treatment
   - Calculate actual success rate

4. **Photo Gallery**
   - Store disease images for visual reference
   - "Does your crop look like this?"

5. **Farmer Reputation**
   - Farmers who share helpful practices get reputation points
   - Top contributors get recognition

6. **District-Level Analytics**
   - Agricultural officers see disease trends
   - Identify areas needing intervention

---

## Testing

### Test Disease Report
```python
from disease_tracker import hyperlocal_tracker

report_id = hyperlocal_tracker.report_disease(
    user_id="919000000001",
    village="Nandani",
    district="Sangli",
    crop="sugarcane",
    disease_name="Red Rot",
    severity="high",
    symptoms="Reddish discoloration"
)
print(f"Report ID: {report_id}")
```

### Test Treatment Query
```python
treatments = hyperlocal_tracker.get_successful_treatments("Red Rot")
for t in treatments:
    print(f"{t['treatment_method']}: {t['effectiveness_score']}/10")
```

### Test Best Practices
```python
practices = hyperlocal_tracker.get_best_practices("rice", "pest_control")
for p in practices:
    print(f"{p['title']} ({p['upvotes']} upvotes)")
```

---

## Monitoring

### Check Disease Reports
```bash
aws dynamodb scan --table-name kisaanmitra-disease-reports --region ap-south-1 | jq '.Items | length'
```

### Check Treatment Success
```bash
aws dynamodb scan --table-name kisaanmitra-treatment-success --region ap-south-1 | jq '.Items | length'
```

### Check Best Practices
```bash
aws dynamodb scan --table-name kisaanmitra-best-practices --region ap-south-1 | jq '.Items | length'
```

---

## Cost Estimate

DynamoDB costs (with 5 RCU/WCU per table):
- 3 tables × $0.00065/hour = **$1.40/month**
- Storage: First 25GB free
- Queries: First 25 RCU/WCU free

**Total: ~$1-2/month** for hyperlocal system

---

## Support

For issues:
1. Check CloudWatch logs for hyperlocal errors
2. Verify tables exist and have correct indexes
3. Test with seed data first
4. Check IAM permissions for DynamoDB access

---

## Summary

The Hyperlocal System transforms KisaanMitra from an individual AI assistant into a **community-powered platform** where farmers learn from each other's real experiences. This creates a virtuous cycle:

1. Farmer reports disease (via image)
2. Gets AI diagnosis + community treatments
3. Tries a treatment
4. Reports success back
5. Helps next farmer with same disease

**Result: Collective intelligence that improves over time!** 🌾
