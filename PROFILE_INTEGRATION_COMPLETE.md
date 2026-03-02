# Profile Integration Complete - All Agents Now Use Onboarding Data

## Overview
All agents (General, Crop, Market, Finance) now ALWAYS fetch and use user profile data from the onboarding system for personalized responses.

## Changes Made

### 1. Fixed Module Imports (All Agents)

**Before (Broken):**
```python
from onboarding.farmer_onboarding import onboarding_manager  # ❌ Import Error
from hyperlocal.disease_tracker import hyperlocal_tracker    # ❌ Import Error
```

**After (Working):**
```python
from farmer_onboarding import onboarding_manager  # ✅ Works
from disease_tracker import hyperlocal_tracker    # ✅ Works
```

### 2. Mandatory Profile Fetching

All agents now follow this pattern:

```python
# ALWAYS fetch user profile first
profile = None
if ONBOARDING_AVAILABLE and user_id != "unknown":
    try:
        profile = onboarding_manager.get_user_profile(user_id)
        if profile:
            name = profile.get('name')
            village = profile.get('village')
            district = profile.get('district')
            crops = profile.get('current_crops')
            land = profile.get('land_acres')
            # Use this data for personalization
    except Exception as e:
        print(f"[AGENT] Could not get profile: {e}")
```

## Agent-Specific Implementations

### General Agent
**Profile Usage:**
- Fetches: name, village, district, crops, land
- Uses district for weather queries (Priority 1)
- Passes profile context to AI for general queries

**Example Log:**
```
[GENERAL AGENT] Profile loaded: Parth Nikam from Nandani, Sangli
[GENERAL AGENT] Using profile district: Sangli
```

**Weather Priority:**
1. Profile district → "Sangli"
2. Message location → extracted by AI
3. Default → "Pune"

### Crop Agent
**Profile Usage:**
- Fetches: name, village, district, crops, land
- Uses village for hyperlocal disease data
- Uses district for weather context
- Passes full profile to AI

**Example Log:**
```
[CROP AGENT] Profile loaded: Parth Nikam from Nandani, Sangli. Crops: sugarcane
[CROP AGENT] Checking hyperlocal data for Nandani, sugarcane
[CROP AGENT] Fetching weather for Sangli
```

**Context Priority:**
1. Hyperlocal community data (village-specific)
2. Weather context (district-specific)
3. AI with profile context

### Market Agent
**Profile Usage:**
- Fetches: village, district
- Uses district for market data location
- Passes location context to AI

**Example Log:**
```
[MARKET AGENT] Profile loaded: Nandani, Sangli
[MARKET AGENT] Using market data for sugarcane in Sangli
```

**Location Priority:**
1. Profile district → "Sangli"
2. Message state → extracted by AI

### Finance Agent
**Profile Usage:**
- Fetches: name, village, district, land, crops
- Passes comprehensive profile to AI
- Personalizes budget/loan/scheme recommendations

**Example Log:**
```
[FINANCE AGENT] Profile loaded: Parth Nikam from Nandani, Sangli
```

**Profile Context Example:**
```
User Profile: Parth Nikam from Nandani, Sangli. Land: 20 acres. Growing: sugarcane.
```

## Benefits

### 1. Personalized Responses
Every response now considers:
- User's location (village, district)
- Current crops
- Land size
- Farming experience

### 2. Location-Specific Data
- Weather: Uses user's district automatically
- Market: Uses user's district/state for prices
- Hyperlocal: Uses user's village for community data

### 3. No Repeated Questions
System already knows:
- "You know my location" → Yes, Sangli
- "My crop" → Yes, sugarcane
- "My land" → Yes, 20 acres

### 4. Better Context
AI receives full profile context:
```
User Profile: Parth Nikam from Nandani, Sangli. 
Land: 20 acres. Growing: sugarcane.
```

## Testing

### Test User Profile
```json
{
  "user_id": "919000000002",
  "name": "Parth Nikam",
  "village": "Nandani",
  "district": "Sangli",
  "land_acres": "20",
  "current_crops": "sugarcane",
  "soil_type": "Black Cotton Soil",
  "water_source": "Canal"
}
```

### Test Scenarios

**1. Weather Query:**
```
User: "Give me weather report"
Expected: Weather for Sangli (not Pune)
Log: [GENERAL AGENT] Using profile district: Sangli
```

**2. Crop Query:**
```
User: "How to care for my crop?"
Expected: Advice for sugarcane in Sangli
Log: [CROP AGENT] Profile loaded: Parth Nikam from Nandani, Sangli. Crops: sugarcane
```

**3. Market Query:**
```
User: "What's the price?"
Expected: Sugarcane prices in Sangli/Maharashtra
Log: [MARKET AGENT] Using market data for sugarcane in Sangli
```

**4. Finance Query:**
```
User: "I need a loan"
Expected: Loan options for 20 acres sugarcane farmer
Log: [FINANCE AGENT] Profile loaded: Parth Nikam from Nandani, Sangli
```

## Deployment Details

**Files Modified:**
- `src/lambda/agents/general_agent.py`
- `src/lambda/agents/crop_agent.py`
- `src/lambda/agents/market_agent.py`
- `src/lambda/agents/finance_agent.py`
- `src/lambda/lambda_handler_v2.py`

**Deployment:**
- Function: `whatsapp-llama-bot`
- Region: `ap-south-1`
- Timestamp: 2026-03-02 22:48 IST
- Status: ✅ Active

## Monitoring

**Check Profile Loading:**
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep "Profile loaded"
```

**Check Profile Usage:**
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep "Using profile"
```

**Check Import Errors:**
```bash
aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1 | grep "not available"
```

## Status
✅ **COMPLETE AND DEPLOYED**

All agents now intelligently use onboarding profile data for personalized, context-aware responses.
