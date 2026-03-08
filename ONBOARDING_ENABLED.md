# Web Demo Onboarding - Now Enabled

## Status: ✅ Fixed and Working

Onboarding has been re-enabled for web demo users. New users will now go through the complete registration flow before accessing features.

## What Changed

### Before
- Onboarding was disabled for web demo
- Users could ask questions immediately without registration
- No user profiles were created

### After
- Full onboarding flow enabled
- New users must complete registration
- User profiles are saved to DynamoDB
- Personalized responses based on user location and crops

## Onboarding Flow

1. **Welcome Message**
   - User sends first message (e.g., "Hello")
   - System asks for name

2. **Name Collection**
   - User provides name
   - System asks for village

3. **Village Collection**
   - User provides village name
   - System asks for district

4. **District Collection**
   - User provides district
   - System asks for land size

5. **Land Size Collection**
   - User provides land in acres
   - System asks for soil type

6. **Soil Type Collection**
   - User selects soil type
   - System asks for irrigation method

7. **Irrigation Method**
   - User selects irrigation method
   - System asks for current crops

8. **Crops Collection**
   - User provides crops (comma-separated)
   - System asks for farming experience

9. **Experience Collection**
   - User provides years of experience
   - Onboarding complete!
   - Profile saved to DynamoDB
   - User can now access all features

## Testing

### Test New User Onboarding
```bash
# Step 1: Send first message
curl -X POST https://8zu6u7bc48.execute-api.ap-south-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user_456","type":"text","message":"Hello","language":"english"}'

# Response: "What is your name?"

# Step 2: Provide name
curl -X POST https://8zu6u7bc48.execute-api.ap-south-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user_456","type":"text","message":"John Doe","language":"english"}'

# Response: "Which village are you from?"

# Continue with village, district, land, soil, irrigation, crops, experience...
```

### Test Existing User
```bash
# Existing users skip onboarding and go directly to queries
curl -X POST https://8zu6u7bc48.execute-api.ap-south-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"919000000002","type":"text","message":"What is the weather?","language":"english"}'

# Response: Weather forecast for user's location
```

## Benefits

1. **Personalized Experience**: Responses tailored to user's location and crops
2. **Better Recommendations**: Weather, market prices, and advice specific to user's district
3. **User Profiles**: All data saved for future interactions
4. **Knowledge Graph**: User data contributes to KG dashboard
5. **Complete System**: Web demo now matches WhatsApp bot functionality

## User Data Collected

- Name
- Village
- District
- Land size (acres)
- Soil type
- Irrigation method
- Current crops
- Farming experience (years)
- Phone number (from user_id if provided)

## Data Storage

All user profiles are saved to:
- **DynamoDB Table**: `kisaanmitra-farmer-profiles`
- **Region**: `ap-south-1`
- **Key**: `phone_number` (user_id)

## Code Changes

**File**: `src/lambda/lambda_handler_web.py`

**Changes**:
- Re-enabled onboarding check for new users
- Added onboarding state validation
- Process onboarding messages through `onboarding_manager`
- Only allow queries after onboarding completion
- Added detailed logging for debugging

## Deployment

- **Lambda**: `whatsapp-llama-bot`
- **Handler**: `lambda_handler_unified.lambda_handler`
- **Size**: 517KB
- **Status**: Active
- **Deployed**: 2026-03-08 20:12 IST

## Testing URLs

- **Web Demo**: http://kisaanmitra-web-demo-1772974554.s3-website.ap-south-1.amazonaws.com/
- **API Endpoint**: https://8zu6u7bc48.execute-api.ap-south-1.amazonaws.com/prod/chat

## Notes

- Phone number modal on web demo is optional (Skip button available)
- If user skips phone number, a random user_id is generated
- Onboarding works with any user_id format
- Language can be switched during onboarding
- All responses are available in English and Hindi

---
Updated: 2026-03-08 20:15 IST
Status: Deployed and Working ✅
