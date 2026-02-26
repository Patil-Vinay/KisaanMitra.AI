# Quick Test Reference

## 🚀 One Command to Test Everything

```bash
./test_all.sh
```

This runs all 32 tests across 3 agents in ~2 minutes.

---

## 📋 Individual Agent Tests

### Crop Agent (10 tests)
```bash
./test_whatsapp_integration.sh
```

### Market Agent (10 tests)
```bash
./test_market_agent.sh
```

### Finance Agent (12 tests)
```bash
./test_finance_agent.sh
```

---

## 🧪 Test with Real Data

### Test Crop Engine
```bash
python3 test_crop_engine.py
```

### Test Finance Functions
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'src/finance_agent')
from finance_agent import get_crop_budget_template

budget = get_crop_budget_template("wheat", 2)
print(f"Cost: ₹{budget['total_cost']:,}")
print(f"Profit: ₹{budget['expected_profit']:,}")
print(f"ROI: {budget['roi_percent']}%")
EOF
```

---

## ☁️ Test Lambda Functions (After Deployment)

### Crop Agent
```bash
aws lambda invoke \
  --function-name kisaanmitra-crop-agent \
  --payload file://src/lambda/test_event.json \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

### Market Agent
```bash
aws lambda invoke \
  --function-name kisaanmitra-market-agent \
  --payload '{"body":"{\"type\":\"price_check\",\"crop\":\"wheat\"}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

### Finance Agent
```bash
aws lambda invoke \
  --function-name kisaanmitra-finance-agent \
  --payload '{"body":"{\"type\":\"budget_plan\",\"crop\":\"wheat\",\"land_size\":2,\"income\":50000}"}' \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  response.json && cat response.json
```

---

## ✅ Quick Verification

```bash
# Check if everything is ready
echo "Crop Agent:" && [ -f "src/crop_agent/crop_health_api.py" ] && echo "✅" || echo "❌"
echo "Market Agent:" && [ -f "src/market_agent/market_agent.py" ] && echo "✅" || echo "❌"
echo "Finance Agent:" && [ -f "src/finance_agent/finance_agent.py" ] && echo "✅" || echo "❌"
```

---

## 📊 Expected Results

| Test | Time | Expected |
|------|------|----------|
| Crop Agent | 30s | 10/10 ✅ |
| Market Agent | 30s | 10/10 ✅ |
| Finance Agent | 30s | 12/12 ✅ |
| **Total** | **2min** | **32/32 ✅** |

---

## 🐛 Quick Fixes

### Missing dependencies?
```bash
pip3 install boto3 urllib3 python-dotenv
```

### AWS not configured?
```bash
aws configure
# Region: ap-south-1
```

### Tests not executable?
```bash
chmod +x test_*.sh
```

---

## 🎯 Full Testing Flow

```bash
# 1. Test all agents locally
./test_all.sh

# 2. Deploy to AWS (if not done)
./infrastructure/setup_dynamodb.sh
./infrastructure/setup_finance_tables.sh
cd src/lambda && ./deploy_lambda.sh && ./deploy_market_agent.sh && ./deploy_finance_agent.sh

# 3. Test Lambda functions
# (Use commands from "Test Lambda Functions" section above)
```

---

**Total Time: 2 minutes for local tests, 15 minutes for full deployment + testing**
