# Quick Deployment Reference

## 🚀 Deploy in 3 Steps

### Step 1: Setup Infrastructure
```bash
./infrastructure/setup_navigation_table.sh
./infrastructure/update_iam_permissions.sh
```

### Step 2: Deploy Lambda
```bash
cd src/lambda
./deploy_whatsapp.sh
```

### Step 3: Test
Send "hi" in WhatsApp, then test:
- Type `back` ✅
- Type `home` ✅
- Type `cancel` ✅
- Click navigation buttons ✅

---

## 📝 What Changed

### Removed:
- ❌ Hardcoded yields (Wheat: 20-25 quintal, etc.)
- ❌ Hardcoded prices (₹2,200-2,600/quintal, etc.)

### Added:
- ✅ AI research instructions
- ✅ Navigation system (back/home/cancel)
- ✅ Navigation buttons on all responses
- ✅ Fallback warnings for static data

---

## 🧪 Quick Test

```
You: hi
Bot: [Main Menu]

You: [Select Budget Planning]
Bot: [Budget prompt with navigation]

You: back
Bot: [Main Menu] ✅

You: home
Bot: [Main Menu] ✅

You: cancel
Bot: ❌ Cancelled. Starting fresh!
     [Main Menu] ✅
```

---

## 📊 Verification

```bash
# Check no hardcoded examples
grep "EXAMPLES OF REALISTIC" src/lambda/lambda_whatsapp_kisaanmitra.py
# Should return: (nothing)

# Check navigation integrated
grep -c "add_navigation_text" src/lambda/lambda_whatsapp_kisaanmitra.py
# Should return: 9

# Check table created
aws dynamodb describe-table \
  --table-name kisaanmitra-navigation-state \
  --region ap-south-1 \
  --query 'Table.TableStatus'
# Should return: "ACTIVE"
```

---

## 🆘 Rollback

If issues occur:
```bash
aws lambda update-alias \
  --function-name kisaanmitra-whatsapp \
  --name PROD \
  --function-version <PREVIOUS_VERSION> \
  --region ap-south-1
```

---

## 📚 Full Documentation

- `DEPLOYMENT_GUIDE_PHASE2.md` - Complete deployment guide
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Full summary
- `PHASE1_COMPLETE.md` - Phase 1 details
- `PHASE2_COMPLETE.md` - Phase 2 details

---

**Time:** 20-30 minutes  
**Risk:** LOW  
**Impact:** HIGH
