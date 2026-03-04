# Price Forecasting - Quick Start Guide

## ✅ System Status
- Daily training script: WORKING
- DynamoDB: 5 crops with 30-day forecasts
- WhatsApp bot: INTEGRATED
- Prophet models: TRAINED on 1800+ records

## 🚀 Quick Commands

### Run Training Manually
```bash
chcp 65001
python src/price_forecasting/daily_trainer.py
```

### Setup Daily Automation (Windows)
```powershell
.\scripts\setup_daily_training.ps1
```

### Test via WhatsApp
Send: `week forecast for wheat`

### Check DynamoDB
```bash
aws dynamodb scan --table-name kisaanmitra-price-forecasts --region ap-south-1
```

### View Logs
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --since 10m --region ap-south-1
```

## 📊 Supported Crops
1. Onion (₹1800/quintal)
2. Rice (₹2500/quintal)
3. Sugarcane (₹350/quintal)
4. Tomato (₹1200/quintal)
5. Wheat (₹2200/quintal)

## 🎯 How It Works
1. **6:00 AM Daily**: Script trains models, uploads to DynamoDB
2. **User Query**: Bot reads from DynamoDB (no training)
3. **Response**: <2 seconds with 30-day forecast

## 📁 Key Files
- `src/price_forecasting/daily_trainer.py` - Training script
- `scripts/setup_daily_training.ps1` - Automation setup
- `src/lambda/agents/general_agent.py` - WhatsApp detection
- `data/historical_prices/*.csv` - Historical data

## ✅ Verified Working
- [x] Prophet training (5/5 crops)
- [x] DynamoDB uploads (5/5 successful)
- [x] WhatsApp detection (logs confirmed)
- [x] 30-day forecasts generated
- [x] Confidence intervals included

## 🔧 Troubleshooting
- **Unicode error**: Run `chcp 65001` first
- **Prophet not found**: `pip install prophet`
- **WhatsApp 401**: Token expired, update in Lambda env vars
- **No forecasts**: Check DynamoDB table exists

---
**Ready to use!** Your daily training strategy is fully implemented.
