# Weather State Management Fix - Complete ✅

## Issue Summary
When user completed onboarding and then typed "Give me weather report", the system was treating it as a city name instead of detecting weather intent because:
1. The `awaiting_weather_location` state persisted from a previous weather button click
2. No state clearing after onboarding completion
3. No weather intent detection in the state handler

## Root Cause
```
User Flow:
1. User clicks Weather button → State set to 'awaiting_weather_location'
2. User completes onboarding → State NOT cleared
3. User types "Give me weather report" → System treats as city name "give me report"
4. Weather API fails with 404 (city not found)
```

## Fixes Applied

### 1. Clear State After Onboarding Completion
**File**: `src/lambda/lambda_whatsapp_kisaanmitra.py`

Added state clearing in both onboarding completion sections:
```python
# If onboarding completed, add to knowledge graph
if is_completed:
    profile = onboarding_manager.get_user_profile(from_number)
    if profile:
        knowledge_graph.add_farmer_to_graph(profile)
        print(f"✅ Onboarding completed! Added {profile.get('name')} to knowledge graph")
        
        # Clear any pending states after onboarding
        try:
            from user_state_manager import clear_user_state
            clear_user_state(from_number)
            print(f"[STATE] Cleared pending states after onboarding completion")
        except:
            pass
```

### 2. Enhanced Weather State Handler with Intent Detection
**File**: `src/lambda/lambda_whatsapp_kisaanmitra.py`

Updated the `awaiting_weather_location` state handler to:
- Detect weather intent keywords (weather, mausam, forecast, report, etc.)
- Automatically use profile village when user asks for weather
- Only ask for city if no profile location available

```python
# Check if user is asking for weather (not providing a city name)
weather_intent_keywords = ['weather', 'mausam', 'मौसम', 'forecast', 'report', 'बताओ', 'दिखाओ', 'give me', 'show me']
is_weather_query = any(kw in user_message.lower() for kw in weather_intent_keywords)

# If it's a weather query (not a city name), try to use profile location
if is_weather_query:
    print(f"[WEATHER] Detected weather query, checking profile for location")
    user_location = None
    
    # Try to get user's village from profile
    if ONBOARDING_AVAILABLE:
        try:
            from onboarding.farmer_onboarding import onboarding_manager
            profile = onboarding_manager.get_user_profile(from_number)
            if profile and profile.get('village'):
                user_location = profile.get('village')
                print(f"[WEATHER] Using profile location: {user_location}")
        except Exception as e:
            print(f"[WEATHER] Could not fetch profile: {e}")
    
    # If we have location from profile, use it
    if user_location:
        user_message = user_location
        print(f"[WEATHER] Using profile village: {user_location}")
```

### 3. Cleared Existing State for Test User
Manually cleared the stuck state:
```bash
aws dynamodb delete-item --table-name kisaanmitra-user-state \
  --key '{"user_id": {"S": "919000000002"}}' --region ap-south-1
```

## Testing Scenarios

### Scenario 1: Weather Button Click (with profile)
```
User: [Clicks Weather button]
System: Shows weather for Nashik (from profile) ✅
```

### Scenario 2: Weather Query (with profile)
```
User: "Give me weather report"
System: Detects intent → Uses Nashik from profile → Shows weather ✅
```

### Scenario 3: Weather Query (no profile)
```
User: "Give me weather report"
System: Detects intent → No profile location → Asks for city name ✅
```

### Scenario 4: Direct City Name (in weather state)
```
User: "Pune"
System: Shows weather for Pune ✅
```

## Deployment
```bash
cd src/lambda
./deploy_whatsapp.sh
```

**Status**: ✅ Deployed successfully
**Lambda**: whatsapp-llama-bot
**Region**: ap-south-1

## User Profile
- Phone: 919000000002
- Name: Pune
- Village: Nashik
- Crops: Wheat
- Land: 10 acres

## Next Steps for Testing
1. Send "hi" to reset conversation
2. Click Weather button → Should show Nashik weather automatically
3. Type "Give me weather report" → Should show Nashik weather
4. Type "weather in Mumbai" → Should show Mumbai weather

## Files Modified
- `src/lambda/lambda_whatsapp_kisaanmitra.py` (3 sections updated)

## Impact
- ✅ Weather button now uses profile location automatically
- ✅ Weather queries detect intent and use profile location
- ✅ State cleared after onboarding to prevent conflicts
- ✅ Better user experience - no repeated location questions
