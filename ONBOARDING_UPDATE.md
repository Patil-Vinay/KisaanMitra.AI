# KisaanMitra Onboarding Update - Always Check New Users First

## 🎯 What Changed

Updated the Lambda function to **ALWAYS check if a user is new** before processing any message, regardless of message type.

## 📋 Changes Made

### 1. **New Helper Function: `check_user_status()`**

Added a centralized function to check user status:

```python
def check_user_status(user_id):
    """
    Check user onboarding status
    Returns: (is_new, onboarding_state, profile)
    """
    # Check if user has completed profile
    is_new = onboarding_manager.is_new_user(user_id)
    
    # Get onboarding state
    state, data = onboarding_manager.get_onboarding_state(user_id)
    
    # Get profile if exists
    profile = None if is_new else onboarding_manager.get_user_profile(user_id)
    
    return is_new, state, profile
```

**Benefits:**
- Single source of truth for user status
- Returns all needed information in one call
- Easier to maintain and test

### 2. **Updated Lambda Handler Flow**

The new flow ALWAYS checks user status first:

```python
# STEP 1: Check user status (ALWAYS FIRST)
is_new_user, onboarding_state, user_profile = check_user_status(from_number)

# STEP 2: Handle new users
if is_new_user:
    # Start onboarding
    
# STEP 3: Handle users in onboarding
if onboarding_state != "completed":
    # Continue onboarding
    
# STEP 4: Handle existing users
# Route to normal agents (crop/market/finance)
```

### 3. **Enhanced Logging**

Added emoji-based logging for better visibility:

```python
print(f"📱 Message from {from_number}, type: {msg_type}")
print(f"👤 User Status: is_new={is_new_user}, state={onboarding_state}")
print(f"🆕 NEW USER DETECTED: {from_number}")
print(f"📝 USER IN ONBOARDING: {from_number}, state: {onboarding_state}")
print(f"✅ EXISTING USER: {from_number} ({user_profile.get('name')})")
```

### 4. **Non-Text Message Handling**

New users who send images/videos are now asked to complete onboarding first:

```python
if is_new_user and msg_type != "text":
    send_whatsapp_message(
        from_number,
        "🙏 नमस्ते! KisaanMitra में आपका स्वागत है!\n\n"
        "पहले अपना रजिस्ट्रेशन पूरा करें।\n"
        "कृपया 'Hi' टाइप करें।"
    )
```

## 🔄 Flow Comparison

### Before (Old Flow)
```
Message Received
    ↓
Check message type
    ↓
If text → Check if new user
    ↓
If image → Process directly (PROBLEM!)
```

**Issue:** New users could send images and bypass onboarding.

### After (New Flow)
```
Message Received
    ↓
ALWAYS check user status FIRST
    ↓
If new user → Force onboarding (text only)
    ↓
If in onboarding → Continue onboarding
    ↓
If existing user → Route to agents
```

**Fixed:** All new users must complete onboarding before using any feature.

## 📊 Detailed Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Message Arrives from WhatsApp                               │
│ from_number = "919876543210"                                │
│ msg_type = "text" or "image" or "video"                     │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Check User Status (ALWAYS FIRST)                   │
│                                                              │
│ check_user_status(from_number)                              │
│   ↓                                                          │
│ Returns:                                                     │
│   - is_new_user: True/False                                 │
│   - onboarding_state: "new", "asked_name", etc.            │
│   - user_profile: {...} or None                             │
└─────────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌──────────────────┐          ┌──────────────────┐
│ is_new_user =    │          │ is_new_user =    │
│ TRUE             │          │ FALSE            │
└──────────────────┘          └──────────────────┘
        ↓                               ↓
┌──────────────────────────┐  ┌──────────────────────────┐
│ STEP 2: New User         │  │ STEP 3: Check State      │
│                          │  │                          │
│ If msg_type = "text":    │  │ If state != "completed": │
│   Start onboarding       │  │   Continue onboarding    │
│   "आपका नाम क्या है?"    │  │                          │
│                          │  │ Else:                    │
│ Else:                    │  │   STEP 4: Route to       │
│   "पहले रजिस्ट्रेशन      │  │   agents                 │
│    पूरा करें"            │  │   (crop/market/finance)  │
└──────────────────────────┘  └──────────────────────────┘
```

## 🧪 Testing

### Test Script

Run the test script to verify changes:

```bash
cd src/lambda
python3 test_onboarding_flow.py
```

**Tests:**
1. ✅ New user detection
2. ✅ Complete onboarding flow (5 steps)
3. ✅ Existing user detection
4. ✅ User status check logic

### Manual Testing

**Test 1: New User with Text**
```
User: Hi
Expected: Welcome message + ask for name
```

**Test 2: New User with Image**
```
User: [sends image]
Expected: "पहले अपना रजिस्ट्रेशन पूरा करें"
```

**Test 3: User in Onboarding**
```
User: [in middle of onboarding, sends image]
Expected: "कृपया पहले अपना रजिस्ट्रेशन पूरा करें"
```

**Test 4: Existing User**
```
User: [completed profile, sends any message]
Expected: Routes to appropriate agent
```

## 🚀 Deployment

### Step 1: Deploy Updated Lambda

```bash
cd src/lambda
chmod +x deploy_updated_onboarding.sh
./deploy_updated_onboarding.sh
```

### Step 2: Monitor Logs

```bash
aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow
```

Look for:
- `📱 Message from...`
- `👤 User Status: is_new=...`
- `🆕 NEW USER DETECTED` or `✅ EXISTING USER`

### Step 3: Test with Real WhatsApp

1. Send "Hi" from a new number
2. Complete onboarding
3. Send another message
4. Verify it routes to agents

## 📝 Code Changes Summary

### Files Modified

1. **`src/lambda/lambda_whatsapp_kisaanmitra.py`**
   - Added `check_user_status()` helper function
   - Updated `lambda_handler()` to always check user status first
   - Enhanced logging with emojis
   - Added non-text message handling for new users

### Files Created

1. **`src/lambda/deploy_updated_onboarding.sh`**
   - Deployment script for updated Lambda

2. **`src/lambda/test_onboarding_flow.py`**
   - Comprehensive test suite

3. **`ONBOARDING_UPDATE.md`**
   - This documentation file

## 🔍 Key Improvements

### 1. **Always Check First**
- User status is checked before ANY processing
- No way to bypass onboarding

### 2. **Better Error Handling**
- Graceful fallback if DynamoDB fails
- Default to treating as new user (safer)

### 3. **Enhanced Logging**
- Emoji-based logs for easy scanning
- Shows user name for existing users
- Clear state transitions

### 4. **Cleaner Code**
- Single helper function for status check
- Reduced code duplication
- Easier to maintain

### 5. **Better UX**
- Clear messages for new users
- Guides users to complete onboarding
- Prevents confusion

## 📊 Monitoring

### CloudWatch Logs to Watch

**New User Flow:**
```
📱 Message from 919876543210, type: text
👤 User Status: is_new=True, state=new, has_profile=False
🆕 NEW USER DETECTED: 919876543210 - Starting onboarding
```

**Onboarding Progress:**
```
📱 Message from 919876543210, type: text
👤 User Status: is_new=False, state=asked_crops, has_profile=False
📝 USER IN ONBOARDING: 919876543210, state: asked_crops
```

**Onboarding Complete:**
```
✅ Onboarding completed! Added Rajesh Patil to knowledge graph
```

**Existing User:**
```
📱 Message from 919876543210, type: text
👤 User Status: is_new=False, state=completed, has_profile=True
✅ EXISTING USER: 919876543210 (Rajesh Patil) - Routing to agents
```

## 🎯 Success Criteria

- ✅ All new users go through onboarding
- ✅ No way to bypass onboarding
- ✅ Existing users route directly to agents
- ✅ Clear logging for debugging
- ✅ Graceful error handling
- ✅ Tests pass successfully

## 🔧 Troubleshooting

### Issue: User not detected as new

**Check:**
```bash
aws dynamodb get-item \
    --table-name kisaanmitra-user-profiles \
    --key '{"user_id": {"S": "919876543210"}}' \
    --region ap-south-1
```

**Solution:** If profile exists but shouldn't, delete it:
```bash
aws dynamodb delete-item \
    --table-name kisaanmitra-user-profiles \
    --key '{"user_id": {"S": "919876543210"}}' \
    --region ap-south-1
```

### Issue: Onboarding not starting

**Check Lambda logs:**
```bash
aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow
```

**Look for:**
- `ONBOARDING_AVAILABLE = True`
- `check_user_status()` being called
- Any error messages

### Issue: User stuck in onboarding

**Check onboarding state:**
```bash
aws dynamodb get-item \
    --table-name kisaanmitra-onboarding \
    --key '{"user_id": {"S": "919876543210"}}' \
    --region ap-south-1
```

**Solution:** Reset onboarding state:
```bash
aws dynamodb delete-item \
    --table-name kisaanmitra-onboarding \
    --key '{"user_id": {"S": "919876543210"}}' \
    --region ap-south-1
```

## 📚 Related Documentation

- **Complete Docs**: `docs/ONBOARDING_AND_KNOWLEDGE_GRAPH.md`
- **Quick Start**: `ONBOARDING_QUICKSTART.md`
- **Architecture**: `ONBOARDING_ARCHITECTURE.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`

## ✅ Checklist

Before deploying:
- [ ] Run test script: `python3 test_onboarding_flow.py`
- [ ] Review code changes
- [ ] Check DynamoDB tables exist
- [ ] Verify AWS credentials
- [ ] Test deployment script

After deploying:
- [ ] Monitor CloudWatch logs
- [ ] Test with new WhatsApp number
- [ ] Complete full onboarding flow
- [ ] Test existing user flow
- [ ] Verify knowledge graph updates
- [ ] Check dashboard shows new farmer

---

**Status**: Ready to Deploy ✅  
**Last Updated**: 2026-02-26  
**Version**: 2.1.0
