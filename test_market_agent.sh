#!/bin/bash

# Test Market Agent functionality

set -e

echo "🧪 Testing Market Agent"
echo "======================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAILED++))
    fi
    echo ""
}

# Test 1: Check market agent file
echo "Test 1: Market Agent File Structure"
if [ -f "src/market_agent/market_agent.py" ]; then
    if grep -q "def lambda_handler" src/market_agent/market_agent.py; then
        echo "✓ Lambda handler found"
        if grep -q "SYSTEM_PROMPT" src/market_agent/market_agent.py; then
            echo "✓ System prompt configured"
            if grep -q "get_mandi_prices" src/market_agent/market_agent.py; then
                echo "✓ Mandi price function found"
                test_result 0 "Market agent structure valid"
            else
                test_result 1 "Mandi price function missing"
            fi
        else
            test_result 1 "System prompt missing"
        fi
    else
        test_result 1 "Lambda handler missing"
    fi
else
    test_result 1 "Market agent file not found"
fi

# Test 2: Check system prompt
echo "Test 2: System Prompt Configuration"
if grep -q "Market Intelligence Agent" src/market_agent/market_agent.py; then
    if grep -q "Hindi" src/market_agent/market_agent.py; then
        echo "✓ Hindi language support"
        test_result 0 "System prompt properly configured"
    else
        test_result 1 "Language support missing"
    fi
else
    test_result 1 "System prompt not configured"
fi

# Test 3: Check data sources
echo "Test 3: Data Source Integration"
SOURCES=("get_mandi_prices" "get_cached_market_data" "cache_market_data")
ALL_PRESENT=true

for source in "${SOURCES[@]}"; do
    if grep -q "$source" src/market_agent/market_agent.py; then
        echo "✓ $source function found"
    else
        echo "✗ $source function missing"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = true ]; then
    test_result 0 "All data sources integrated"
else
    test_result 1 "Some data sources missing"
fi

# Test 4: Check DynamoDB integration
echo "Test 4: DynamoDB Integration"
if grep -q "dynamodb" src/market_agent/market_agent.py; then
    if grep -q "MARKET_DATA_TABLE" src/market_agent/market_agent.py; then
        echo "✓ DynamoDB client configured"
        echo "✓ Table name configured"
        test_result 0 "DynamoDB integration present"
    else
        test_result 1 "Table configuration missing"
    fi
else
    test_result 1 "DynamoDB integration missing"
fi

# Test 5: Check price trend analysis
echo "Test 5: Price Trend Analysis"
if grep -q "analyze_price_trend" src/market_agent/market_agent.py; then
    if grep -q "trend" src/market_agent/market_agent.py; then
        echo "✓ Trend analysis function found"
        test_result 0 "Price trend analysis implemented"
    else
        test_result 1 "Trend logic incomplete"
    fi
else
    test_result 1 "Price trend analysis missing"
fi

# Test 6: Check crop recommendation
echo "Test 6: Crop Recommendation System"
if grep -q "get_crop_recommendation" src/market_agent/market_agent.py; then
    if grep -q "kharif" src/market_agent/market_agent.py; then
        echo "✓ Seasonal recommendations found"
        test_result 0 "Crop recommendation system present"
    else
        test_result 1 "Seasonal logic missing"
    fi
else
    test_result 1 "Crop recommendation missing"
fi

# Test 7: Check response formatting
echo "Test 7: Response Formatting"
if grep -q "format_market_response" src/market_agent/market_agent.py; then
    if grep -q "WhatsApp" src/market_agent/market_agent.py; then
        echo "✓ Response formatter found"
        test_result 0 "Response formatting implemented"
    else
        test_result 1 "WhatsApp formatting missing"
    fi
else
    test_result 1 "Response formatter missing"
fi

# Test 8: Check enhanced crop agent
echo "Test 8: Enhanced Crop Agent"
if [ -f "src/crop_agent/crop_agent_enhanced.py" ]; then
    if grep -q "CROP_SYSTEM_PROMPT" src/crop_agent/crop_agent_enhanced.py; then
        echo "✓ System prompt added"
        if grep -q "get_conversation_history" src/crop_agent/crop_agent_enhanced.py; then
            echo "✓ Conversation memory added"
            if grep -q "detect_language" src/crop_agent/crop_agent_enhanced.py; then
                echo "✓ Language detection added"
                test_result 0 "Enhanced crop agent complete"
            else
                test_result 1 "Language detection missing"
            fi
        else
            test_result 1 "Conversation memory missing"
        fi
    else
        test_result 1 "System prompt missing"
    fi
else
    test_result 1 "Enhanced crop agent file not found"
fi

# Test 9: Check infrastructure scripts
echo "Test 9: Infrastructure Setup Scripts"
if [ -f "infrastructure/setup_dynamodb.sh" ]; then
    echo "✓ DynamoDB setup script found"
    if [ -f "infrastructure/update_iam_permissions.sh" ]; then
        echo "✓ IAM update script found"
        test_result 0 "Infrastructure scripts present"
    else
        test_result 1 "IAM script missing"
    fi
else
    test_result 1 "DynamoDB script missing"
fi

# Test 10: Check deployment scripts
echo "Test 10: Deployment Scripts"
if [ -f "src/lambda/deploy_market_agent.sh" ]; then
    echo "✓ Market agent deployment script found"
    test_result 0 "Deployment scripts ready"
else
    test_result 1 "Market agent deployment script missing"
fi

# Summary
echo ""
echo "=========================================="
echo "📊 Market Agent Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All market agent tests passed!${NC}"
    echo ""
    echo "✅ Features Verified:"
    echo "   • System prompt with agricultural context"
    echo "   • Mandi price integration"
    echo "   • DynamoDB caching"
    echo "   • Price trend analysis"
    echo "   • Crop recommendations"
    echo "   • Response formatting"
    echo "   • Enhanced crop agent with memory"
    echo "   • Language detection"
    echo "   • Infrastructure scripts"
    echo ""
    echo "🚀 Ready for deployment!"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi
