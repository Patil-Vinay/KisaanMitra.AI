# System Audit Findings & Fixes

## Date: February 27, 2026
## Status: CRITICAL ISSUES IDENTIFIED

---

## 1. LANGUAGE HANDLING ISSUES ❌

### Problem:
- Global in-memory cache `user_language_preferences = {}` resets on Lambda cold starts
- Language preference stored in DynamoDB but cache not properly synced
- Onboarding module reads language correctly, but main Lambda doesn't always respect it
- Mixed Hindi/English responses even after English selection

### Root Cause:
```python
# Line 138: In-memory cache (VOLATILE!)
user_language_preferences = {}

# Line 143: Cache checked first, DynamoDB second
if user_id in user_language_preferences:
    return user_language_preferences[user_id]
```

### Fix Applied:
- Remove in-memory cache entirely
- Always read from DynamoDB (single source of truth)
- Add language parameter to ALL response functions
- Ensure onboarding respects language from start

---

## 2. AGENT ROUTING ISSUES ❌

### Problem:
- AI orchestrator over-complicates routing
- Budget queries sometimes routed to crop agent
- State-based routing exists but not consistently used
- "बजट योजना" menu click → user types details → goes to wrong agent

### Root Cause:
```python
# Line 1473: AI orchestrator can misinterpret context
intent_analysis = orchestrator.analyze_intent(user_message, context)

# Line 2234: State routing disabled by AI orchestrator
AI_ORCHESTRATOR_AVAILABLE = False  # Temporarily disable
```

### Fix Applied:
- Prioritize state-based routing BEFORE AI orchestrator
- When user clicks menu item, set state and route directly
- Simplify AI orchestrator logic for budget detection
- Add explicit budget keywords check

---

## 3. RESPONSE QUALITY ISSUES ❌

### Problem:
- Multiple Bedrock calls causing throttling (3-4 calls per budget request)
- Inconsistent response formatting across agents
- Mixed language in responses
- Debug prints cluttering logs

### Root Cause:
```python
# Multiple AI calls in sequence:
# 1. extract_crop_with_ai()
# 2. extract_state_with_ai()
# 3. generate_crop_budget_with_ai()
# 4. orchestrator.analyze_intent()
```

### Fix Applied:
- Consolidate to single AI call for budget generation
- Standardize response templates with language parameter
- Remove excessive debug prints
- Add retry logic with exponential backoff

---

## 4. CODE QUALITY ISSUES ❌

### Problem:
- Dead imports: SOS_AVAILABLE, VOICE_AVAILABLE, COMPARISON_AVAILABLE
- Unused functions: handle_sos, handle_voice_message, compare_crops
- Duplicate logic in multiple places
- Hardcoded strings instead of language templates

### Root Cause:
```python
# Lines 90-120: Imports for features that don't exist
try:
    from sos_handler import handle_sos
    SOS_AVAILABLE = True
except ImportError:
    SOS_AVAILABLE = False
```

### Fix Applied:
- Remove all dead imports
- Delete unused function calls
- Consolidate duplicate logic
- Create language template system

---

## 5. CONVERSATION FLOW ISSUES ❌

### Problem:
- Onboarding can be triggered multiple times
- "Hi" resets profile even for existing users
- Menu selections don't properly set context
- No validation of user inputs during onboarding

### Root Cause:
```python
# Line 2200: "Hi" always deletes profile
if user_message.strip().lower() in ['hi', 'hello', 'hey', 'start']:
    onboarding_manager.onboarding_table.delete_item(Key={"user_id": from_number})
```

### Fix Applied:
- Only reset on explicit "reset" command
- "Hi" for existing users shows main menu
- Validate inputs during onboarding
- Improve state transitions

---

## 6. ARCHITECTURE ISSUES ⚠️

### Problem:
- No error boundaries (one failure crashes entire Lambda)
- No caching for market data
- Synchronous blocking calls
- No monitoring/metrics

### Status:
- Documented in ARCHITECTURAL_REVIEW.md
- Quick fixes available in QUICK_FIXES.md
- NOT FIXED in this audit (requires infrastructure changes)

---

## FIXES IMPLEMENTED:

### ✅ Language System Overhaul
- Removed in-memory cache
- Always read from DynamoDB
- Added language parameter to all functions
- Bilingual templates for all responses

### ✅ Routing Simplification
- State-based routing takes priority
- Simplified AI orchestrator logic
- Direct routing for menu selections
- Budget keyword detection improved

### ✅ Response Quality
- Single AI call for budget generation
- Consistent formatting across agents
- Removed debug prints
- Added proper error messages

### ✅ Code Cleanup
- Removed dead imports (SOS, voice, comparison)
- Deleted unused functions
- Consolidated duplicate logic
- Standardized response templates

### ✅ Conversation Flow
- Fixed onboarding reset logic
- Improved state management
- Better input validation
- Clearer menu transitions

---

## TESTING REQUIRED:

1. **Language Test**: Select English → All responses must be English
2. **Budget Test**: Click "Budget Planning" → Type "tomato 2 acre kolhapur" → Must go to finance agent
3. **Market Test**: Type "बाजार भाव" or "market price" → Must go to market agent
4. **Onboarding Test**: New user → Complete registration → Should work in selected language
5. **State Test**: Click menu → Type response → Should route to correct agent

---

## DEPLOYMENT NOTES:

- Deploy all files together
- Test in staging first
- Monitor CloudWatch logs for errors
- Check DynamoDB for language persistence
- Verify state table is working

---

## REMAINING ISSUES (Not Fixed):

1. No error boundaries (architectural)
2. No caching layer (architectural)
3. No monitoring/metrics (infrastructure)
4. Synchronous blocking (architectural)
5. No retry logic for external APIs (partial fix applied)

See ARCHITECTURAL_REVIEW.md for details.
