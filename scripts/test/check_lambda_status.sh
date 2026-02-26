#!/bin/bash

# Check Lambda Status and Configuration

FUNCTION_NAME="whatsapp-llama-bot"
REGION="ap-south-1"

echo "🔍 Checking Lambda: $FUNCTION_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check if function exists
echo "1️⃣ Checking if Lambda function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    echo "✅ Lambda function exists"
else
    echo "❌ Lambda function not found"
    exit 1
fi
echo ""

# 2. Check configuration
echo "2️⃣ Checking Lambda configuration..."
CONFIG=$(aws lambda get-function-configuration --function-name $FUNCTION_NAME --region $REGION)

TIMEOUT=$(echo $CONFIG | jq -r '.Timeout')
MEMORY=$(echo $CONFIG | jq -r '.MemorySize')
RUNTIME=$(echo $CONFIG | jq -r '.Runtime')
LAST_MODIFIED=$(echo $CONFIG | jq -r '.LastModified')

echo "   Runtime: $RUNTIME"
echo "   Timeout: $TIMEOUT seconds $([ $TIMEOUT -ge 60 ] && echo '✅' || echo '⚠️  Should be 60+')"
echo "   Memory: $MEMORY MB $([ $MEMORY -ge 512 ] && echo '✅' || echo '⚠️  Should be 512+')"
echo "   Last Modified: $LAST_MODIFIED"
echo ""

# 3. Check environment variables
echo "3️⃣ Checking environment variables..."
ENV_VARS=$(echo $CONFIG | jq -r '.Environment.Variables')

check_env_var() {
    local var_name=$1
    local value=$(echo $ENV_VARS | jq -r ".$var_name // \"NOT_SET\"")
    if [ "$value" != "NOT_SET" ] && [ "$value" != "null" ]; then
        echo "   ✅ $var_name: ${value:0:20}..."
    else
        echo "   ❌ $var_name: NOT SET"
    fi
}

check_env_var "VERIFY_TOKEN"
check_env_var "WHATSAPP_TOKEN"
check_env_var "PHONE_NUMBER_ID"
check_env_var "CROP_HEALTH_API_KEY"
check_env_var "AGMARKNET_API_KEY"
echo ""

# 4. Check IAM role
echo "4️⃣ Checking IAM role..."
ROLE_ARN=$(echo $CONFIG | jq -r '.Role')
ROLE_NAME=$(echo $ROLE_ARN | cut -d'/' -f2)
echo "   Role: $ROLE_NAME"

# Check if role has DynamoDB permissions
POLICIES=$(aws iam list-attached-role-policies --role-name $ROLE_NAME --query 'AttachedPolicies[*].PolicyName' --output text 2>/dev/null)
if echo "$POLICIES" | grep -q "DynamoDB"; then
    echo "   ✅ Has DynamoDB policy"
else
    echo "   ⚠️  Check DynamoDB permissions"
fi
echo ""

# 5. Check DynamoDB tables
echo "5️⃣ Checking DynamoDB tables..."
check_table() {
    local table_name=$1
    if aws dynamodb describe-table --table-name $table_name --region $REGION &> /dev/null; then
        echo "   ✅ $table_name exists"
    else
        echo "   ❌ $table_name NOT FOUND"
    fi
}

check_table "kisaanmitra-conversations"
check_table "kisaanmitra-market-data"
check_table "kisaanmitra-finance"
echo ""

# 6. Check recent logs
echo "6️⃣ Checking recent CloudWatch logs..."
LOG_GROUP="/aws/lambda/$FUNCTION_NAME"

if aws logs describe-log-groups --log-group-name-prefix $LOG_GROUP --region $REGION &> /dev/null; then
    echo "   ✅ Log group exists"
    
    # Get latest log stream
    LATEST_STREAM=$(aws logs describe-log-streams \
        --log-group-name $LOG_GROUP \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --region $REGION \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null)
    
    if [ "$LATEST_STREAM" != "None" ] && [ -n "$LATEST_STREAM" ]; then
        echo "   Latest activity: $(aws logs describe-log-streams \
            --log-group-name $LOG_GROUP \
            --log-stream-name-prefix $LATEST_STREAM \
            --region $REGION \
            --query 'logStreams[0].lastEventTime' \
            --output text 2>/dev/null | xargs -I {} date -r {} 2>/dev/null || echo 'Unknown')"
        
        echo ""
        echo "   📋 Last 5 log entries:"
        aws logs tail $LOG_GROUP --since 1h --format short --region $REGION 2>/dev/null | tail -5 || echo "   No recent logs"
    else
        echo "   ⚠️  No log streams found (Lambda not invoked yet?)"
    fi
else
    echo "   ❌ Log group not found"
fi
echo ""

# 7. Test Lambda with a simple event
echo "7️⃣ Testing Lambda with webhook verification..."
TEST_EVENT='{
  "queryStringParameters": {
    "hub.mode": "subscribe",
    "hub.verify_token": "mySecret_123",
    "hub.challenge": "test_challenge_123"
  }
}'

echo "$TEST_EVENT" > /tmp/test_event.json

INVOKE_RESULT=$(aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload file:///tmp/test_event.json \
    --region $REGION \
    /tmp/response.json 2>&1)

if [ $? -eq 0 ]; then
    RESPONSE=$(cat /tmp/response.json)
    if [ "$RESPONSE" == "test_challenge_123" ]; then
        echo "   ✅ Lambda responding correctly"
    else
        echo "   ⚠️  Unexpected response: $RESPONSE"
    fi
else
    echo "   ❌ Lambda invocation failed"
    echo "   Error: $INVOKE_RESULT"
fi

rm -f /tmp/test_event.json /tmp/response.json
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ISSUES=0

if [ $TIMEOUT -lt 60 ]; then
    echo "⚠️  Increase timeout to 60 seconds"
    ISSUES=$((ISSUES + 1))
fi

if [ $MEMORY -lt 512 ]; then
    echo "⚠️  Increase memory to 512 MB"
    ISSUES=$((ISSUES + 1))
fi

AGMARKNET_KEY=$(echo $ENV_VARS | jq -r '.AGMARKNET_API_KEY // "NOT_SET"')
if [ "$AGMARKNET_KEY" == "NOT_SET" ]; then
    echo "⚠️  Add AGMARKNET_API_KEY environment variable"
    ISSUES=$((ISSUES + 1))
fi

if ! aws dynamodb describe-table --table-name kisaanmitra-market-data --region $REGION &> /dev/null; then
    echo "⚠️  Create kisaanmitra-market-data table"
    ISSUES=$((ISSUES + 1))
fi

if ! aws dynamodb describe-table --table-name kisaanmitra-finance --region $REGION &> /dev/null; then
    echo "⚠️  Create kisaanmitra-finance table"
    ISSUES=$((ISSUES + 1))
fi

echo ""
if [ $ISSUES -eq 0 ]; then
    echo "✅ All checks passed! Lambda is ready."
    echo ""
    echo "🧪 Test via WhatsApp:"
    echo "   • Send: 'गेहूं का भाव' (Market test)"
    echo "   • Send: 'बजट बताओ' (Finance test)"
    echo "   • Send crop image (Crop test)"
else
    echo "⚠️  Found $ISSUES issue(s) - see above for details"
    echo ""
    echo "📖 Fix issues using: QUICK_AWS_UPDATE.md"
fi
echo ""
