#!/bin/bash

echo "🧪 Testing Microservice Architecture v2.0"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test Lambda invocation
test_lambda() {
    local test_name=$1
    local payload=$2
    
    echo -n "Testing: $test_name... "
    
    # Invoke Lambda
    response=$(aws lambda invoke \
        --function-name whatsapp-llama-bot \
        --payload "$payload" \
        --region ap-south-1 \
        --cli-binary-format raw-in-base64-out \
        /tmp/lambda_response.json 2>&1)
    
    # Check if invocation was successful
    if echo "$response" | grep -q "StatusCode.*200"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $response"
        ((FAILED++))
        return 1
    fi
}

# Test 1: Webhook Verification
echo "1️⃣  Testing Webhook Verification"
test_lambda "Webhook Verification" '{
    "queryStringParameters": {
        "hub.verify_token": "mySecret_123",
        "hub.challenge": "test_challenge"
    }
}'
echo ""

# Test 2: Text Message (Greeting)
echo "2️⃣  Testing Text Message - Greeting"
test_lambda "Greeting Message" '{
    "body": "{\"entry\":[{\"changes\":[{\"value\":{\"messages\":[{\"from\":\"919000000002\",\"type\":\"text\",\"text\":{\"body\":\"hi\"}}]}}]}}]}"
}'
echo ""

# Test 3: Check Lambda Logs
echo "3️⃣  Checking Lambda Logs for Errors"
echo -n "Fetching recent logs... "

logs=$(aws logs tail /aws/lambda/whatsapp-llama-bot \
    --since 2m \
    --region ap-south-1\
    --format short 2>&1)

if echo "$logs" | grep -qi "error\|exception\|failed"; then
    echo -e "${RED}✗ ERRORS FOUND${NC}"
    echo "$logs" | grep -i "error\|exception\|failed" | head -10
    ((FAILED++))
else
    echo -e "${GREEN}✓ NO ERRORS${NC}"
    ((PASSED++))
fi
echo ""

# Test 4: Check Handler Configuration
echo "4️⃣  Verifying Handler Configuration"
echo -n "Checking handler... "

handler=$(aws lambda get-function-configuration \
    --function-name whatsapp-llama-bot \
    --region ap-south-1 \
    --query 'Handler' \
    --output text)

if [ "$handler" = "lambda_handler_v2.lambda_handler" ]; then
    echo -e "${GREEN}✓ CORRECT (v2)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ WRONG ($handler)${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: Check Code Size
echo "5️⃣  Checking Code Size"
echo -n "Verifying package size... "

code_size=$(aws lambda get-function-configuration \
    --function-name whatsapp-llama-bot \
    --region ap-south-1 \
    --query 'CodeSize' \
    --output text)

# Convert to KB
code_size_kb=$((code_size / 1024))

if [ $code_size_kb -lt 600 ]; then
    echo -e "${GREEN}✓ OPTIMAL (${code_size_kb} KB)${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ LARGE (${code_size_kb} KB)${NC}"
    ((PASSED++))
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "🎉 Microservice architecture is working correctly!"
    echo ""
    echo "Next steps:"
    echo "  1. Test with real WhatsApp messages"
    echo "  2. Monitor logs: aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1"
    echo "  3. Check performance metrics in CloudWatch"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check Lambda logs: aws logs tail /aws/lambda/whatsapp-llama-bot --follow --region ap-south-1"
    echo "  2. Verify all dependencies are included in deployment package"
    echo "  3. Check IAM permissions"
    exit 1
fi
