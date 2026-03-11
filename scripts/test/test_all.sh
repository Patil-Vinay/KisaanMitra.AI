#!/bin/bash

# Complete Test Suite for All 3 Agents

set -e

echo "KisaanMitra.AI - Complete Test Suite"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL_PASSED=0
TOTAL_FAILED=0

# Test 1: Crop Agent
echo -e "${BLUE}1 CROP AGENT TESTING${NC}"
echo ""

if ./test_whatsapp_integration.sh; then
    echo -e "${GREEN}Crop Agent: ALL TESTS PASSED${NC}"
    TOTAL_PASSED=$((TOTAL_PASSED + 10))
else
    echo -e "${RED}Crop Agent: SOME TESTS FAILED${NC}"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

echo ""
echo ""

# Test 2: Market Agent
echo -e "${BLUE}2 MARKET AGENT TESTING${NC}"
echo ""

if ./test_market_agent.sh; then
    echo -e "${GREEN}Market Agent: ALL TESTS PASSED${NC}"
    TOTAL_PASSED=$((TOTAL_PASSED + 10))
else
    echo -e "${RED}Market Agent: SOME TESTS FAILED${NC}"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

echo ""
echo ""

# Test 3: Finance Agent
echo -e "${BLUE}3 FINANCE AGENT TESTING${NC}"
echo ""

if ./test_finance_agent.sh; then
    echo -e "${GREEN}Finance Agent: ALL TESTS PASSED${NC}"
    TOTAL_PASSED=$((TOTAL_PASSED + 12))
else
    echo -e "${RED}Finance Agent: SOME TESTS FAILED${NC}"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi

echo ""
echo ""

# Final Summary
echo -e "${BLUE}FINAL TEST SUMMARY${NC}"
echo ""
echo -e "${GREEN}Tests Passed: $TOTAL_PASSED/32${NC}"
echo -e "${RED}Tests Failed: $TOTAL_FAILED${NC}"
echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}ALL TESTS PASSED! SYSTEM READY! ${NC}"
    echo ""
    echo "Agent Status:"
    echo "   • Crop Agent: 10/10 tests passed"
    echo "   • Market Agent: 10/10 tests passed"
    echo "   • Finance Agent: 12/12 tests passed"
    echo ""
    echo "Next Steps:"
    echo "   1. Deploy to AWS Lambda"
    echo "   2. Configure WhatsApp webhook"
    echo "   3. Start testing with real users"
    echo ""
    exit 0
else
    echo -e "${YELLOW}SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the output above for details."
    echo ""
    exit 1
fi
