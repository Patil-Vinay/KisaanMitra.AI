## KisaanMitra Onboarding & Knowledge Graph - Quick Start

### What's New?

1. **Automated Farmer Onboarding** - New users are automatically detected and guided through registration
2. **Village Knowledge Graph** - Stores farmer relationships in Amazon Neptune (or local fallback)
3. **Streamlit Dashboard** - Real-time visualization of farmer data and village statistics

### Quick Setup (5 minutes)

#### Step 1: Create DynamoDB Tables

```bash
cd infrastructure
chmod +x setup_onboarding_tables.sh
./setup_onboarding_tables.sh
```

This creates:
- `kisaanmitra-onboarding` - Tracks onboarding state
- `kisaanmitra-user-profiles` - Stores farmer profiles

#### Step 2: Deploy Lambda with Onboarding

```bash
cd ../src/lambda
chmod +x deploy_with_onboarding.sh

# Set environment variables
export WHATSAPP_TOKEN="your_token"
export PHONE_NUMBER_ID="your_phone_id"
export CROP_HEALTH_API_KEY="your_crop_api_key"
export AGMARKNET_API_KEY="your_agmarknet_key"

# Deploy
./deploy_with_onboarding.sh
```

#### Step 3: Test Onboarding

Send "Hi" to your WhatsApp Business number. You'll see:

```
🙏 नमस्ते! KisaanMitra में आपका स्वागत है!

मैं आपका कृषि सहायक हूं। मैं आपकी मदद कर सकता हूं:
🌾 फसल रोग पहचान
📊 बाजार भाव
💰 बजट योजना

पहले मुझे आपके बारे में कुछ जानकारी चाहिए।

*आपका नाम क्या है?*
```

Follow the prompts to complete registration.

#### Step 4: View Dashboard

```bash
cd ../../dashboard
chmod +x run_dashboard.sh
./run_dashboard.sh
```

Dashboard opens at `http://localhost:8501`

### What You'll See

**Dashboard Features:**
- 📊 Overview metrics (farmers, villages, crops, land)
- 🕸️ Interactive network graph showing relationships
- 🏘️ Village-wise breakdown
- 👨‍🌾 Farmer profiles table with CSV export
- 🌾 Crop distribution charts
- 📈 Registration timeline

### Onboarding Flow

```
User: Hi
Bot: आपका नाम क्या है?

User: मेरा नाम राजेश है
Bot: आप कौन सी फसलें उगाते हैं?

User: गेहूं और धान
Bot: आपके पास कितनी जमीन है?

User: 5 एकड़
Bot: आप किस गांव से हैं?

User: पुणे
Bot: ✅ रजिस्ट्रेशन पूरा हुआ!
```

### Knowledge Graph Structure

```
(Farmer: Rajesh) ──[LIVES_IN]──> (Village: Pune)
       │
       ├──[GROWS]──> (Crop: Wheat)
       └──[GROWS]──> (Crop: Rice)
```

### Where to See the Knowledge Graph

1. **Streamlit Dashboard** (Recommended)
   - Run: `cd dashboard && ./run_dashboard.sh`
   - URL: `http://localhost:8501`
   - Features: Interactive graph, statistics, export

2. **DynamoDB Console**
   - Table: `kisaanmitra-user-profiles`
   - URL: https://console.aws.amazon.com/dynamodb

3. **Neptune Console** (if using Neptune)
   - URL: https://console.aws.amazon.com/neptune
   - Query with Gremlin

4. **Programmatically**
   ```python
   from knowledge_graph.village_graph import knowledge_graph
   
   # Get all data
   summary = knowledge_graph.get_graph_summary()
   print(f"Total farmers: {summary['total_farmers']}")
   
   # Get village data
   stats = knowledge_graph.get_village_statistics("Pune")
   print(f"Farmers in Pune: {stats['farmer_count']}")
   ```

### Cost

**Development (Local Graph):**
- DynamoDB: $0.25/month
- Lambda: $0.20/month
- Bedrock: $0.50/month
- **Total: ~$1/month**

**Production (with Neptune):**
- Add Neptune: $73/month (db.t3.medium)
- **Total: ~$76/month**

### Neptune Setup (Optional - Production Only)

For production with large scale (1000+ farmers):

```bash
cd infrastructure
./setup_neptune.sh
```

Update Lambda environment variable:
```bash
aws lambda update-function-configuration \
    --function-name kisaanmitra-whatsapp \
    --environment Variables={NEPTUNE_ENDPOINT=your-endpoint.amazonaws.com}
```

### Troubleshooting

**Onboarding not working?**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow

# Look for: "Profile saved for user {user_id}"
```

**Dashboard not loading?**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify tables exist
aws dynamodb list-tables --region ap-south-1
```

**AI extraction failing?**
- Verify Bedrock access in IAM role
- Check region: us-east-1 for cross-region inference

### Next Steps

1. ✅ Complete onboarding for 5-10 test farmers
2. ✅ View dashboard to see knowledge graph
3. ✅ Export farmer data as CSV
4. ✅ Query village statistics
5. ✅ Monitor CloudWatch logs

### Documentation

- Full docs: `docs/ONBOARDING_AND_KNOWLEDGE_GRAPH.md`
- Architecture: `CURRENT_ARCHITECTURE_DIAGRAM.md`
- API reference: See documentation

### Support

Questions? Check:
- Lambda logs: `aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow`
- DynamoDB console: https://console.aws.amazon.com/dynamodb
- Dashboard: `http://localhost:8501`

---

**Ready to scale!** 🚀
