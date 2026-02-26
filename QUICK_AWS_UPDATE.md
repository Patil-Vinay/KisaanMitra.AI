# ⚡ Quick AWS Update - 5 Minutes

## What Changed
✅ Lambda now has FULL Market & Finance agents (not just AI responses)

## 5 Steps to Update AWS

### 1️⃣ Add Environment Variable (30 seconds)
AWS Console → Lambda → whatsapp-llama-bot → Configuration → Environment variables → Add:
```
AGMARKNET_API_KEY = not_available
```
(data.gov.in is down - use this placeholder, market agent will use AI instead)

### 2️⃣ Increase Resources (30 seconds)
Configuration → General configuration → Edit:
```
Timeout: 60 seconds
Memory: 512 MB
```

### 3️⃣ Create Tables (1 minute)
```bash
bash infrastructure/setup_finance_tables.sh
```

### 4️⃣ Update Permissions (1 minute)
Configuration → Permissions → Execution role → Add inline policy:
```json
{
    "Effect": "Allow",
    "Action": ["dynamodb:GetItem", "dynamodb:PutItem"],
    "Resource": "arn:aws:dynamodb:ap-south-1:*:table/kisaanmitra-*"
}
```

### 5️⃣ Deploy Code (2 minutes)
```bash
cd src/lambda
bash deploy_whatsapp.sh
```

## Test It
WhatsApp messages to try:
- `गेहूं का भाव` → Market prices
- `बजट बताओ` → Budget breakdown
- `योजना` → Government schemes
- Send crop image → Disease detection

## Done! 🎉

Full details: `AWS_LAMBDA_UPDATES_NEEDED.md`
