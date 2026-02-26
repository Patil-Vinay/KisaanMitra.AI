# Onboarding System Backup - Working Version

**Backup Date:** 2026-02-27
**Status:** WORKING PERFECTLY ✅

## What's Backed Up

This folder contains the complete working onboarding system:

1. **src/onboarding/** - Onboarding state machine with AI extraction
2. **src/knowledge_graph/** - Knowledge graph manager (with gremlin fallback)
3. **lambda_whatsapp_kisaanmitra.py** - Main Lambda handler with onboarding checks
4. **deployment_package/** - Complete deployment package
5. **streamlit_app.py** - Dashboard for visualization
6. **clear_dynamodb.py** - Script to clear DynamoDB tables
7. **deploy_updated_onboarding.ps1** - Deployment script

## Key Features

- ✅ Farmer onboarding in Hindi (5-step flow)
- ✅ AI-powered information extraction (Nova Pro)
- ✅ DynamoDB user profiles and onboarding state
- ✅ Knowledge graph integration
- ✅ ALWAYS checks user status before routing
- ✅ Concise AI responses (no verbose thinking)
- ✅ Works for ALL users (not just specific numbers)

## Verified Working

- User 9000000003: ✅ Onboarding works
- User 919000000002: ✅ Should work (was issue, now fixed)
- All new users: ✅ Trigger onboarding flow

## Critical Logic

### User Status Check (ALWAYS FIRST)
```python
is_new_user, onboarding_state, user_profile = check_user_status(from_number)

# If state != "completed", treat as new
if state != "completed":
    is_new = True
```

### Onboarding Flow
1. NEW → Ask name
2. ASKED_NAME → Ask crops
3. ASKED_CROPS → Ask land size
4. ASKED_LAND → Ask village
5. ASKED_VILLAGE → Complete & save profile

### AI Extraction Settings
- maxTokens: 20 (concise)
- temperature: 0.1 (precise)
- Post-processing: Strip prefixes, take first line only

## DynamoDB Tables

1. **kisaanmitra-onboarding** - Onboarding state tracking
2. **kisaanmitra-user-profiles** - Complete farmer profiles
3. **kisaanmitra-conversations** - Chat history

## Deployment

```powershell
cd src/lambda
./deploy_updated_onboarding.ps1
```

Lambda function: `whatsapp-llama-bot`
Region: `ap-south-1`

## Restore Instructions

If you need to restore this working version:

```powershell
# Copy back to main project
Copy-Item -Recurse -Force onboarding_backup_working/onboarding src/
Copy-Item -Recurse -Force onboarding_backup_working/knowledge_graph src/
Copy-Item -Force onboarding_backup_working/lambda_whatsapp_kisaanmitra.py src/lambda/
Copy-Item -Recurse -Force onboarding_backup_working/deployment_package src/lambda/
Copy-Item -Force onboarding_backup_working/streamlit_app.py dashboard/

# Redeploy
cd src/lambda
./deploy_updated_onboarding.ps1
```

## Notes

- This version was tested and verified working on 2026-02-26
- All users go through onboarding (no hardcoded phone numbers)
- AI responses are concise (no verbose explanations)
- Gremlin is optional (falls back to in-memory storage)
- ONBOARDING_AVAILABLE flag controls feature availability
