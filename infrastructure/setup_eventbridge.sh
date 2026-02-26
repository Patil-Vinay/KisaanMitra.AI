#!/bin/bash

# Setup EventBridge Rules for Automated Tasks

set -e

REGION="ap-south-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "📅 Setting up EventBridge Rules"
echo "==============================="
echo ""

# 1. Daily Market Price Update (6 AM IST)
echo "1️⃣ Creating daily market price update rule..."
aws events put-rule \
  --name kisaanmitra-daily-price-update \
  --description "Fetch fresh mandi prices daily at 6 AM IST" \
  --schedule-expression "cron(30 0 * * ? *)" \
  --state ENABLED \
  --region $REGION

# Add Lambda target
aws events put-targets \
  --rule kisaanmitra-daily-price-update \
  --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:kisaanmitra-market-agent","Input"="{\"type\":\"scheduled_update\",\"action\":\"fetch_prices\"}" \
  --region $REGION

# Add permission for EventBridge to invoke Lambda
aws lambda add-permission \
  --function-name kisaanmitra-market-agent \
  --statement-id AllowEventBridgeDailyPriceUpdate \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/kisaanmitra-daily-price-update" \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

echo "✓ Daily price update rule created (6 AM IST)"

# 2. Weekly Scheme Notifications (Monday 9 AM IST)
echo ""
echo "2️⃣ Creating weekly scheme notification rule..."
aws events put-rule \
  --name kisaanmitra-weekly-schemes \
  --description "Send government scheme updates every Monday at 9 AM IST" \
  --schedule-expression "cron(30 3 ? * MON *)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule kisaanmitra-weekly-schemes \
  --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:kisaanmitra-finance-agent","Input"="{\"type\":\"scheduled_update\",\"action\":\"send_scheme_updates\"}" \
  --region $REGION

aws lambda add-permission \
  --function-name kisaanmitra-finance-agent \
  --statement-id AllowEventBridgeWeeklySchemes \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/kisaanmitra-weekly-schemes" \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

echo "✓ Weekly scheme notification rule created (Monday 9 AM IST)"

# 3. Monthly Financial Planning Reminder (1st of month, 10 AM IST)
echo ""
echo "3️⃣ Creating monthly financial reminder rule..."
aws events put-rule \
  --name kisaanmitra-monthly-finance-reminder \
  --description "Send financial planning reminders on 1st of every month" \
  --schedule-expression "cron(30 4 1 * ? *)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule kisaanmitra-monthly-finance-reminder \
  --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:kisaanmitra-finance-agent","Input"="{\"type\":\"scheduled_update\",\"action\":\"send_finance_reminders\"}" \
  --region $REGION

aws lambda add-permission \
  --function-name kisaanmitra-finance-agent \
  --statement-id AllowEventBridgeMonthlyFinance \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/kisaanmitra-monthly-finance-reminder" \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

echo "✓ Monthly finance reminder rule created (1st of month, 10 AM IST)"

# 4. Seasonal Crop Planting Alerts
echo ""
echo "4️⃣ Creating seasonal crop planting alerts..."

# Kharif season (June 1st)
aws events put-rule \
  --name kisaanmitra-kharif-season-alert \
  --description "Kharif season planting reminder" \
  --schedule-expression "cron(0 4 1 6 ? *)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule kisaanmitra-kharif-season-alert \
  --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:kisaanmitra-market-agent","Input"="{\"type\":\"seasonal_alert\",\"season\":\"kharif\"}" \
  --region $REGION

aws lambda add-permission \
  --function-name kisaanmitra-market-agent \
  --statement-id AllowEventBridgeKharifAlert \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/kisaanmitra-kharif-season-alert" \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

# Rabi season (October 1st)
aws events put-rule \
  --name kisaanmitra-rabi-season-alert \
  --description "Rabi season planting reminder" \
  --schedule-expression "cron(0 4 1 10 ? *)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule kisaanmitra-rabi-season-alert \
  --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:kisaanmitra-market-agent","Input"="{\"type\":\"seasonal_alert\",\"season\":\"rabi\"}" \
  --region $REGION

aws lambda add-permission \
  --function-name kisaanmitra-market-agent \
  --statement-id AllowEventBridgeRabiAlert \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/kisaanmitra-rabi-season-alert" \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

echo "✓ Seasonal alerts created (Kharif: June 1, Rabi: October 1)"

# 5. Cache Cleanup (Daily midnight)
echo ""
echo "5️⃣ Creating cache cleanup rule..."
aws events put-rule \
  --name kisaanmitra-cache-cleanup \
  --description "Clean up expired cache entries daily" \
  --schedule-expression "cron(0 18 * * ? *)" \
  --state ENABLED \
  --region $REGION

aws events put-targets \
  --rule kisaanmitra-cache-cleanup \
  --targets "Id"="1","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:kisaanmitra-market-agent","Input"="{\"type\":\"maintenance\",\"action\":\"cleanup_cache\"}" \
  --region $REGION

aws lambda add-permission \
  --function-name kisaanmitra-market-agent \
  --statement-id AllowEventBridgeCacheCleanup \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/kisaanmitra-cache-cleanup" \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

echo "✓ Cache cleanup rule created (daily midnight IST)"

echo ""
echo "✅ EventBridge Setup Complete!"
echo ""
echo "📅 Scheduled Rules Created:"
echo "   1. Daily Price Update: 6:00 AM IST"
echo "   2. Weekly Schemes: Monday 9:00 AM IST"
echo "   3. Monthly Finance: 1st of month, 10:00 AM IST"
echo "   4. Kharif Season Alert: June 1st"
echo "   5. Rabi Season Alert: October 1st"
echo "   6. Cache Cleanup: Daily midnight IST"
echo ""
echo "🔍 View rules:"
echo "   aws events list-rules --region $REGION"
echo ""
echo "📊 Monitor invocations:"
echo "   aws cloudwatch get-metric-statistics \\"
echo "     --namespace AWS/Events \\"
echo "     --metric-name Invocations \\"
echo "     --dimensions Name=RuleName,Value=kisaanmitra-daily-price-update \\"
echo "     --start-time 2026-02-26T00:00:00Z \\"
echo "     --end-time 2026-02-27T00:00:00Z \\"
echo "     --period 3600 \\"
echo "     --statistics Sum"
