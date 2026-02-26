# Complete Testing Guide - All 3 Agents

## 🧪 Quick Test All Agents (2 minutes)

```bash
# Run all tests at once
./test_whatsapp_integration.sh && \
./test_market_agent.sh && \
./test_finance_agent.sh
```

---

## 1️⃣ Crop Agent Testing

### A. Local Code Testing (No AWS)

```bash
# Test 1: WhatsApp Integration Features
./test_whatsapp_integration.sh
```

**Expected Output:**
```
✅ PASS: All new functions present
✅ PASS: All required environment variables referenced
✅ PASS: WhatsApp webhook verification implemented
✅ PASS: All message types handled
✅ PASS: Bedrock AI integration configured
✅ PASS: Crop Health API integrated
✅ PASS: Response formatting implemented
✅ PASS: Error handling implemented
✅ PASS: Image download functionality implemented
✅ PASS: Image encoding implemented

Passed: 10/10
```

### B. Crop Engine Testing (Requires API Key)

```bash
# Test 2: Crop Health API with Real Image
python3 test_crop_engine.py
```

**Expected Output:**
```
🔍 Testing Crop Engine with test image...
Crop API status: 201
📊 Formatted Result for WhatsApp:
*🌾 फसल रोग विश्लेषण*

1. *sugarcane rust*
   विश्वास: 99.0%

💡 सर्वोत्तम परिणामों के लिए स्थानीय कृषि विशेषज्ञ से परामर्श लें।
✅ Crop engine test completed!
```

### C. Lambda Testing (Requires AWS)

```bash
# Test 3: Deployed Lambda Function
aws lambda invoke \
  --function-name kisaanmitra-crop-agent \
  --payload file://src/lambda/test_event.json \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json | python3 -m json.tool
```

**Expected Output:**
```json
{
  "statusCode": 200,
  "body": "ok"
}
```

### D. Full Deployment Testing

```bash
# Test 4: Complete Deployment Verification
./test_deployment.sh
```

**Expected Output:**
```
✅ PASS: Lambda function exists
✅ PASS: IAM role configured
✅ PASS: S3 bucket accessible
✅ PASS: Secrets Manager configured
✅ PASS: Test image uploaded
✅ PASS: Lambda invocation successful
✅ PASS: Disease detection working
✅ PASS: Response formatting correct
✅ PASS: Logs available
✅ PASS: Error handling working

Passed: 10/10
```

---

## 2️⃣ Market Agent Testing

### A. Local Code Testing

```bash
# Test 1: Market Agent Features
./test_market_agent.sh
```

**Expected Output:**
```
✅ PASS: Market agent structure valid
✅ PASS: System prompt properly configured
✅ PASS: All data sources integrated
✅ PASS: DynamoDB integration present
✅ PASS: Price trend analysis implemented
✅ PASS: Crop recommendation system present
✅ PASS: Response formatting implemented
✅ PASS: Enhanced crop agent complete
✅ PASS: Infrastructure scripts present
✅ PASS: Deployment scripts ready

Passed: 10/10
```

### B. Function Testing (Python)

```bash
# Test 2: Market Agent Functions
python3 << 'EOF'
import sys
sys.path.insert(0, 'src/market_agent')
from market_agent import get_crop_recommendation, analyze_price_trend

# Test crop recommendations
crops = get_crop_recommendation("Pune", "kharif")
print("🌾 Kharif Crops:", crops)

# Test price trend analysis
prices = [
    {"modal_price": "2500"},
    {"modal_price": "2450"},
    {"modal_price": "2300"}
]
trend = analyze_price_trend(prices)
print("📊 Trend Analysis:", trend)
EOF
```

**Expected Output:**
```
🌾 Kharif Crops: ['rice', 'cotton', 'soybean', 'maize', 'sugarcane']
📊 Trend Analysis: {'trend': 'increasing', 'recent_avg': 2500.0, ...}
```

### C. Lambda Testing (After Deployment)

```bash
# Test 3: Market Agent Lambda
aws lambda invoke \
  --function-name kisaanmitra-market-agent \
  --payload '{"body":"{\"type\":\"price_check\",\"crop\":\"wheat\"}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  market_response.json

cat market_response.json | python3 -m json.tool
```

**Expected Output:**
```json
{
  "statusCode": 200,
  "body": "{\"success\": true, \"response\": \"*📊 Wheat - Market Analysis*...\"}"
}
```

---

## 3️⃣ Finance Agent Testing

### A. Local Code Testing

```bash
# Test 1: Finance Agent Features
./test_finance_agent.sh
```

**Expected Output:**
```
✅ PASS: File structure valid
✅ PASS: All crop budgets present (6 crops)
✅ PASS: Loan calculation implemented
✅ PASS: Government schemes integrated
✅ PASS: Cost optimization implemented
✅ PASS: Risk assessment implemented
✅ PASS: Financial plan generation complete
✅ PASS: DynamoDB integration present
✅ PASS: S3 integration present
✅ PASS: Response formatting implemented
✅ PASS: Infrastructure scripts present
✅ PASS: Deployment ready

Passed: 12/12
```

### B. Function Testing (Python)

```bash
# Test 2: Finance Agent Functions
python3 << 'EOF'
import sys
sys.path.insert(0, 'src/finance_agent')
from finance_agent import (
    get_crop_budget_template,
    calculate_loan_eligibility,
    optimize_input_costs,
    assess_financial_risk
)

# Test budget template
budget = get_crop_budget_template("wheat", 2)
print("💰 Budget for 2 acres wheat:")
print(f"   Total Cost: ₹{budget['total_cost']:,}")
print(f"   Expected Profit: ₹{budget['expected_profit']:,}")
print(f"   ROI: {budget['roi_percent']}%")

# Test loan eligibility
loan = calculate_loan_eligibility(budget, 50000)
print(f"\n🏦 Loan Eligibility:")
print(f"   Max Loan: ₹{loan['max_loan_amount']:,}")
print(f"   Interest Rate: {loan['interest_rate']}%")
print(f"   Monthly EMI: ₹{loan['monthly_emi']:,}")

# Test cost optimization
optimizations = optimize_input_costs(budget)
print(f"\n💡 Cost Savings:")
print(f"   Potential Savings: ₹{optimizations['total_potential_savings']:,}")
print(f"   Optimized Cost: ₹{optimizations['optimized_cost']:,}")

# Test risk assessment
risk = assess_financial_risk(budget, loan)
print(f"\n⚠️  Risk Assessment:")
print(f"   Risk Level: {risk['risk_level'].upper()}")
print(f"   Risk Score: {risk['risk_score']}/100")
EOF
```

**Expected Output:**
```
💰 Budget for 2 acres wheat:
   Total Cost: ₹31,400
   Expected Profit: ₹88,600
   ROI: 282%

🏦 Loan Eligibility:
   Max Loan: ₹25,120
   Interest Rate: 7.0%
   Monthly EMI: ₹4,300

💡 Cost Savings:
   Potential Savings: ₹6,280
   Optimized Cost: ₹25,120

⚠️  Risk Assessment:
   Risk Level: LOW
   Risk Score: 15/100
```

### C. Lambda Testing (After Deployment)

```bash
# Test 3: Finance Agent Lambda - Budget Plan
aws lambda invoke \
  --function-name kisaanmitra-finance-agent \
  --payload '{"body":"{\"type\":\"budget_plan\",\"crop\":\"wheat\",\"land_size\":2,\"income\":50000,\"user_id\":\"test_user\"}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  finance_response.json

cat finance_response.json | python3 -m json.tool
```

**Expected Output:**
```json
{
  "statusCode": 200,
  "body": "{\"success\": true, \"response\": \"*💰 Wheat - Financial Plan*\\n*Land*: 2 acres...\"}"
}
```

```bash
# Test 4: Finance Agent Lambda - Schemes
aws lambda invoke \
  --function-name kisaanmitra-finance-agent \
  --payload '{"body":"{\"type\":\"schemes\",\"crop\":\"wheat\",\"land_size\":2}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  schemes_response.json

cat schemes_response.json | python3 -m json.tool
```

```bash
# Test 5: Finance Agent Lambda - Loan Check
aws lambda invoke \
  --function-name kisaanmitra-finance-agent \
  --payload '{"body":"{\"type\":\"loan_check\",\"budget\":30000,\"income\":50000}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  loan_response.json

cat loan_response.json | python3 -m json.tool
```

---

## 🚀 Complete Deployment & Testing Flow

### Step 1: Setup Infrastructure (5 min)

```bash
# 1. Create DynamoDB tables
chmod +x infrastructure/*.sh
./infrastructure/setup_dynamodb.sh
./infrastructure/setup_finance_tables.sh

# 2. Update IAM permissions
./infrastructure/update_iam_permissions.sh
```

### Step 2: Deploy All Agents (5 min)

```bash
cd src/lambda

# Deploy Crop Agent (already deployed)
./deploy_lambda.sh

# Deploy Market Agent
./deploy_market_agent.sh

# Deploy Finance Agent
./deploy_finance_agent.sh

cd ../..
```

### Step 3: Run All Tests (2 min)

```bash
# Test all agents
./test_whatsapp_integration.sh
./test_market_agent.sh
./test_finance_agent.sh
```

### Step 4: Test Lambda Functions (3 min)

```bash
# Test Crop Agent
aws lambda invoke \
  --function-name kisaanmitra-crop-agent \
  --payload file://src/lambda/test_event.json \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  crop_response.json

# Test Market Agent
aws lambda invoke \
  --function-name kisaanmitra-market-agent \
  --payload '{"body":"{\"type\":\"price_check\",\"crop\":\"wheat\"}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  market_response.json

# Test Finance Agent
aws lambda invoke \
  --function-name kisaanmitra-finance-agent \
  --payload '{"body":"{\"type\":\"budget_plan\",\"crop\":\"wheat\",\"land_size\":2,\"income\":50000}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  finance_response.json

# View all responses
echo "=== Crop Agent ===" && cat crop_response.json
echo -e "\n=== Market Agent ===" && cat market_response.json
echo -e "\n=== Finance Agent ===" && cat finance_response.json
```

---

## 🧪 Advanced Testing Scenarios

### Scenario 1: Complete Farmer Journey

```bash
# 1. Farmer sends crop image (Crop Agent)
aws lambda invoke \
  --function-name kisaanmitra-crop-agent \
  --payload '{"body":"{\"entry\":[{\"changes\":[{\"value\":{\"messages\":[{\"from\":\"919876543210\",\"type\":\"image\",\"image\":{\"id\":\"test_media_id\"}}]}}]}]}"}' \
  --region ap-south-1 \
  response1.json

# 2. Farmer asks about market prices (Market Agent)
aws lambda invoke \
  --function-name kisaanmitra-market-agent \
  --payload '{"body":"{\"type\":\"price_check\",\"crop\":\"wheat\"}"}' \
  --region ap-south-1 \
  response2.json

# 3. Farmer requests budget plan (Finance Agent)
aws lambda invoke \
  --function-name kisaanmitra-finance-agent \
  --payload '{"body":"{\"type\":\"budget_plan\",\"crop\":\"wheat\",\"land_size\":2,\"income\":50000}"}' \
  --region ap-south-1 \
  response3.json
```

### Scenario 2: Different Crops Testing

```bash
# Test all 6 crop budgets
for crop in wheat rice cotton sugarcane onion potato; do
  echo "Testing $crop..."
  aws lambda invoke \
    --function-name kisaanmitra-finance-agent \
    --payload "{\"body\":\"{\\\"type\\\":\\\"budget_plan\\\",\\\"crop\\\":\\\"$crop\\\",\\\"land_size\\\":1,\\\"income\\\":50000}\"}" \
    --region ap-south-1 \
    ${crop}_response.json
  echo "✓ $crop tested"
done
```

### Scenario 3: Load Testing

```bash
# Test 10 concurrent requests
for i in {1..10}; do
  aws lambda invoke \
    --function-name kisaanmitra-crop-agent \
    --payload file://src/lambda/test_event.json \
    --region ap-south-1 \
    response_$i.json &
done
wait
echo "✓ Load test complete"
```

---

## 📊 Expected Test Results Summary

| Test | Expected Result | Pass Criteria |
|------|----------------|---------------|
| Crop Agent Code | 10/10 tests pass | All functions present |
| Crop Engine | 99% confidence | Disease detected |
| Crop Lambda | 200 status | Response received |
| Market Agent Code | 10/10 tests pass | All functions present |
| Market Lambda | 200 status | Price data returned |
| Finance Agent Code | 12/12 tests pass | All functions present |
| Finance Lambda | 200 status | Budget generated |
| Infrastructure | All tables created | No errors |
| Deployment | All functions deployed | No errors |

---

## 🐛 Troubleshooting

### Issue: Module not found
```bash
# Solution: Install dependencies
pip3 install boto3 urllib3 python-dotenv
```

### Issue: AWS credentials not configured
```bash
# Solution: Configure AWS CLI
aws configure
# Enter: Access Key, Secret Key, Region (ap-south-1)
```

### Issue: Lambda function not found
```bash
# Solution: Deploy the function first
cd src/lambda
./deploy_lambda.sh  # or deploy_market_agent.sh or deploy_finance_agent.sh
```

### Issue: API key not found
```bash
# Solution: Check .env file
cat .env | grep CROP_HEALTH_API_KEY
# If missing, add it to .env
```

### Issue: DynamoDB table not found
```bash
# Solution: Create tables
./infrastructure/setup_dynamodb.sh
./infrastructure/setup_finance_tables.sh
```

---

## ✅ Quick Verification Checklist

```bash
# Run this to verify everything is working
echo "🧪 Quick Verification"
echo "===================="

# 1. Check files exist
echo -n "Crop Agent: "
[ -f "src/crop_agent/crop_health_api.py" ] && echo "✅" || echo "❌"

echo -n "Market Agent: "
[ -f "src/market_agent/market_agent.py" ] && echo "✅" || echo "❌"

echo -n "Finance Agent: "
[ -f "src/finance_agent/finance_agent.py" ] && echo "✅" || echo "❌"

# 2. Check Lambda functions
echo -n "Crop Lambda: "
aws lambda get-function --function-name kisaanmitra-crop-agent --region ap-south-1 &>/dev/null && echo "✅" || echo "❌"

echo -n "Market Lambda: "
aws lambda get-function --function-name kisaanmitra-market-agent --region ap-south-1 &>/dev/null && echo "✅" || echo "❌"

echo -n "Finance Lambda: "
aws lambda get-function --function-name kisaanmitra-finance-agent --region ap-south-1 &>/dev/null && echo "✅" || echo "❌"

# 3. Check DynamoDB tables
echo -n "Conversations Table: "
aws dynamodb describe-table --table-name kisaanmitra-conversations --region ap-south-1 &>/dev/null && echo "✅" || echo "❌"

echo -n "Market Data Table: "
aws dynamodb describe-table --table-name kisaanmitra-market-data --region ap-south-1 &>/dev/null && echo "✅" || echo "❌"

echo -n "Finance Table: "
aws dynamodb describe-table --table-name kisaanmitra-finance --region ap-south-1 &>/dev/null && echo "✅" || echo "❌"

echo ""
echo "✅ Verification complete!"
```

---

## 🎯 Final Test Command

Run this single command to test everything:

```bash
# Complete test suite
echo "🧪 Testing All Agents..." && \
./test_whatsapp_integration.sh && \
./test_market_agent.sh && \
./test_finance_agent.sh && \
echo "" && \
echo "🎉 All tests passed! System is ready!" && \
echo "" && \
echo "📊 Test Summary:" && \
echo "   • Crop Agent: 10/10 ✅" && \
echo "   • Market Agent: 10/10 ✅" && \
echo "   • Finance Agent: 12/12 ✅" && \
echo "   • Total: 32/32 ✅"
```

---

**Testing Time: ~15 minutes total**
**Expected Result: 32/32 tests passing ✅**
