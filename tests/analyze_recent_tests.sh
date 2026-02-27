#!/bin/bash
# Analyze recent Lambda logs to identify issues and patterns

echo "=========================================="
echo "  Analyzing Recent Lambda Logs"
echo "=========================================="
echo ""

FUNCTION_NAME="whatsapp-llama-bot"

# Get logs from last 3 hours
echo "📋 Fetching logs from last 3 hours..."
LOGS=$(aws logs tail /aws/lambda/$FUNCTION_NAME --since 3h --format short 2>/dev/null)

echo ""
echo "🔍 Analysis Results:"
echo "===================="

# Count requests
TOTAL_REQUESTS=$(echo "$LOGS" | grep -c "User message:" || echo "0")
echo ""
echo "📊 Request Statistics:"
echo "   Total requests: $TOTAL_REQUESTS"

# Count successful Anthropic calls
ANTHROPIC_SUCCESS=$(echo "$LOGS" | grep -c "ANTHROPIC.*✅ Response received" || echo "0")
ANTHROPIC_ERRORS=$(echo "$LOGS" | grep -c "ANTHROPIC.*❌" || echo "0")
echo "   Anthropic success: $ANTHROPIC_SUCCESS"
echo "   Anthropic errors: $ANTHROPIC_ERRORS"

# Count validation steps
VALIDATION_RUNS=$(echo "$LOGS" | grep -c "STEP 1: PRE-SCALING VALIDATION" || echo "0")
MATH_ENFORCEMENT=$(echo "$LOGS" | grep -c "STEP 4: MATHEMATICAL ENFORCEMENT" || echo "0")
SANITY_CHECKS=$(echo "$LOGS" | grep -c "STEP 5: FINAL SANITY CHECK" || echo "0")
echo "   Validation runs: $VALIDATION_RUNS"
echo "   Math enforcement: $MATH_ENFORCEMENT"
echo "   Sanity checks: $SANITY_CHECKS"

# Check for issues
echo ""
echo "⚠️  Issues Detected:"
echo "===================="

# Unrealistic ROI
UNREALISTIC_ROI=$(echo "$LOGS" | grep -c "UNREALISTIC ROI DETECTED" || echo "0")
if [ $UNREALISTIC_ROI -gt 0 ]; then
    echo "   - Unrealistic ROI detected: $UNREALISTIC_ROI times"
fi

# Sanity check failures
SANITY_FAILURES=$(echo "$LOGS" | grep -c "SANITY CHECK FAILED" || echo "0")
if [ $SANITY_FAILURES -gt 0 ]; then
    echo "   - Sanity check failures: $SANITY_FAILURES times"
fi

# Revenue mismatches
REVENUE_MISMATCH=$(echo "$LOGS" | grep -c "Revenue mismatch" || echo "0")
if [ $REVENUE_MISMATCH -gt 0 ]; then
    echo "   - Revenue mismatches: $REVENUE_MISMATCH times"
fi

# Profit mismatches
PROFIT_MISMATCH=$(echo "$LOGS" | grep -c "Profit mismatch" || echo "0")
if [ $PROFIT_MISMATCH -gt 0 ]; then
    echo "   - Profit mismatches: $PROFIT_MISMATCH times"
fi

# Cost validation issues
COST_TOO_LOW=$(echo "$LOGS" | grep -c "Cost too low" || echo "0")
if [ $COST_TOO_LOW -gt 0 ]; then
    echo "   - Cost too low: $COST_TOO_LOW times"
fi

# Extract recent crops tested
echo ""
echo "🌾 Recent Crops Tested:"
echo "======================"
echo "$LOGS" | grep "Extracted crop from AI response:" | tail -10 | sed 's/.*response: /   - /'

# Extract recent final budgets
echo ""
echo "💰 Recent Final Budgets:"
echo "======================="
echo "$LOGS" | grep "\[FINAL\] Crop:" | tail -5 | while read line; do
    echo "   $line"
done

# Check for errors
echo ""
echo "❌ Recent Errors:"
echo "================"
ERRORS=$(echo "$LOGS" | grep -i "error\|exception\|failed" | grep -v "SANITY CHECK FAILED" | grep -v "UNREALISTIC ROI" | tail -10)
if [ -z "$ERRORS" ]; then
    echo "   No critical errors found ✅"
else
    echo "$ERRORS" | sed 's/^/   /'
fi

# Performance metrics
echo ""
echo "⚡ Performance Metrics:"
echo "====================="
AVG_RESPONSE_TIME=$(echo "$LOGS" | grep "Billed Duration:" | awk '{print $4}' | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print 0}')
echo "   Average response time: ${AVG_RESPONSE_TIME}ms"

# Model usage
echo ""
echo "🤖 Model Usage:"
echo "=============="
CLAUDE_46=$(echo "$LOGS" | grep -c "claude-sonnet-4-6" || echo "0")
echo "   Claude Sonnet 4.6: $CLAUDE_46 calls"

# Save detailed analysis
echo ""
echo "💾 Saving detailed logs..."
echo "$LOGS" > /tmp/lambda_logs_analysis.txt
echo "   Saved to: /tmp/lambda_logs_analysis.txt"

echo ""
echo "✅ Analysis complete!"
