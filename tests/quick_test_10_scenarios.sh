#!/bin/bash
# Quick Test Script for 10 Scenarios
# Tests various crops and validates financial calculations

set -e

PHONE="919000000002"
FUNCTION_NAME="whatsapp-llama-bot"

echo "=========================================="
echo "  KisaanMitra 10-Scenario Test Suite"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL=10
PASSED=0
FAILED=0

# Function to send test message
send_test() {
    local test_num=$1
    local message=$2
    local crop=$3
    
    echo ""
    echo "----------------------------------------"
    echo "Test #$test_num: $crop"
    echo "----------------------------------------"
    echo "Message: $message"
    echo ""
    
    # Create webhook payload
    PAYLOAD=$(cat <<EOF
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "1460763002175471",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "15551411052",
          "phone_number_id": "1049535664900621"
        },
        "messages": [{
          "from": "$PHONE",
          "id": "test_${test_num}_$(date +%s)",
          "timestamp": "$(date +%s)",
          "text": {
            "body": "$message"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}
EOF
)
    
    # Invoke Lambda
    echo "⏳ Invoking Lambda..."
    aws lambda invoke \
        --function-name $FUNCTION_NAME \
        --payload "$PAYLOAD" \
        --cli-binary-format raw-in-base64-out \
        /tmp/test_response_${test_num}.json > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Lambda invoked successfully${NC}"
    else
        echo -e "${RED}❌ Lambda invocation failed${NC}"
        ((FAILED++))
        return 1
    fi
    
    # Wait for processing
    echo "⏳ Processing (15s)..."
    sleep 15
    
    # Check logs
    echo "📋 Checking logs..."
    LOGS=$(aws logs tail /aws/lambda/$FUNCTION_NAME --since 2m --format short 2>/dev/null | tail -100)
    
    # Validate response
    if echo "$LOGS" | grep -q "ANTHROPIC.*✅ Response received"; then
        echo -e "${GREEN}✅ Anthropic API responded${NC}"
    else
        echo -e "${YELLOW}⚠️  No Anthropic response found${NC}"
    fi
    
    if echo "$LOGS" | grep -q "VALIDATION"; then
        echo -e "${GREEN}✅ Validation pipeline executed${NC}"
    else
        echo -e "${YELLOW}⚠️  Validation not found${NC}"
    fi
    
    if echo "$LOGS" | grep -q "MATH_ENFORCEMENT"; then
        echo -e "${GREEN}✅ Math enforcement applied${NC}"
    else
        echo -e "${YELLOW}⚠️  Math enforcement not found${NC}"
    fi
    
    if echo "$LOGS" | grep -q "\[FINAL\].*Total Cost"; then
        echo -e "${GREEN}✅ Final budget generated${NC}"
        
        # Extract and display final numbers
        COST=$(echo "$LOGS" | grep "\[FINAL\] Total Cost:" | tail -1 | sed 's/.*₹/₹/')
        REVENUE=$(echo "$LOGS" | grep "\[FINAL\] Total Revenue:" | tail -1 | sed 's/.*₹/₹/')
        PROFIT=$(echo "$LOGS" | grep "\[FINAL\] Total Profit:" | tail -1 | sed 's/.*₹/₹/')
        ROI=$(echo "$LOGS" | grep "\[FINAL\] ROI:" | tail -1 | sed 's/.*ROI: //')
        
        echo ""
        echo "💰 Final Numbers:"
        echo "   Cost:    $COST"
        echo "   Revenue: $REVENUE"
        echo "   Profit:  $PROFIT"
        echo "   ROI:     $ROI"
        
        ((PASSED++))
    else
        echo -e "${RED}❌ No final budget found${NC}"
        ((FAILED++))
    fi
    
    # Wait before next test
    if [ $test_num -lt $TOTAL ]; then
        echo ""
        echo "⏸️  Waiting 25s before next test..."
        sleep 25
    fi
}

# Run all 10 test scenarios
send_test 1 "I need sugarcane budget for 20 acres in Jalgaon" "Sugarcane"
send_test 2 "wheat cultivation cost for 5 acres in Ludhiana" "Wheat"
send_test 3 "cotton farming budget 10 acres Ahmedabad" "Cotton"
send_test 4 "paddy rice budget for 15 acres in Kolkata region" "Rice"
send_test 5 "tomato cultivation 3 acres Bangalore" "Tomato"
send_test 6 "onion farming cost 8 acres Nashik" "Onion"
send_test 7 "soybean budget 12 acres Indore" "Soybean"
send_test 8 "groundnut peanut cultivation 6 acres Guntur" "Groundnut"
send_test 9 "maize corn farming 7 acres Jaipur" "Maize"
send_test 10 "chilli pepper cultivation 4 acres Hyderabad" "Chilli"

# Summary
echo ""
echo "=========================================="
echo "  TEST SUMMARY"
echo "=========================================="
echo ""
echo "Total Tests:  $TOTAL"
echo -e "${GREEN}Passed:       $PASSED${NC}"
echo -e "${RED}Failed:       $FAILED${NC}"
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed or incomplete${NC}"
    exit 1
fi
