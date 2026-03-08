# AWS Price Forecasting System - Complete Setup

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Price Forecasting System                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│ EventBridge  │────────>│   Lambda     │────────>│  AgMarkNet   │
│ (Daily 6 AM) │         │   Updater    │         │     API      │
└──────────────┘         └──────┬───────┘         └──────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │    S3    │ │ DynamoDB │ │   SNS    │
            │  Bucket  │ │  Table   │ │  Topic   │
            └──────────┘ └──────────┘ └──────────┘
                    │           │
                    └─────┬─────┘
                          │
                          ▼
                ┌──────────────────┐
                │  WhatsApp Lambda │
                │  (Main Handler)  │
                └──────────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │  Farmer  │
                    │ (WhatsApp)│
                    └──────────┘
```

## AWS Services Used

### 1. **Amazon S3** - Data Storage
- **Bucket**: `kisaanmitra-price-data`
- **Purpose**: Store historical CSV files and forecast JSON files
- **Structure**:
  ```
  kisaanmitra-price-data/
  ├── historical_prices/
  │   ├── Onion.csv
  │   ├── Rice.csv
  │   ├── Sugarcane.csv
  │   ├── Tomato.csv
  │   └── Wheat.csv
  ├── forecasts/
  │   ├── onion_forecast.json
  │   ├── rice_forecast.json
  │   ├── sugarcane_forecast.json
  │   ├── tomato_forecast.json
  │   └── wheat_forecast.json
  └── models/
      └── (trained models - future)
  ```

### 2. **Amazon DynamoDB** - Fast Forecast Access
- **Table**: `kisaanmitra-price-forecasts`
- **Primary Key**: `commodity` (String)
- **Attributes**:
  - `commodity`: Crop name (onion, rice, etc.)
  - `generated_at`: Timestamp
  - `forecasts`: List of predictions
  - `ttl`: Auto-expire after 7 days
- **Purpose**: Fast access to latest forecasts for WhatsApp bot

### 3. **AWS Lambda** - Serverless Computing
#### Lambda 1: Price Updater (`kisaanmitra-price-updater`)
- **Runtime**: Python 3.12
- **Memory**: 512 MB
- **Timeout**: 300 seconds (5 minutes)
- **Trigger**: EventBridge (daily at 6 AM IST)
- **Functions**:
  - Fetch data from AgMarkNet API
  - Update CSV files in S3
  - Train forecasting models
  - Save forecasts to DynamoDB and S3
  - Send SNS notifications

#### Lambda 2: WhatsApp Handler (`whatsapp-llama-bot`)
- **Enhanced with**: Price forecasting integration
- **New Functions**:
  - `handle_price_forecast_query()` - Process price queries
  - `format_daily_forecast()` - Format today/tomorrow prices
  - `format_week_forecast()` - Format 7-day forecast
- **DynamoDB Access**: Read forecasts from table

### 4. **Amazon EventBridge** - Scheduled Triggers
- **Rule**: `kisaanmitra-daily-price-update`
- **Schedule**: `cron(30 0 * * ? *)` (6:00 AM IST daily)
- **Target**: Lambda function `kisaanmitra-price-updater`
- **Purpose**: Automated daily data updates

### 5. **Amazon SNS** - Notifications
- **Topic**: `kisaanmitra-price-alerts`
- **Purpose**: Send email/SMS alerts about:
  - Daily update completion
  - Update failures
  - Significant price changes (future)
- **Subscribers**: Admin emails

### 6. **AWS IAM** - Security & Permissions
- **Role**: `kisaanmitra-price-updater-role`
- **Policies**:
  - S3: Read/Write access to price data bucket
  - DynamoDB: Read/Write access to forecasts table
  - SNS: Publish to alerts topic
  - CloudWatch Logs: Write logs
  - Lambda: Basic execution role

## Setup Instructions

### Prerequisites
```bash
# Set AgMarkNet API key
export AGMARKNET_API_KEY="your-api-key-here"

# Ensure AWS CLI is configured
aws configure
```

### One-Command Setup
```bash
chmod +x infrastructure/setup_price_forecasting.sh
./infrastructure/setup_price_forecasting.sh
```

### Manual Setup Steps

#### 1. Create S3 Bucket
```bash
aws s3 mb s3://kisaanmitra-price-data --region ap-south-1

# Upload historical data
aws s3 sync data/historical_prices/ s3://kisaanmitra-price-data/historical_prices/
```

#### 2. Create DynamoDB Table
```bash
aws dynamodb create-table \
    --table-name kisaanmitra-price-forecasts \
    --attribute-definitions AttributeName=commodity,AttributeType=S \
    --key-schema AttributeName=commodity,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1
```

#### 3. Create SNS Topic
```bash
aws sns create-topic --name kisaanmitra-price-alerts --region ap-south-1

# Subscribe your email
aws sns subscribe \
    --topic-arn arn:aws:sns:ap-south-1:ACCOUNT_ID:kisaanmitra-price-alerts \
    --protocol email \
    --notification-endpoint your@email.com
```

#### 4. Deploy Lambda Function
```bash
cd src/lambda
zip lambda_price_updater.zip lambda_price_updater.py

aws lambda create-function \
    --function-name kisaanmitra-price-updater \
    --runtime python3.12 \
    --role arn:aws:iam::ACCOUNT_ID:role/kisaanmitra-price-updater-role \
    --handler lambda_price_updater.lambda_handler \
    --zip-file fileb://lambda_price_updater.zip \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{S3_BUCKET=kisaanmitra-price-data,PRICE_FORECAST_TABLE=kisaanmitra-price-forecasts,AGMARKNET_API_KEY=$AGMARKNET_API_KEY}" \
    --region ap-south-1
```

#### 5. Create EventBridge Rule
```bash
# Create rule for daily 6 AM IST (12:30 AM UTC)
aws events put-rule \
    --name kisaanmitra-daily-price-update \
    --schedule-expression "cron(30 0 * * ? *)" \
    --state ENABLED \
    --region ap-south-1

# Add Lambda as target
aws events put-targets \
    --rule kisaanmitra-daily-price-update \
    --targets "Id"="1","Arn"="arn:aws:lambda:ap-south-1:ACCOUNT_ID:function:kisaanmitra-price-updater" \
    --region ap-south-1
```

#### 6. Update WhatsApp Lambda
```bash
# Redeploy with price forecasting integration
cd src/lambda
zip -r whatsapp_deployment.zip lambda_whatsapp_kisaanmitra.py knowledge_graph_helper.py anthropic_client.py whatsapp_interactive.py navigation_controller.py user_state_manager.py

# Add onboarding module
cd ..
zip -r lambda/whatsapp_deployment.zip onboarding/

# Deploy
aws lambda update-function-code \
    --function-name whatsapp-llama-bot \
    --zip-file fileb://lambda/whatsapp_deployment.zip \
    --region ap-south-1

# Update environment variables
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --environment Variables="{PRICE_FORECAST_TABLE=kisaanmitra-price-forecasts,S3_BUCKET=kisaanmitra-price-data}" \
    --region ap-south-1
```

## Usage Examples

### WhatsApp Queries

#### English
```
User: "What is onion price today?"
Bot: 📊 Onion Price Forecast
     Today (Wednesday)
     💰 Predicted: ₹305/quintal
     📈 Range: ₹-157 - ₹725
     ...

User: "Week forecast for wheat"
Bot: 📅 Wheat - 7 Day Forecast
     Tuesday, 2026-03-03
     ₹2994/quintal (₹2613-₹3365)
     ...

User: "Tomorrow rice price"
Bot: 📊 Rice Price Forecast
     Tomorrow (Thursday)
     💰 Predicted: ₹5289/quintal
     ...

User: "Cotton price"
Bot: 📊 Price Forecasting Available
     I can provide forecasts for:
     🧅 Onion, 🌾 Rice, 🎋 Sugarcane, 🍅 Tomato, 🌾 Wheat
     ⚠️ I can only forecast prices for these 5 crops.
```

#### Hindi
```
User: "आज प्याज का भाव क्या है?"
Bot: 📊 प्याज मूल्य पूर्वानुमान
     आज (बुधवार)
     💰 अनुमानित: ₹305/क्विंटल
     ...

User: "गेहूं का साप्ताहिक पूर्वानुमान"
Bot: 📅 गेहूं - 7 दिन का पूर्वानुमान
     ...
```

## Daily Workflow

### 6:00 AM IST - Automated Update
```
1. EventBridge triggers Lambda
2. Lambda fetches latest data from AgMarkNet API
3. Updates CSV files in S3
4. Trains forecasting models
5. Generates 30-day forecasts
6. Saves to DynamoDB (fast access)
7. Saves to S3 (backup)
8. Sends SNS notification with summary
```

### Throughout Day - User Queries
```
1. Farmer sends WhatsApp message
2. Lambda detects price query
3. Identifies crop (onion/rice/etc.)
4. Fetches forecast from DynamoDB
5. Formats message (English/Hindi)
6. Sends response via WhatsApp
```

## Monitoring & Maintenance

### View Lambda Logs
```bash
# Price updater logs
aws logs tail /aws/lambda/kisaanmitra-price-updater --follow --region ap-south-1

# WhatsApp bot logs
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
```

### Check DynamoDB Data
```bash
# Scan forecasts table
aws dynamodb scan --table-name kisaanmitra-price-forecasts --region ap-south-1

# Get specific crop
aws dynamodb get-item \
    --table-name kisaanmitra-price-forecasts \
    --key '{"commodity":{"S":"onion"}}' \
    --region ap-south-1
```

### View S3 Files
```bash
# List historical data
aws s3 ls s3://kisaanmitra-price-data/historical_prices/

# List forecasts
aws s3 ls s3://kisaanmitra-price-data/forecasts/

# Download a file
aws s3 cp s3://kisaanmitra-price-data/forecasts/onion_forecast.json .
```

### Manual Trigger
```bash
# Trigger price update manually
aws lambda invoke \
    --function-name kisaanmitra-price-updater \
    --region ap-south-1 \
    response.json

cat response.json
```

## Cost Estimation

### Monthly Costs (Approximate)

| Service | Usage | Cost |
|---------|-------|------|
| S3 | 100 MB storage, 1000 requests | $0.01 |
| DynamoDB | 5 items, on-demand | $0.00 |
| Lambda (Updater) | 30 invocations/month, 300s each | $0.01 |
| Lambda (WhatsApp) | 10,000 invocations/month | $0.20 |
| EventBridge | 30 rules/month | $0.00 |
| SNS | 30 notifications/month | $0.00 |
| **Total** | | **~$0.25/month** |

*Note: Costs are minimal due to AWS Free Tier*

## Troubleshooting

### Issue: Lambda timeout
**Solution**: Increase timeout to 300 seconds
```bash
aws lambda update-function-configuration \
    --function-name kisaanmitra-price-updater \
    --timeout 300 \
    --region ap-south-1
```

### Issue: AgMarkNet API not responding
**Solution**: Check API key and rate limits
```bash
# Test API manually
curl "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=$AGMARKNET_API_KEY&format=json&limit=1"
```

### Issue: DynamoDB access denied
**Solution**: Update IAM role permissions
```bash
# Attach DynamoDB policy
aws iam attach-role-policy \
    --role-name kisaanmitra-price-updater-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
```

### Issue: Forecasts not updating
**Solution**: Check EventBridge rule
```bash
# Verify rule is enabled
aws events describe-rule --name kisaanmitra-daily-price-update --region ap-south-1

# Check Lambda permissions
aws lambda get-policy --function-name kisaanmitra-price-updater --region ap-south-1
```

## Future Enhancements

1. **SageMaker Integration**
   - Train Prophet models on SageMaker
   - Better accuracy with more compute
   - Model versioning and A/B testing

2. **CloudWatch Alarms**
   - Alert on Lambda failures
   - Monitor API latency
   - Track forecast accuracy

3. **API Gateway**
   - REST API for forecasts
   - Public access for partners
   - Rate limiting and authentication

4. **Step Functions**
   - Orchestrate complex workflows
   - Parallel processing of crops
   - Error handling and retries

5. **Athena Queries**
   - Analyze historical trends
   - Generate insights
   - Business intelligence

## Security Best Practices

1. **API Keys**: Store in AWS Secrets Manager
2. **IAM Roles**: Principle of least privilege
3. **S3 Buckets**: Enable versioning and encryption
4. **DynamoDB**: Enable point-in-time recovery
5. **Lambda**: Use VPC for sensitive operations

## Support & Documentation

- **AWS Documentation**: https://docs.aws.amazon.com/
- **AgMarkNet API**: https://data.gov.in/
- **Prophet Library**: https://facebook.github.io/prophet/

---

**System Status**: FULLY OPERATIONAL ✅
**Last Updated**: March 4, 2026
**Next Scheduled Update**: Daily at 6:00 AM IST
