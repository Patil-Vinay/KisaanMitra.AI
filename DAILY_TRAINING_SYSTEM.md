# Daily Price Forecasting Training System

## Overview
This system trains Prophet ML models every morning at 6:00 AM IST and stores predictions in DynamoDB. The WhatsApp bot simply reads pre-computed forecasts (no on-demand training).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY TRAINING FLOW                       │
└─────────────────────────────────────────────────────────────┘

6:00 AM IST Daily:
┌──────────────┐
│ EventBridge  │ (AWS) or Windows Task Scheduler (Local)
│   Trigger    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 1: Fetch Latest Data                                   │
│  ┌────────────┐                                              │
│  │ AgMarkNet  │ ──> Get last 30 days prices                 │
│  │    API     │     for 5 crops                              │
│  └────────────┘                                              │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 2: Update Historical Data                              │
│  ┌────────────┐                                              │
│  │ CSV Files  │ ──> Append new records                       │
│  │  or S3     │     Remove duplicates                        │
│  └────────────┘     Sort by date                             │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 3: Train Prophet Models                                │
│  ┌────────────┐                                              │
│  │  Prophet   │ ──> Train on historical data                 │
│  │   Model    │     Generate 30-day forecast                 │
│  └────────────┘     With confidence intervals                │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  STEP 4: Store Predictions                                   │
│  ┌────────────┐                                              │
│  │ DynamoDB   │ ──> Store 30-day forecasts                   │
│  │   Table    │     for each crop                            │
│  └────────────┘                                              │
└──────────────────────────────────────────────────────────────┘

USER QUERY FLOW:
┌──────────────┐
│ User asks    │ "week forecast for wheat"
│ via WhatsApp │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  WhatsApp Lambda                                              │
│  ┌────────────┐                                              │
│  │  General   │ ──> Detect price forecast query              │
│  │   Agent    │     Extract crop name                        │
│  └────────────┘     Validate crop                            │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Read from DynamoDB (NO TRAINING)                            │
│  ┌────────────┐                                              │
│  │ DynamoDB   │ ──> Get pre-computed forecast                │
│  │   Table    │     Format for WhatsApp                      │
│  └────────────┘     Send to user                             │
└──────────────────────────────────────────────────────────────┘
```

## Components

### 1. Daily Trainer Script
**File**: `src/price_forecasting/daily_trainer.py`

**What it does**:
- Fetches latest data from AgMarkNet API
- Updates CSV files with new records
- Trains Prophet models for 5 crops
- Generates 30-day forecasts
- Uploads to DynamoDB

**Run manually**:
```bash
python src/price_forecasting/daily_trainer.py
```

### 2. Windows Task Scheduler (Local)
**File**: `scripts/setup_daily_training.ps1`

**Setup**:
```powershell
.\scripts\setup_daily_training.ps1
```

**Features**:
- Runs daily at 6:00 AM
- Logs to `logs/daily_training.log`
- Can be triggered manually

**Manual trigger**:
```powershell
schtasks /Run /TN "KisaanMitra-DailyPriceTraining"
```

### 3. AWS Lambda + EventBridge (Cloud)
**File**: `src/lambda/lambda_daily_trainer.py`

**Setup**:
```bash
bash infrastructure/setup_daily_training_lambda.sh
```

**Features**:
- Runs daily at 6:00 AM IST (00:30 UTC)
- Stores historical data in S3
- Uploads forecasts to DynamoDB
- 15-minute timeout
- CloudWatch logs

**Test Lambda**:
```bash
aws lambda invoke --function-name kisaanmitra-daily-trainer --region ap-south-1 output.json
```

## Data Flow

### Historical Data Storage

**Local (CSV)**:
```
data/historical_prices/
├── Onion.csv
├── Rice.csv
├── Sugarcane.csv
├── Tomato.csv
└── Wheat.csv
```

**AWS (S3)**:
```
s3://kisaanmitra-images/historical_prices/
├── Onion.csv
├── Rice.csv
├── Sugarcane.csv
├── Tomato.csv
└── Wheat.csv
```

### Forecast Storage (DynamoDB)

**Table**: `kisaanmitra-price-forecasts`

**Structure**:
```json
{
  "commodity": "wheat",
  "last_updated": "2026-03-04T06:00:00",
  "model": "Prophet",
  "training_records": 365,
  "forecasts": [
    {
      "date": "2026-03-04",
      "day": "Wednesday",
      "price": 2200.00,
      "lower": 2100.00,
      "upper": 2300.00
    },
    // ... 29 more days
  ]
}
```

## Supported Crops

1. **Onion** - Base price: ₹1800/quintal
2. **Rice** - Base price: ₹2500/quintal
3. **Sugarcane** - Base price: ₹350/quintal
4. **Tomato** - Base price: ₹1200/quintal
5. **Wheat** - Base price: ₹2200/quintal

## Prophet Model Configuration

```python
model = Prophet(
    daily_seasonality=True,      # Capture daily patterns
    weekly_seasonality=True,     # Capture weekly patterns
    yearly_seasonality=True,     # Capture seasonal patterns
    changepoint_prior_scale=0.05 # Flexibility for trend changes
)
```

## WhatsApp Bot Integration

### Detection Logic
File: `src/lambda/agents/general_agent.py`

```python
# Detects queries like:
- "week forecast for wheat"
- "7 day prices for onion"
- "price forecast for rice"
- "future price of tomato"
```

### Response Format

**7-Day Forecast**:
```
📅 Wheat - 7 Day Forecast

Wednesday, 2026-03-04
₹2200.00/quintal (₹2100.00-₹2300.00)

Thursday, 2026-03-05
₹2202.00/quintal (₹2102.00-₹2302.00)

...

⚠️ I can only forecast prices for: Onion, Rice, Sugarcane, Tomato, Wheat
```

**Daily Forecast**:
```
📊 Wheat Price Forecast

Today (Wednesday)
💰 Predicted: ₹2200/quintal
📈 Range: ₹2100 - ₹2300

Tomorrow (Thursday)
💰 Predicted: ₹2202/quintal
📈 Range: ₹2102 - ₹2302

📈 Expected to increase by ₹2.00
```

## Monitoring

### Check Training Logs (Local)
```bash
cat logs/daily_training.log
```

### Check Lambda Logs (AWS)
```bash
aws logs tail /aws/lambda/kisaanmitra-daily-trainer --since 1h --region ap-south-1
```

### Verify DynamoDB Data
```bash
aws dynamodb get-item \
  --table-name kisaanmitra-price-forecasts \
  --key '{"commodity":{"S":"wheat"}}' \
  --region ap-south-1
```

### Check Last Update Time
```bash
aws dynamodb scan \
  --table-name kisaanmitra-price-forecasts \
  --projection-expression "commodity,last_updated" \
  --region ap-south-1
```

## Troubleshooting

### Training Fails
1. Check AgMarkNet API key is valid
2. Verify CSV files exist and are readable
3. Check Prophet is installed: `pip install prophet`
4. Review logs for specific errors

### Lambda Timeout
1. Increase timeout to 15 minutes (900 seconds)
2. Increase memory to 1024 MB or higher
3. Consider processing crops in parallel

### DynamoDB Upload Fails
1. Verify IAM role has DynamoDB write permissions
2. Check table name matches environment variable
3. Ensure Decimal types are used (not float)

### AgMarkNet API Issues
1. API may be down - training will use existing data
2. Check API key is not expired
3. Verify network connectivity

## Cost Estimation (AWS)

### Lambda
- Runs: 1x per day
- Duration: ~5 minutes
- Memory: 1024 MB
- Cost: ~$0.01/month

### DynamoDB
- Storage: ~5 KB per crop = 25 KB total
- Reads: ~100/day (user queries)
- Writes: 5/day (training updates)
- Cost: ~$0.50/month

### S3
- Storage: ~5 CSV files × 100 KB = 500 KB
- Cost: ~$0.01/month

**Total**: ~$0.52/month

## Future Enhancements

1. **More Crops**: Expand to 20+ crops
2. **Regional Forecasts**: State-specific predictions
3. **Accuracy Tracking**: Compare predictions vs actual prices
4. **Model Improvements**: Try ARIMA, LSTM, XGBoost
5. **Price Alerts**: Notify users of significant changes
6. **Historical Analysis**: Show price trends over time
7. **Market Insights**: Add supply/demand factors

## Testing

### Test Training Script
```bash
# Local
python src/price_forecasting/daily_trainer.py

# AWS Lambda
aws lambda invoke \
  --function-name kisaanmitra-daily-trainer \
  --region ap-south-1 \
  output.json && cat output.json
```

### Test WhatsApp Bot
Send these messages:
1. "week forecast for wheat"
2. "7 day prices for onion"
3. "price forecast for rice"

### Verify Results
```bash
# Check DynamoDB
aws dynamodb scan \
  --table-name kisaanmitra-price-forecasts \
  --region ap-south-1

# Check WhatsApp Lambda logs
aws logs tail /aws/lambda/whatsapp-llama-bot \
  --since 5m --region ap-south-1 | grep -i "price\|forecast"
```

## Deployment Checklist

- [ ] Install Prophet: `pip install prophet`
- [ ] Set AgMarkNet API key in environment
- [ ] Create DynamoDB table
- [ ] Upload historical CSV files
- [ ] Test training script locally
- [ ] Set up Windows Task Scheduler OR AWS Lambda
- [ ] Deploy updated WhatsApp Lambda
- [ ] Test end-to-end via WhatsApp
- [ ] Monitor logs for 24 hours
- [ ] Verify daily training runs successfully

---

**Status**: ✅ READY FOR DEPLOYMENT
**Last Updated**: 2026-03-04
**Maintainer**: KisaanMitra Team
