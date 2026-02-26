# Deploy Integrated System - Quick Guide

## What Changed

✅ **Backed up** your working onboarding code to `onboarding_backup_working/`
✅ **Pulled** latest code from GitHub (friend's changes)
✅ **Integrated** onboarding logic into new code
✅ **Preserved** all friend's enhancements (AI, market data, logging)

## Deploy Now

```powershell
cd src/lambda
./deploy_updated_onboarding.ps1
```

## What You Get

### Your Onboarding System (Preserved)
- Hindi onboarding flow (5 steps)
- AI information extraction
- DynamoDB user profiles
- Knowledge graph integration
- Works for ALL users

### Friend's Enhancements (Added)
- Enhanced debug logging
- Claude Sonnet 4 for budgets
- Real-time AgMarkNet prices
- Feasibility analysis
- Data source transparency

## Flow After Deployment

```
User sends "Hi"
    ↓
Check user status (ALWAYS FIRST)
    ↓
┌─────────────────┬──────────────────┬─────────────────┐
│   New User      │  In Onboarding   │  Completed User │
│                 │                  │                 │
│ Start           │ Continue         │ Route to        │
│ Onboarding      │ Onboarding       │ Agents          │
│ (Hindi)         │ (Hindi)          │ (Enhanced AI)   │
└─────────────────┴──────────────────┴─────────────────┘
```

## Test After Deployment

1. **New user test:**
   - Send "Hi" from new number
   - Should get: "🙏 नमस्ते! KisaanMitra में आपका स्वागत है!"

2. **Budget test:**
   - Complete onboarding
   - Ask: "onion budget in Kolhapur"
   - Should get: Enhanced budget with real market data

3. **Check logs:**
   ```powershell
   aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1
   ```
   - Should see: "🔧 ONBOARDING_AVAILABLE: True"
   - Should see: "👤 User Status: is_new=True"

## If Something Goes Wrong

Restore from backup:
```powershell
Copy-Item -Force onboarding_backup_working/lambda_whatsapp_kisaanmitra.py src/lambda/
cd src/lambda
./deploy_updated_onboarding.ps1
```

## Summary

Your onboarding + Friend's enhancements = Best of both worlds! 🚀
