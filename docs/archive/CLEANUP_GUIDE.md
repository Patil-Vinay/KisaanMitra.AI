# File Cleanup Guide - What to Keep & Delete

## Files Currently IN USE ✅

### 1. Source Code (KEEP)
```
src/lambda/lambda_sagemaker_forecaster.py          ✅ Main Lambda function
src/sagemaker_forecasting/
├── automl_trainer.py                              ✅ Creates SageMaker jobs
├── data_preparer.py                               ✅ Prepares data for training
└── batch_predictor.py                             ✅ Generates forecasts

src/price_forecasting/agmarknet_fetcher.py         ✅ Fetches live data (optional)
```

### 2. Data Files (KEEP)
```
data/historical_prices/
├── Tomato.csv                                     ✅ 5 years of real data
├── Onion.csv                                      ✅ 5 years of real data
├── Potato.csv                                     ✅ 5 years of real data
├── Wheat.csv                                      ✅ 5 years of real data
└── Rice.csv                                       ✅ 5 years of real data
```

### 3. Deployment Scripts (KEEP)
```
scripts/deploy_sagemaker_forecasting.ps1           ✅ Deploys Lambda
infrastructure/setup_sagemaker_forecasting.sh      ✅ Sets up AWS resources
```

### 4. Documentation (KEEP - Most Important)
```
FORECASTING_EXPLAINED.md                           ✅ How it works
REAL_DATA_DEPLOYMENT_COMPLETE.md                   ✅ Current status
AGMARKNET_API_SETUP.md                             ✅ API setup guide
```

---

## Files NOT IN USE (Can Delete) ❌

### 1. Old Prophet-based Files (DELETED)
```
src/lambda/lambda_daily_trainer.py                 ❌ Old Prophet trainer
src/lambda/lambda_price_updater.py                 ❌ Old price updater
src/price_forecasting/daily_trainer.py             ❌ Old Prophet code
src/price_forecasting/price_api.py                 ❌ Old API
src/price_forecasting/price_predictor.py           ❌ Old Prophet predictor
```
**Status**: Already deleted (marked with 'D' in git)

### 2. Old Setup Scripts (DELETED)
```
infrastructure/setup_daily_training_lambda.sh      ❌ Old Prophet setup
infrastructure/setup_price_forecasting.sh          ❌ Old setup
scripts/setup_daily_training.ps1                   ❌ Old training script
scripts/upload_forecasts_to_dynamodb.py            ❌ Old upload script
```
**Status**: Already deleted (marked with 'D' in git)

### 3. Temporary/Build Files (Can Delete)
```
lambda_package/                                    ❌ Build artifact (regenerated)
lambda_deployment.zip                              ❌ Deployment package (regenerated)
output.json                                        ❌ Test output
lambda-trust.json                                  ❌ Temporary IAM policy
sagemaker-trust.json                               ❌ Temporary IAM policy
```

### 4. Duplicate Documentation (Can Delete)
```
DEPLOYMENT_STATUS.md                               ❌ Outdated
DEPLOY_NOW.md                                      ❌ Outdated
FINAL_DEPLOYMENT_STEPS.md                          ❌ Outdated
SAGEMAKER_FORECASTING_DEPLOYED.md                  ❌ Superseded by REAL_DATA_DEPLOYMENT_COMPLETE.md
SAGEMAKER_FORECASTING_SOLUTION.md                  ❌ Duplicate
SAGEMAKER_IMPLEMENTATION_COMPLETE.md               ❌ Duplicate
SAGEMAKER_QUICK_START.md                           ❌ Duplicate
SAGEMAKER_WORKFLOW.md                              ❌ Duplicate
SIMPLE_FORECAST_SOLUTION.md                        ❌ Outdated
```

### 5. Temporary Scripts (Can Delete)
```
deploy_sagemaker_now.ps1                           ❌ One-time use
scripts/complete_deployment.ps1                    ❌ One-time use
scripts/finish_deployment.ps1                      ❌ One-time use
scripts/package_sagemaker_lambda.ps1               ❌ One-time use
```

---

## Cleanup Commands

### Delete Temporary Files:
```powershell
# Delete build artifacts
Remove-Item -Recurse -Force lambda_package
Remove-Item lambda_deployment.zip
Remove-Item output.json
Remove-Item lambda-trust.json
Remove-Item sagemaker-trust.json

# Delete duplicate documentation
Remove-Item DEPLOYMENT_STATUS.md
Remove-Item DEPLOY_NOW.md
Remove-Item FINAL_DEPLOYMENT_STEPS.md
Remove-Item SAGEMAKER_FORECASTING_DEPLOYED.md
Remove-Item SAGEMAKER_FORECASTING_SOLUTION.md
Remove-Item SAGEMAKER_IMPLEMENTATION_COMPLETE.md
Remove-Item SAGEMAKER_QUICK_START.md
Remove-Item SAGEMAKER_WORKFLOW.md
Remove-Item SIMPLE_FORECAST_SOLUTION.md

# Delete temporary scripts
Remove-Item deploy_sagemaker_now.ps1
Remove-Item scripts/complete_deployment.ps1
Remove-Item scripts/finish_deployment.ps1
Remove-Item scripts/package_sagemaker_lambda.ps1
```

### Commit Deletions to Git:
```powershell
# Stage all deletions
git add -A

# Commit
git commit -m "Cleanup: Remove old Prophet code and duplicate documentation"

# Push
git push
```

---

## Final Clean Structure

After cleanup, your project will look like:

```
KisaanMitra.AI/
├── data/
│   └── historical_prices/          ✅ 5 CSV files (real data)
│
├── src/
│   ├── lambda/
│   │   └── lambda_sagemaker_forecaster.py    ✅ Main Lambda
│   ├── sagemaker_forecasting/                ✅ SageMaker modules
│   └── price_forecasting/
│       └── agmarknet_fetcher.py              ✅ API integration
│
├── scripts/
│   └── deploy_sagemaker_forecasting.ps1      ✅ Deployment script
│
├── infrastructure/
│   └── setup_sagemaker_forecasting.sh        ✅ AWS setup
│
└── docs/
    ├── FORECASTING_EXPLAINED.md              ✅ How it works
    ├── REAL_DATA_DEPLOYMENT_COMPLETE.md      ✅ Current status
    └── AGMARKNET_API_SETUP.md                ✅ API guide
```

---

## Summary

**Currently Using**:
- 1 Lambda function: `kisaanmitra-sagemaker-forecaster`
- 5 CSV files with historical data
- 3 Python modules for SageMaker
- 1 EventBridge rule for weekly training

**Can Delete**:
- Old Prophet-based code (already deleted)
- Temporary build files
- Duplicate documentation (9 files)
- One-time deployment scripts (4 files)

**Total Cleanup**: ~15 files can be safely deleted

Would you like me to run the cleanup commands now?
