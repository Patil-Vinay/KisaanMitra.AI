# Deployment Guide - Phase 2: Navigation System

## Overview

This guide walks you through deploying the complete UX & Architecture Redesign with navigation system.

---

## Pre-Deployment Checklist

### ✅ Phase 1 Complete:
- [x] Removed hardcoded yields/prices from AI prompts
- [x] Marked crop calendar as fallback
- [x] Marked mock weather as fallback
- [x] Created NavigationController
- [x] Created navigation table setup script

### ✅ Phase 2 Complete:
- [x] Updated interactive menus with navigation
- [x] Integrated NavigationController into Lambda
- [x] Added navigation to all agent responses
- [x] Updated IAM permissions script

---

## Deployment Steps

### Step 1: Create Navigation State Table

```bash
cd infrastructure
./setup_navigation_table.sh
```

**Expected Output:**
```
🔧 Setting up Navigation State Table...
✅ Navigation state table created successfully!
⏳ Waiting for table to be active...
✅ Navigation state table is ready!
```

**Verify:**
```bash
aws dynamodb describe-table \
  --table-name kisaanmitra-navigation-state \
  --region ap-south-1 \
  --query 'Table.TableStatus'
```

Should return: `"ACTIVE"`

---

### Step 2: Update IAM Permissions

```bash
cd infrastructure
./update_iam_permissions.sh
```

**Expected Output:**
```
🔐 Updating IAM permissions for Lambda...
1️⃣ Creating/updating policy...
✅ IAM permissions updated!
```

**Verify:**
```bash
aws iam get-role-policy \
  --role-name kisaanmitra-lambda-role \
  --policy-name kisaanmitra-lambda-policy \
  --query 'PolicyDocument.Statement[4].Resource' \
  --output json
```

Should include: `kisaanmitra-navigation-state`

---

### Step 3: Deploy Lambda Function

```bash
cd src/lambda
./deploy_whatsapp.sh
```

**Expected Output:**
```
📦 Packaging Lambda function...
🚀 Deploying to AWS Lambda...
✅ Deployment successful!
```

**Verify:**
```bash
aws lambda get-function \
  --function-name kisaanmitra-whatsapp \
  --region ap-south-1 \
  --query 'Configuration.LastModified'
```

Should show recent timestamp.

---

### Step 4: Test Navigation System

#### Test 1: Text Commands

**In WhatsApp:**
1. Send: `hi`
2. Select a service (e.g., Budget Planning)
3. Send: `back`
   - ✅ Should return to main menu
4. Send: `home`
   - ✅ Should show main menu
5. Send: `cancel`
   - ✅ Should show "Cancelled" message and main menu

#### Test 2: Hindi Commands

**In WhatsApp:**
1. Send: `hi`
2. Select a service
3. Send: `पीछे`
   - ✅ Should return to main menu
4. Send: `मुख्य मेनू`
   - ✅ Should show main menu
5. Send: `रद्द करें`
   - ✅ Should show "रद्द कर दिया" message

#### Test 3: Button Navigation

**In WhatsApp:**
1. Send: `hi`
2. Select Budget Planning
3. Provide budget details
4. Click [⬅ Back] button
   - ✅ Should return to main menu
5. Click [🏠 Home] button
   - ✅ Should show main menu
6. Click [❌ Cancel] button
   - ✅ Should clear state and show main menu

#### Test 4: Navigation Text

**In WhatsApp:**
1. Ask any question to any agent
2. Check response includes:
   - ✅ "💡 Type 'back' to go back..." (English)
   - ✅ "💡 'back' टाइप करें..." (Hindi)

#### Test 5: Agent Responses

**Test each agent:**
- Crop Agent: Ask about crop disease
  - ✅ Response includes navigation text
- Market Agent: Ask about crop price
  - ✅ Response includes navigation text
- Finance Agent: Ask for budget
  - ✅ Response includes navigation text
- General Agent: Ask general question
  - ✅ Response includes navigation text

---

### Step 5: Verify No Static Data

**Check CloudWatch Logs:**

```bash
aws logs tail /aws/lambda/kisaanmitra-whatsapp \
  --region ap-south-1 \
  --follow
```

**Look for:**
- ✅ `[WARNING] ⚠️ Using STATIC crop calendar` - If reminders are used
- ✅ `[WARNING] ⚠️⚠️⚠️ Using MOCK weather data` - If weather is used
- ✅ `CRITICAL DATA RESEARCH INSTRUCTIONS` - In AI prompts
- ❌ Should NOT see hardcoded yields/prices in logs

---

## Rollback Plan

If issues occur, rollback to previous version:

```bash
# Get previous version
aws lambda list-versions-by-function \
  --function-name kisaanmitra-whatsapp \
  --region ap-south-1 \
  --query 'Versions[-2].Version'

# Rollback
aws lambda update-alias \
  --function-name kisaanmitra-whatsapp \
  --name PROD \
  --function-version <PREVIOUS_VERSION> \
  --region ap-south-1
```

---

## Monitoring

### Key Metrics to Watch:

1. **Lambda Errors:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=kisaanmitra-whatsapp \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region ap-south-1
```

2. **DynamoDB Throttles:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=kisaanmitra-navigation-state \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region ap-south-1
```

3. **Navigation Usage:**
```bash
# Check navigation table item count
aws dynamodb describe-table \
  --table-name kisaanmitra-navigation-state \
  --region ap-south-1 \
  --query 'Table.ItemCount'
```

---

## Troubleshooting

### Issue: Navigation commands not working

**Check:**
1. NavigationController imported successfully
   ```bash
   aws logs filter-pattern "Navigation Controller loaded" \
     --log-group-name /aws/lambda/kisaanmitra-whatsapp \
     --region ap-south-1
   ```

2. Navigation table exists
   ```bash
   aws dynamodb describe-table \
     --table-name kisaanmitra-navigation-state \
     --region ap-south-1
   ```

3. IAM permissions correct
   ```bash
   aws iam get-role-policy \
     --role-name kisaanmitra-lambda-role \
     --policy-name kisaanmitra-lambda-policy
   ```

### Issue: Navigation text not showing

**Check:**
1. INTERACTIVE_MESSAGES_AVAILABLE flag
   ```bash
   aws logs filter-pattern "WhatsApp Interactive Messages loaded" \
     --log-group-name /aws/lambda/kisaanmitra-whatsapp \
     --region ap-south-1
   ```

2. add_navigation_text function imported
   ```bash
   grep -n "add_navigation_text" src/lambda/lambda_whatsapp_kisaanmitra.py
   ```

### Issue: Static data still being used

**Check:**
1. AI prompts don't contain examples
   ```bash
   grep -n "EXAMPLES OF REALISTIC" src/lambda/lambda_whatsapp_kisaanmitra.py
   # Should return: (no results)
   ```

2. Fallback warnings present
   ```bash
   grep -n "WARNING.*STATIC" src/lambda/reminder_manager.py
   grep -n "WARNING.*MOCK" src/lambda/weather_service.py
   ```

---

## Post-Deployment Validation

### ✅ Validation Checklist:

- [ ] Navigation table created and active
- [ ] IAM permissions updated
- [ ] Lambda deployed successfully
- [ ] Text commands work (back, home, cancel)
- [ ] Hindi commands work (पीछे, मुख्य मेनू, रद्द करें)
- [ ] Navigation buttons work
- [ ] All agents include navigation text
- [ ] No hardcoded yields/prices in logs
- [ ] Fallback warnings appear when appropriate
- [ ] No errors in CloudWatch logs
- [ ] User experience smooth and intuitive

---

## Success Criteria

**Deployment is successful when:**

1. ✅ All navigation commands work in both languages
2. ✅ All navigation buttons work correctly
3. ✅ All agent responses include navigation text
4. ✅ No hardcoded agricultural data in AI prompts
5. ✅ Fallback warnings appear in logs when needed
6. ✅ No Lambda errors in CloudWatch
7. ✅ No DynamoDB throttling
8. ✅ User can navigate smoothly through conversation
9. ✅ State persists correctly across messages
10. ✅ Cancel clears state properly

---

## Estimated Timeline

- **Step 1 (Table):** 2-3 minutes
- **Step 2 (IAM):** 1-2 minutes
- **Step 3 (Deploy):** 3-5 minutes
- **Step 4 (Testing):** 10-15 minutes
- **Step 5 (Verification):** 5 minutes

**Total:** 20-30 minutes

---

## Support

If you encounter issues:

1. Check CloudWatch logs for errors
2. Verify all resources created successfully
3. Test each component individually
4. Use rollback plan if needed
5. Review troubleshooting section

---

**Ready to deploy!** Follow the steps above to deploy the complete navigation system.
