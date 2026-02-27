# Comprehensive Refactoring Plan

## Analysis of Current Codebase

### Issues Identified

#### 1. Duplicate/Backup Files
- `onboarding_backup_working/` - Entire backup folder (REMOVE)
- `src/lambda/deployment_package/` - Old deployment artifacts (REMOVE)
- `src/lambda/test_extract/` - Test extraction folder (REMOVE)
- `lambda_whatsapp_kisaanmitra.py.backup` - Backup file (REMOVE)
- Multiple deployment zips (REMOVE)

#### 2. Excessive Documentation Files (30+ MD files)
Keep only:
- README.md (main)
- ARCHITECTURE.md
- docs/ folder (consolidated)

Remove:
- AI_MODEL_UPGRADE.md
- AI_POWERED_SYSTEM.md
- AWS_ENHANCEMENTS.md
- CRITICAL_FIXES_ANALYSIS.md
- CURRENT_ARCHITECTURE_DIAGRAM.md
- DEPLOY_*.md (multiple)
- DEPLOYMENT_*.md (multiple)
- GIT_COLLABORATION_GUIDE.md
- GROUND_ZERO_REBUILD_COMPLETE.md
- HACKATHON_*.md (multiple)
- IMPLEMENTATION_SUMMARY.md
- INTEGRATION_COMPLETE.md
- ONBOARDING_*.md (multiple)
- README_*.md (duplicates)
- REMAINING_FEATURES_GUIDE.md
- UPDATE_SUMMARY.md

#### 3. Unused Lambda Functions
- `lambda_crop_agent.py` - Not used (main handler is lambda_whatsapp_kisaanmitra.py)
- Separate agent Lambdas not deployed

#### 4. Unused Features/Modules
- `crop_comparison.py` - Not integrated
- `voice_handler.py` - Not implemented
- `sos_handler.py` - Not fully implemented
- `agent_router.py` - Replaced by ai_orchestrator.py

#### 5. Test/Debug Files
- `test_event.json`
- `test_onboarding_flow.py`
- `response.json`
- `lambda_logs*.txt` (3 files)
- `log-events-viewer-result.csv`
- `clear_*.sh/py` files

#### 6. Unused Scripts
- Multiple deploy scripts (consolidate to one)
- PowerShell scripts (.ps1) - Not needed on macOS

#### 7. Generated Artifacts
- `generated-diagrams/` - Keep in assets only
- `*.zip` files in src/lambda/

## Refactoring Strategy

### Phase 1: Remove Dead Code
1. Delete backup folders
2. Delete duplicate documentation
3. Delete test/debug files
4. Delete unused deployment artifacts

### Phase 2: Consolidate Core Files
1. Merge duplicate helper functions
2. Standardize error handling
3. Clean up imports
4. Remove debug print statements

### Phase 3: Restructure Folders
```
kisaanmitra/
├── src/
│   ├── lambda/
│   │   ├── handlers/
│   │   │   └── whatsapp_handler.py (main)
│   │   ├── agents/
│   │   │   ├── ai_orchestrator.py
│   │   │   ├── disease_detector.py
│   │   │   └── state_manager.py
│   │   ├── services/
│   │   │   ├── whatsapp_service.py
│   │   │   ├── weather_service.py
│   │   │   └── reminder_service.py
│   │   ├── utils/
│   │   │   └── market_data.py
│   │   └── deploy.sh
│   ├── onboarding/
│   │   └── farmer_onboarding.py
│   └── knowledge_graph/
│       └── village_graph.py
├── infrastructure/
│   ├── setup_tables.sh (consolidated)
│   └── update_permissions.sh
├── docs/
│   ├── README.md
│   ├── SETUP.md
│   └── API.md
├── scripts/
│   └── test/
│       └── test_integration.sh
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

### Phase 4: Code Quality
1. Remove all commented code
2. Standardize function naming
3. Add type hints
4. Improve error messages
5. Remove excessive logging

## Files to DELETE

### Backup/Duplicate Folders
- `onboarding_backup_working/` (entire folder)
- `src/lambda/deployment_package/` (entire folder)
- `src/lambda/test_extract/` (entire folder)
- `src/lambda/package/` (if exists)

### Documentation (Keep only essential)
DELETE:
- AI_MODEL_UPGRADE.md
- AI_POWERED_SYSTEM.md
- AWS_ENHANCEMENTS.md
- CRITICAL_FIXES_ANALYSIS.md
- CURRENT_ARCHITECTURE_DIAGRAM.md
- DEPLOY_INTEGRATED_SYSTEM.md
- DEPLOY_NOW.md
- DEPLOY_ONBOARDING_UPDATE.md
- DEPLOYMENT_COMPLETE_2026-02-27.md
- DEPLOYMENT_SUCCESS_ALL_FEATURES.md
- DEPLOYMENT_SUCCESS.md
- GIT_COLLABORATION_GUIDE.md
- GROUND_ZERO_REBUILD_COMPLETE.md
- HACKATHON_FEATURES.md
- HACKATHON_STATUS.md
- IMPLEMENTATION_SUMMARY.md
- INTEGRATION_COMPLETE.md
- ONBOARDING_ARCHITECTURE.md
- ONBOARDING_INTEGRATED.md
- ONBOARDING_QUICKSTART.md
- ONBOARDING_UPDATE.md
- README_ONBOARDING.md
- README_UPDATE.md
- REMAINING_FEATURES_GUIDE.md
- UPDATE_SUMMARY.md

### Test/Debug Files
- lambda_logs_new.txt
- lambda_logs_raw.txt
- lambda_logs.txt
- log-events-viewer-result (1).csv
- clear_all_dynamodb.sh
- clear_all_users.ps1
- clear_dynamodb.py
- src/lambda/test_event.json
- src/lambda/response.json
- src/lambda/test_onboarding_flow.py
- src/lambda/lambda_whatsapp_kisaanmitra.py.backup

### Deployment Artifacts
- src/lambda/*.zip (all zip files)
- src/lambda/trust-policy.json (move to infrastructure)

### Unused Scripts
- src/lambda/deploy_finance_agent.sh
- src/lambda/deploy_market_agent.sh
- src/lambda/deploy_lambda.sh
- src/lambda/deploy_onboarding.ps1
- src/lambda/deploy_updated_onboarding.ps1
- src/lambda/deploy_updated_onboarding.sh
- src/lambda/deploy_with_onboarding.sh
- setup_git_protection.ps1

### Unused Code Files
- src/lambda/lambda_crop_agent.py
- src/lambda/agent_router.py (replaced by ai_orchestrator)
- src/lambda/crop_comparison.py (not integrated)
- src/lambda/voice_handler.py (not implemented)
- src/lambda/sos_handler.py (not fully implemented)

### Generated/Asset Duplicates
- generated-diagrams/ (keep only in assets/)
- index.html (if not used)
- privacy-policy.html (if not used)

### Other
- design.md (duplicate)
- requirements.md (use requirements.txt)

## Files to KEEP & REFACTOR

### Core Lambda Files
- lambda_whatsapp_kisaanmitra.py → handlers/whatsapp_handler.py
- ai_orchestrator.py → agents/ai_orchestrator.py
- enhanced_disease_detection.py → agents/disease_detector.py
- user_state_manager.py → agents/state_manager.py
- whatsapp_interactive.py → services/whatsapp_service.py
- weather_service.py → services/weather_service.py
- reminder_manager.py → services/reminder_service.py
- market_data_sources.py → utils/market_data.py

### Infrastructure
- Consolidate all setup_*.sh into setup_tables.sh
- Keep deploy_whatsapp.sh as deploy.sh

### Documentation
- README.md (main)
- ARCHITECTURE.md
- WHATSAPP_SETUP.md → docs/SETUP.md
- docs/AWS_SETUP_GUIDE.md
- docs/DEPLOYMENT_CHECKLIST.md

## Execution Plan

1. Create backup branch
2. Delete all identified files
3. Restructure remaining files
4. Clean up code (remove debug logs, comments)
5. Test core flows
6. Commit with detailed message
7. Update README with new structure

## Success Criteria

✅ Codebase reduced by 60%+
✅ No duplicate files
✅ Clear folder structure
✅ All core flows work
✅ Easy to understand and maintain
