# Weather Location Fix - Sangli vs Pune Issue

## Problem
User (Parth Nikam, 919000000002) from Sangli district was getting weather forecasts for Pune instead of Sangli.

## Root Cause
The agents were trying to import the onboarding module incorrectly:
```python
from onboarding.farmer_onboarding import onboarding_manager  # ❌ Wrong
from hyperlocal.disease_tracker import hyperlocal_tracker    # ❌ Wrong
```

This caused import errors: `No module named 'onboarding'`

When the import failed, agents couldn't access the user's profile, so they fell back to defaults or message extraction.

## Solution Applied

### 1. Fixed All Import Paths
Changed imports in ALL agent files to match the deployment structure:

**All Agents (general, crop, market, finance):**
```python
from farmer_onboarding import onboarding_manager  # ✅ Correct
from disease_tracker import hyperlocal_tracker    # ✅ Correct
```

### 2. Made Profile Fetching Mandatory
Updated ALL agents to ALWAYS fetch user profile at the start:

**General Agent:**
- Fetches profile first
- Passes profile context to AI
- Uses district for weather queries

**Crop Agent:**
- Fetches profile with village, district, crops, land
- Uses district for weather context
- Passes full profile to hyperlocal system
- Includes profile in AI prompts

**Market Agent:**
- Fetches profile with village, district
- Uses district/state for market data
- Includes location context in AI prompts

**Finance Agent:**
- Fetches profile with name, village, district, land, crops
- Passes comprehensive profile context to AI
- Personalizes budget/loan/scheme recommendations

### 3. Priority Order for All Agents

**Weather Location:**
1. Profile District (from onboarding)
2. Message Location (AI extraction)
3. Default (Pune)

**Market Location:**
1. Profile District (from onboarding)
2. Message State (AI extraction)

**Crop Context:**
1. Profile: village, district, crops, land
2. Hyperlocal data (if available)
3. Weather context (using district)

### 4. Deployment
- Updated `deploy_v2.sh` to correctly package modules
- Deployed to Lambda function `whatsapp-llama-bot`
- Deployment timestamp: 2026-03-02 22:48 IST

## Files Modified
- `src/lambda/agents/general_agent.py` - Fixed imports, always fetch profile, use district for weather
- `src/lambda/agents/crop_agent.py` - Fixed imports, always fetch profile, comprehensive context
- `src/lambda/agents/market_agent.py` - Fixed imports, always fetch profile, use district for market
- `src/lambda/agents/finance_agent.py` - Fixed imports, always fetch profile, personalized advice
- `src/lambda/lambda_handler_v2.py` - Fixed imports
- `src/lambda/deploy_v2.sh` - Correct module packaging

## Expected Behavior Now

### Weather Queries
When user 919000000002 asks for weather:
- ✅ System reads profile → finds district = "Sangli"
- ✅ Uses "Sangli" for weather API call
- ✅ Returns Sangli weather forecast

### Crop Queries
- ✅ Loads: Parth Nikam, Nandani, Sangli, 20 acres, sugarcane
- ✅ Checks hyperlocal data for Nandani village
- ✅ Gets weather for Sangli district
- ✅ Provides personalized advice

### Market Queries
- ✅ Uses Sangli district for market data
- ✅ Provides location-specific prices

### Finance Queries
- ✅ Personalizes with: 20 acres, sugarcane, Sangli
- ✅ Recommends relevant schemes/loans

## Testing Instructions

1. Send any query to test profile loading
2. Check logs:
   ```bash
   aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep -E "Profile loaded|Using profile"
   ```
3. Expected log output:
   ```
   [GENERAL AGENT] Profile loaded: Parth Nikam from Nandani, Sangli
   [GENERAL AGENT] Using profile district: Sangli
   ```

## Status
✅ **DEPLOYED AND READY FOR TESTING**

All agents now ALWAYS use onboarding profile data for personalized responses.
