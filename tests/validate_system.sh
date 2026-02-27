#!/bin/bash
# Quick System Validation Script
# Validates that all components are working correctly

set -e

echo "=========================================="
echo "  KisaanMitra System Validation"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FUNCTION_NAME="whatsapp-llama-bot"

# Check 1: Lambda function exists
echo "1. Checking Lambda function..."
if aws lambda get-function --function-name $FUNCTION_NAME > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Lambda function exists${NC}"
else
    echo -e "${RED}❌ Lambda function not found${NC}"
    exit 1
fi

# Check 2: Environment variables
echo ""
echo "2. Checking environment variables..."
ENV_VARS=$(aws lambda get-function-configuration --function-name $FUNCTION_NAME --query 'Environment.Variables' --output json 2>/dev/null)

if echo "$ENV_VARS" | jq -e '.ANTHROPIC_API_KEY' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ANTHROPIC_API_KEY configured${NC}"
else
    echo -e "${RED}❌ ANTHROPIC_API_KEY missing${NC}"
    exit 1
fi

if echo "$ENV_VARS" | jq -e '.USE_ANTHROPIC_DIRECT' > /dev/null 2>&1; then
    USE_DIRECT=$(echo "$ENV_VARS" | jq -r '.USE_ANTHROPIC_DIRECT')
    if [ "$USE_DIRECT" = "true" ]; then
        echo -e "${GREEN}✅ USE_ANTHROPIC_DIRECT = true${NC}"
    else
        echo -e "${YELLOW}⚠️  USE_ANTHROPIC_DIRECT = false${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  USE_ANTHROPIC_DIRECT not set${NC}"
fi

# Check 3: Recent logs
echo ""
echo "3. Checking recent activity..."
LOGS=$(aws logs tail /aws/lambda/$FUNCTION_NAME --since 1h --format short 2>/dev/null)

if [ -z "$LOGS" ]; then
    echo -e "${YELLOW}⚠️  No recent activity (last 1 hour)${NC}"
else
    REQUEST_COUNT=$(echo "$LOGS" | grep -c "User message:" || echo "0")
    echo -e "${GREEN}✅ Recent activity found: $REQUEST_COUNT requests${NC}"
    
    # Check for Claude Sonnet 4.6
    if echo "$LOGS" | grep -q "claude-sonnet-4-6"; then
        echo -e "${GREEN}✅ Using Claude Sonnet 4.6${NC}"
    else
        echo -e "${YELLOW}⚠️  Claude Sonnet 4.6 not detected in recent logs${NC}"
    fi
    
    # Check for validation pipeline
    if echo "$LOGS" | grep -q "STEP 1: PRE-SCALING VALIDATION"; then
        echo -e "${GREEN}✅ Validation pipeline active${NC}"
    else
        echo -e "${YELLOW}⚠️  Validation pipeline not detected in recent logs${NC}"
    fi
    
    # Check for successful responses
    SUCCESS_COUNT=$(echo "$LOGS" | grep -c "✅ Response received" || echo "0")
    if [ $SUCCESS_COUNT -gt 0 ]; then
        echo -e "${GREEN}✅ Anthropic API responding: $SUCCESS_COUNT successful calls${NC}"
    else
        echo -e "${YELLOW}⚠️  No successful Anthropic API calls in recent logs${NC}"
    fi
fi

# Check 4: Code files exist
echo ""
echo "4. Checking code files..."
FILES=(
    "src/lambda/lambda_whatsapp_kisaanmitra.py"
    "src/lambda/anthropic_client.py"
    "src/lambda/crop_yield_database.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        exit 1
    fi
done

# Check 5: Validation functions exist
echo ""
echo "5. Checking validation functions..."
if grep -q "def validate_yield" src/lambda/crop_yield_database.py; then
    echo -e "${GREEN}✅ validate_yield function exists${NC}"
else
    echo -e "${RED}❌ validate_yield function missing${NC}"
    exit 1
fi

if grep -q "def enforce_mathematical_accuracy" src/lambda/crop_yield_database.py; then
    echo -e "${GREEN}✅ enforce_mathematical_accuracy function exists${NC}"
else
    echo -e "${RED}❌ enforce_mathematical_accuracy function missing${NC}"
    exit 1
fi

if grep -q "def sanity_check_budget" src/lambda/crop_yield_database.py; then
    echo -e "${GREEN}✅ sanity_check_budget function exists${NC}"
else
    echo -e "${RED}❌ sanity_check_budget function missing${NC}"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "  VALIDATION SUMMARY"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ All critical components validated${NC}"
echo ""
echo "System is ready for testing!"
echo ""
echo "To run comprehensive tests:"
echo "  python3 tests/test_3_scenarios.py"
echo ""
echo "To analyze recent logs:"
echo "  tests/analyze_recent_tests.sh"
echo ""
