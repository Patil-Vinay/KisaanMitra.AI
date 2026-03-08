# Price Forecasting System - Complete Explanation

## What Are We Doing?

We're predicting future crop prices (next 30 days) using historical price data and machine learning.

### Simple Example:
```
Historical Data (5 years):
Tomato prices: Mar 2021 to Mar 2026
- 2021-03-01: ₹45/kg
- 2021-03-02: ₹46/kg
- ...
- 2026-03-04: ₹52/kg

AI learns patterns:
- Seasonal trends (prices higher in summer)
- Weekly patterns (prices drop on Sundays)
- Long-term trends (inflation)

Prediction (next 30 days):
- 2026-03-05: ₹53/kg (predicted)
- 2026-03-06: ₹54/kg (predicted)
- ...
- 2026-04-04: ₹58/kg (predicted)
```

## How Are We Doing It?

### Step-by-Step Process:

```
┌─────────────────────────────────────────────────────────────┐
│                    WEEKLY TRAINING CYCLE                     │
└─────────────────────────────────────────────────────────────┘

1. TRIGGER (Every Sunday 2 AM)
   └─ EventBridge Rule: "kisaanmitra-weekly-forecast-training"
      └─ Triggers Lambda Function

2. LAMBDA FUNCTION: "kisaanmitra-sagemaker-forecaster"
   ├─ Fetches historical data from S3
   │  └─ 5 CSV files (Tomato, Onion, Potato, Wheat, Rice)
   │     └─ Each has ~1,820 days (2021-2026)
   │
   ├─ (Optional) Fetches latest 7 days from AgMarkNet API
   │  └─ Adds fresh data to historical data
   │
   ├─ Combines all data into SageMaker format
   │  └─ Creates: train.csv with columns:
   │     - item_id (crop name)
   │     - timestamp (date)
   │     - price (₹/kg)
   │
   └─ Uploads to S3: s3://kisaanmitra-ml-data/sagemaker-forecasting/train.csv

3. SAGEMAKER AUTOML (1-2 hours)
   ├─ Tests 6 different algorithms:
   │  1. ARIMA (statistical)
   │  2. ETS (exponential smoothing)
   │  3. Prophet (Facebook's algorithm)
   │  4. NPTS (neural network)
   │  5. DeepAR+ (deep learning)
   │  6. CNN-QR (convolutional neural network)
   │
   ├─ Each algorithm tries to predict prices
   ├─ SageMaker evaluates which is most accurate
   └─ Picks the BEST algorithm automatically

4. GENERATE FORECASTS
   ├─ Best model predicts next 30 days
   ├─ For each crop (5 crops)
   ├─ With confidence levels:
   │  - p50: 50% confidence (median prediction)
   │  - p60: 60% confidence
   │  - p70: 70% confidence
   │  - p80: 80% confidence
   │  - p90: 90% confidence
   │
   └─ Example output:
      Tomato 2026-03-05:
      - p50: ₹52/kg (most likely)
      - p90: ₹58/kg (worst case)

5. STORE RESULTS
   └─ DynamoDB Table: "kisaanmitra-price-forecasts"
      └─ Farmers can query forecasts via WhatsApp
```

## What Data Are We Using?

### Primary Data Source: S3 CSV Files
```
s3://kisaanmitra-ml-data/historical-prices/
├── Tomato.csv    (1,820 rows: 2021-03-02 to 2026-03-02)
├── Onion.csv     (1,820 rows: 2021-03-02 to 2026-03-02)
├── Potato.csv    (1,820 rows: 2021-03-02 to 2026-03-02)
├── Wheat.csv     (1,820 rows: 2021-03-02 to 2026-03-02)
└── Rice.csv      (1,820 rows: 2021-03-02 to 2026-03-02)

Total: 9,100 data points (5 crops × 1,820 days)
```

### Data Format in CSV:
```csv
State,Commodity Group,Commodity,Date,Arrival Quantity,Arrival Unit,Modal Price,Price Unit
Maharashtra,Vegetables,Tomato,02-03-2021,966.00,Metric Tonnes,872.62,Rs./Quintal
Maharashtra,Vegetables,Tomato,03-03-2021,959.00,Metric Tonnes,996.72,Rs./Quintal
...
```

### Secondary Data Source: AgMarkNet API (Optional)
- Fetches latest 7 days of prices
- Supplements historical data
- Requires API key (currently not configured)

## Why Train Every Week?

### Reason 1: Fresh Data
- Market prices change constantly
- New data = better predictions
- Model learns latest trends

### Reason 2: Model Drift
- Old models become less accurate over time
- Weekly retraining keeps model fresh
- Adapts to new market conditions

### Example:
```
Week 1: Model trained on data up to March 1
        Predicts March 2-31

Week 2: Model retrained with March 1-7 data
        Predicts March 9-April 7
        (More accurate because it saw March 2-7 actual prices)
```

## How is Weekly Training Set Up?

### EventBridge Rule Configuration:
```json
{
  "Name": "kisaanmitra-weekly-forecast-training",
  "ScheduleExpression": "cron(0 20 * * SUN *)",
  "State": "ENABLED",
  "Targets": [
    {
      "Arn": "arn:aws:lambda:ap-south-1:482548785371:function:kisaanmitra-sagemaker-forecaster",
      "Id": "1"
    }
  ]
}
```

**Translation**: 
- `cron(0 20 * * SUN *)` = Every Sunday at 20:00 UTC
- UTC 20:00 = IST 01:30 AM (next day, Monday)
- Triggers Lambda function automatically

### To Check Schedule:
```powershell
aws events describe-rule \
  --name kisaanmitra-weekly-forecast-training \
  --region ap-south-1
```

### To Disable Weekly Training:
```powershell
aws events disable-rule \
  --name kisaanmitra-weekly-forecast-training \
  --region ap-south-1
```

### To Change Frequency:
```powershell
# Monthly (1st of every month)
aws events put-rule \
  --name kisaanmitra-weekly-forecast-training \
  --schedule-expression "cron(0 20 1 * ? *)" \
  --region ap-south-1

# Bi-weekly (every 2 weeks)
aws events put-rule \
  --name kisaanmitra-weekly-forecast-training \
  --schedule-expression "cron(0 20 ? * SUN#1,SUN#3 *)" \
  --region ap-south-1
```

## Cost Breakdown

### Per Training Job:
```
SageMaker AutoML:     $5-15    (1-2 hours)
Lambda:               $0.01    (few seconds)
S3:                   $0.01    (storage)
DynamoDB:             $0.01    (writes)
────────────────────────────
Total:                ~$5-15
```

### Weekly Schedule:
```
4 trainings/month × $10 = $40/month
```

### To Reduce Costs:
1. Train bi-weekly: $20/month (50% savings)
2. Train monthly: $10/month (75% savings)
3. Train on-demand: $0/month (100% savings, manual only)

## Summary

**What**: Predict crop prices for next 30 days
**How**: Machine learning on 5 years of historical data
**Data**: 9,100 price records from 2021-2026
**When**: Every Sunday at 2 AM IST (automatic)
**Cost**: ~$10 per training job
**Output**: Forecasts stored in DynamoDB for farmer queries

---

**Current Status**: 
- ✅ 1 training job running (km-260304185319)
- ✅ Using real 5-year historical data
- ✅ Weekly schedule enabled
- ⚠️ AgMarkNet API not configured (optional)
