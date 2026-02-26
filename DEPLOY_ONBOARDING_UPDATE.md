# Deploy Onboarding Update - Quick Guide

## 🎯 What This Update Does

The Lambda function now **ALWAYS checks if a user is new** before processing any message. This ensures:
- ✅ All new users complete onboarding
- ✅ No way to bypass onboarding
- ✅ Better logging and error handling
- ✅ Cleaner, more maintainable code

## 🚀 Deploy in 3 Steps

### Step 1: Deploy to AWS Lambda

```bash
cd src/lambda
chmod +x deploy_updated_onboarding.sh
./deploy_updated_onboarding.sh
```

**What it does:**
- Packages Lambda with updated code
- Includes onboarding and knowledge graph modules
- Uploads to AWS
- Updates configuration

**Expected output:**
```
✅ Deployment complete!

📋 Summary:
  Function: kisaanmitra-whatsapp
  Region: ap-south-1
  Package: 15M

🔍 Key Changes:
  ✅ ALWAYS checks if user is new (first priority)
  ✅ Blocks non-text messages during onboarding
  ✅ Enhanced logging with emojis
  ✅ Helper function: check_user_status()
```

### Step 2: Monitor Logs

```bash
aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow
```

**Look for:**
- `📱 Message from...` - Message received
- `👤 User Status: is_new=...` - User status check
- `🆕 NEW USER DETECTED` - New user found
- `✅ EXISTING USER` - Existing user found

### Step 3: Test with WhatsApp

**Test 1: New User**
```
Send: Hi
Expected: Welcome message + "आपका नाम क्या है?"
```

**Test 2: Complete Onboarding**
```
Follow the prompts:
1. Name: "मेरा नाम राजेश है"
2. Crops: "गेहूं और धान"
3. Land: "5 एकड़"
4. Village: "पुणे"

Expected: "✅ रजिस्ट्रेशन पूरा हुआ!"
```

**Test 3: Existing User**
```
Send: "गेहूं का भाव?"
Expected: Routes to market agent
```

## 🧪 Optional: Run Tests First

Before deploying, you can run tests locally:

```bash
cd src/lambda
python3 test_onboarding_flow.py
```

**Expected output:**
```
✅ ALL TESTS PASSED!

Onboarding system is working correctly.
Ready to deploy to AWS Lambda.
```

## 📊 Verify Deployment

### Check Lambda Configuration

```bash
aws lambda get-function-configuration \
    --function-name kisaanmitra-whatsapp \
    --region ap-south-1 \
    --query '{Timeout:Timeout,Memory:MemorySize,Runtime:Runtime}'
```

**Expected:**
```json
{
    "Timeout": 60,
    "Memory": 1024,
    "Runtime": "python3.11"
}
```

### Check DynamoDB Tables

```bash
aws dynamodb list-tables --region ap-south-1
```

**Expected tables:**
- `kisaanmitra-onboarding`
- `kisaanmitra-user-profiles`
- `kisaanmitra-conversations`
- `kisaanmitra-market-data`
- `kisaanmitra-finance`

### View Dashboard

```bash
cd dashboard
./run_dashboard.sh
```

Open: http://localhost:8501

## 🔍 What Changed in Code

### New Helper Function

```python
def check_user_status(user_id):
    """Check user onboarding status"""
    is_new = onboarding_manager.is_new_user(user_id)
    state, data = onboarding_manager.get_onboarding_state(user_id)
    profile = None if is_new else onboarding_manager.get_user_profile(user_id)
    return is_new, state, profile
```

### Updated Flow

```python
# ALWAYS check user status first
is_new_user, onboarding_state, user_profile = check_user_status(from_number)

if is_new_user:
    # Start onboarding
elif onboarding_state != "completed":
    # Continue onboarding
else:
    # Route to agents
```

## 📝 Monitoring Checklist

After deployment, verify:

- [ ] New users receive welcome message
- [ ] Onboarding completes successfully
- [ ] Profile saved to DynamoDB
- [ ] Knowledge graph updated
- [ ] Existing users route to agents
- [ ] Logs show correct flow
- [ ] Dashboard shows new farmers

## 🔧 Troubleshooting

### Issue: Deployment fails

**Check:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check Lambda exists
aws lambda get-function --function-name kisaanmitra-whatsapp --region ap-south-1
```

### Issue: Onboarding not working

**Check logs:**
```bash
aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow
```

**Look for:**
- `ONBOARDING_AVAILABLE = True`
- Error messages
- User status checks

### Issue: User not detected as new

**Check profile:**
```bash
aws dynamodb get-item \
    --table-name kisaanmitra-user-profiles \
    --key '{"user_id": {"S": "919876543210"}}' \
    --region ap-south-1
```

## 📚 Documentation

- **Update Details**: `ONBOARDING_UPDATE.md`
- **Complete Docs**: `docs/ONBOARDING_AND_KNOWLEDGE_GRAPH.md`
- **Quick Start**: `ONBOARDING_QUICKSTART.md`
- **Architecture**: `ONBOARDING_ARCHITECTURE.md`

## ✅ Success Criteria

Deployment is successful when:

1. ✅ Lambda deploys without errors
2. ✅ New users complete onboarding
3. ✅ Profiles saved to DynamoDB
4. ✅ Knowledge graph updates
5. ✅ Existing users route correctly
6. ✅ Logs show clear flow
7. ✅ Dashboard displays data

## 🎉 You're Done!

The updated onboarding system is now live. All new users will be automatically detected and guided through registration before they can use any features.

**Next Steps:**
1. Monitor logs for the first few users
2. Check dashboard for new farmers
3. Verify knowledge graph updates
4. Collect feedback

---

**Questions?** Check `ONBOARDING_UPDATE.md` for detailed information.
