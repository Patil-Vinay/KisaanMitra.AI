# KisaanMitra Refactoring Plan

## Current Problems
1. **50+ markdown documentation files** cluttering root directory
2. **Duplicate/unused modules** in src/lambda/
3. **Dead code** and commented blocks throughout
4. **Inconsistent error handling** and logging
5. **No clear separation** between core and optional features
6. **Messy folder structure** with test files mixed with source

## Refactoring Goals

### 1. Clean Root Directory
**Keep:**
- README.md (main documentation)
- requirements.txt (if needed)
- .env.example
- .gitignore

**Move to `/docs/archive/`:**
- All 50+ status/fix/completion markdown files

**Remove:**
- Duplicate deployment scripts
- Old test scripts
- Temporary files (whatsapp_deployment.zip, clear_user_onboarding.py)

### 2. Simplify src/lambda/ Structure

**Core Files (Keep & Clean):**
```
src/lambda/
├── lambda_handler.py          # Main entry point (renamed from lambda_whatsapp_kisaanmitra.py)
├── config.py                  # Environment variables & constants
├── utils/
│   ├── __init__.py
│   ├── whatsapp.py           # WhatsApp API calls
│   ├── dynamodb.py           # DynamoDB operations
│   └── anthropic.py          # Anthropic API client
├── agents/
│   ├── __init__.py
│   ├── router.py             # Agent routing logic
│   ├── crop.py               # Crop health agent
│   ├── market.py             # Market price agent
│   └── finance.py            # Finance agent
├── features/
│   ├── __init__.py
│   ├── onboarding.py         # User onboarding
│   ├── knowledge_graph.py    # Knowledge graph queries
│   └── interactive.py        # WhatsApp interactive messages
└── deploy.sh                 # Single deployment script
```

**Remove:**
- ai_orchestrator.py (unused)
- crop_yield_database.py (unused)
- enhanced_disease_detection.py (duplicate logic)
- reminder_manager.py (not implemented)
- weather_service.py (can be in utils)
- navigation_controller.py (overly complex)
- user_state_manager.py (can be simplified into DynamoDB utils)

### 3. Consolidate Agent Code

**Current:**
- src/crop_agent/crop_agent.py
- src/market_agent/market_agent.py
- src/finance_agent/finance_agent.py
- Logic duplicated in lambda file

**New:**
- All agent logic in `src/lambda/agents/`
- Single source of truth
- Remove duplicate implementations

### 4. Simplify Onboarding

**Current:**
- src/onboarding/farmer_onboarding.py (complex state machine)
- Separate DynamoDB tables

**New:**
- Simplified onboarding in `src/lambda/features/onboarding.py`
- Use single user profile table
- Remove unnecessary state tracking

### 5. Clean Knowledge Graph

**Keep:**
- demo/knowledge_graph_dummy_data.json (production data)
- src/lambda/features/knowledge_graph.py (simplified queries)

**Remove:**
- demo/knowledge_graph_dummy_data_backup.json
- demo/knowledge_graph_dummy_data_expanded.json
- src/knowledge_graph/village_graph.py (unused)
- Complex graph visualization scripts

### 6. Standardize Error Handling

**Pattern:**
```python
def function_name():
    try:
        # Logic here
        return success_response
    except SpecificError as e:
        logger.error(f"Error in function_name: {e}")
        return error_response
```

**Remove:**
- Inconsistent try/except blocks
- Silent error swallowing
- Debug print statements

### 7. Environment Variables

**Consolidate to config.py:**
```python
# Required
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Optional
AGMARKNET_API_KEY = os.getenv('AGMARKNET_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
```

### 8. Remove Unused Features

**Remove:**
- LangGraph routing (not working, adds complexity)
- Voice handler (not implemented)
- SOS handler (not implemented)
- Reminder system (not implemented)
- Navigation controller (overly complex)
- Crop comparison (not used)

### 9. Simplify Tests

**Keep:**
- tests/test_farmer_count_fix.py (if relevant)

**Remove:**
- Duplicate test scenarios
- Old test scripts
- Unused test utilities

### 10. Documentation Structure

```
docs/
├── README.md              # Main documentation
├── DEPLOYMENT.md          # How to deploy
├── API.md                 # API documentation
├── ARCHITECTURE.md        # System architecture
└── archive/               # All old status files
    └── *.md
```

## Implementation Steps

1. ✅ Create new folder structure
2. ✅ Extract and consolidate agent code
3. ✅ Simplify Lambda handler
4. ✅ Create utility modules
5. ✅ Consolidate onboarding
6. ✅ Clean knowledge graph
7. ✅ Remove unused files
8. ✅ Update deployment script
9. ✅ Test core flows
10. ✅ Update documentation

## Success Criteria

- ✅ Root directory has <10 files
- ✅ src/lambda/ has clear structure
- ✅ No duplicate code
- ✅ All core flows work:
  - WhatsApp message → Agent routing → Response
  - Onboarding flow
  - Knowledge graph queries
  - Market prices
  - Crop health
- ✅ Single deployment script
- ✅ Clear documentation

## Estimated Impact

**Before:**
- 50+ root files
- 15+ Lambda files
- Duplicate agent implementations
- ~5000 lines of Lambda code

**After:**
- <10 root files
- 10-12 Lambda files (organized)
- Single agent implementations
- ~2500 lines of Lambda code (50% reduction)
