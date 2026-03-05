# 🚀 Forecast Deployment Guide

## What This Does

This script will:
1. ✅ Deploy your trained SageMaker model as a real-time endpoint
2. ✅ Generate 30-day price forecasts for all 5 crops
3. ✅ Store forecasts in DynamoDB (WhatsApp bot compatible format)
4. ✅ Optionally delete endpoint to save costs

---

## Prerequisites

### 1. Python Dependencies
```bash
pip install boto3 pandas
```

Or use the requirements file:
```bash
pip install -r scripts/requirements.txt
```

### 2. AWS Credentials
Make sure your AWS credentials are configured:
```bash
aws configure
```

### 3. Trained Model
Your model `km-260304185319` is already trained and ready ✅

---

## Running the Script

### Option 1: Interactive Mode (Recommended)
```bash
python scripts/deploy_and_forecast.py
```

The script will:
- Show progress for each step
- Display forecast samples
- Ask if you want to delete the endpoint after forecasting

### Option 2: Run from Project Root
```bash
cd /path/to/KisaanMitra.AI
python scripts/deploy_and_forecast.py
```

---

## What to Expect

### Step 1: Get Best Candidate (5 seconds)
```
📊 Fetching best candidate from AutoML job: km-260304185319
✅ Best candidate: km-260304185319-trial-me-1
   Metric: AverageWeightedQuantileLoss
   Value: 1.6907755195916252e-08
```

### Step 2: Create Model (10 seconds)
```
🔨 Creating model: km-260304185319-model
✅ Model created: arn:aws:sagemaker:ap-south-1:482548785371:model/...
```

### Step 3: Create Endpoint Config (5 seconds)
```
⚙️  Creating endpoint config: km-260304185319-model-config
✅ Endpoint config created
```

### Step 4: Create Endpoint (5-10 minutes)
```
🚀 Creating endpoint: kisaanmitra-forecast-endpoint
✅ Endpoint creation started
⏳ Waiting for endpoint to be InService (this takes 5-10 minutes)...
  [30s] Status: Creating
  [60s] Status: Creating
  [90s] Status: Creating
  ...
  [600s] Status: InService
✅ Endpoint is InService!
```

### Step 5: Generate Forecasts (1-2 minutes per crop)
```
🔮 Generating Forecasts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔮 Generating forecast for: onion
✅ Forecast generated for onion
📝 Formatting forecast for DynamoDB: onion
💾 Storing forecast in DynamoDB: onion
✅ Forecast stored for onion
   First day: 2026-03-06 - ₹2,150.50
   Last day: 2026-04-04 - ₹2,380.75
✅ ONION forecast complete

🔮 Generating forecast for: rice
✅ Forecast generated for rice
...
```

### Step 6: Cleanup Decision
```
✅ Forecast Generation Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Endpoint Cost: ~₹4-5 per hour while running
   Endpoint Name: kisaanmitra-forecast-endpoint

Options:
1. Keep endpoint running for future forecasts
2. Delete endpoint now to save costs (can recreate later)

Delete endpoint? (y/n): 
```

**Recommendation**: Type `y` to delete the endpoint and save costs. You can recreate it anytime by running this script again.

---

## Cost Breakdown

### One-Time Costs (This Run)
- **Endpoint deployment**: Free (just setup time)
- **Inference (5 crops × 30 days)**: ~₹0.50 (negligible)
- **Endpoint running time**: ~₹0.50 (if deleted after 10 minutes)

**Total**: ~₹1 per run

### If You Keep Endpoint Running
- **Cost**: ~₹4-5 per hour = ~₹100-120 per day
- **Monthly**: ~₹3,000-3,600

**Recommendation**: Delete endpoint after forecasting. Recreate weekly when needed.

---

## Verifying the Forecasts

### Check DynamoDB
```bash
aws dynamodb get-item \
  --table-name kisaanmitra-price-forecasts \
  --key '{"commodity": {"S": "tomato"}}'
```

Expected output:
```json
{
  "Item": {
    "commodity": {"S": "tomato"},
    "forecasts": {"L": [
      {"M": {
        "date": {"S": "2026-03-06"},
        "day": {"S": "Thursday"},
        "price": {"N": "1459.61"},
        "lower": {"N": "81.63"},
        "upper": {"N": "2768.12"}
      }},
      ...
    ]},
    "generated_at": {"S": "2026-03-05T02:00:00"},
    "model_version": {"S": "sagemaker_automl_v1"}
  }
}
```

### Test via WhatsApp
Send these messages to your WhatsApp bot:

**Hindi**:
- "टमाटर का भाव कल क्या होगा?"
- "अगले हफ्ते प्याज का रेट?"

**English**:
- "What will tomato price be tomorrow?"
- "Onion price forecast for next week?"

Expected response:
```
🔮 टमाटर - मूल्य पूर्वानुमान

📅 कल (गुरुवार, 6 मार्च)
💰 अनुमानित भाव: ₹1,459.61/quintal
📊 रेंज: ₹81.63 - ₹2,768.12

📈 अगले 7 दिन:
• गुरुवार: ₹1,459.61
• शुक्रवार: ₹1,485.20
• शनिवार: ₹1,510.80
...
```

---

## Troubleshooting

### Error: "Endpoint already exists"
The script handles this automatically. It will use the existing endpoint.

### Error: "Model already exists"
The script handles this automatically. It will use the existing model.

### Error: "Insufficient permissions"
Make sure your IAM role has these permissions:
- `sagemaker:CreateModel`
- `sagemaker:CreateEndpointConfig`
- `sagemaker:CreateEndpoint`
- `sagemaker:InvokeEndpoint`
- `dynamodb:PutItem`

### Error: "Endpoint creation timeout"
Endpoint creation can take 10-15 minutes. The script waits up to 20 minutes. If it times out, check the SageMaker console for the actual status.

### Forecasts look wrong
The script uses a fallback format if the model output structure is different. Check the CloudWatch logs for the actual model response format and adjust the `format_forecast_for_dynamodb()` function.

---

## Automation Options

### Option 1: Manual Weekly Run
Run this script every Sunday after training completes:
```bash
python scripts/deploy_and_forecast.py
```

### Option 2: Lambda Function (Recommended)
Convert this script to a Lambda function triggered by EventBridge when training completes.

### Option 3: Step Functions
Create a Step Functions workflow:
1. Training Lambda (existing)
2. Wait for completion
3. Forecast Lambda (this script)
4. Cleanup

---

## Next Steps After Running

### 1. Verify Forecasts
- Check DynamoDB table
- Test via WhatsApp bot
- Verify date ranges and prices

### 2. Monitor Accuracy
- Compare forecasts with actual prices
- Track farmer feedback
- Adjust model if needed

### 3. Set Up Weekly Automation
- Create Lambda function from this script
- Set up EventBridge trigger
- Test end-to-end flow

### 4. Delete Endpoint (If Not Automated)
```bash
aws sagemaker delete-endpoint --endpoint-name kisaanmitra-forecast-endpoint
```

---

## Script Configuration

You can modify these variables in `scripts/deploy_and_forecast.py`:

```python
# Configuration
REGION = 'ap-south-1'
AUTOML_JOB_NAME = 'km-260304185319'  # Your training job
ENDPOINT_NAME = 'kisaanmitra-forecast-endpoint'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
ROLE_ARN = 'arn:aws:iam::482548785371:role/KisaanMitra-SageMaker-Role'

# Crops to forecast
CROPS = ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']
```

---

## Summary

**Time Required**: 10-15 minutes (mostly waiting for endpoint)
**Cost**: ~₹1 per run (if endpoint deleted after)
**Output**: 30-day forecasts for 5 crops in DynamoDB
**Result**: Farmers can query price predictions via WhatsApp

**Command**:
```bash
python scripts/deploy_and_forecast.py
```

**After Running**: Delete endpoint to save costs (script will ask)

---

## Quick Start

```bash
# 1. Install dependencies
pip install boto3 pandas

# 2. Run the script
python scripts/deploy_and_forecast.py

# 3. Wait 10-15 minutes

# 4. Delete endpoint when prompted (type 'y')

# 5. Test via WhatsApp: "टमाटर का भाव कल क्या होगा?"
```

That's it! Your forecasts are now live and farmers can query them via WhatsApp.
