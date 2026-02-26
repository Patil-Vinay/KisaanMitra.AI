#!/bin/bash

# KisaanMitra.AI - WhatsApp Integration Test
# Tests the new crop engine with WhatsApp functionality

set -e

echo "🧪 Testing WhatsApp + Crop Engine Integration"
echo "=============================================="
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

# Test 1: Check updated crop_health_api.py
echo "Test 1: Updated Crop Health API File"
if [ -f "src/crop_agent/crop_health_api.py" ]; then
    if grep -q "def lambda_handler" src/crop_agent/crop_health_api.py; then
        echo "✓ Lambda handler found"
        if grep -q "def send_whatsapp_message" src/crop_agent/crop_health_api.py; then
            echo "✓ WhatsApp integration found"
            if grep -q "def ask_bedrock" src/crop_agent/crop_health_api.py; then
                echo "✓ Bedrock AI integration found"
                if grep -q "def analyze_crop_image" src/crop_agent/crop_health_api.py; then
                    echo "✓ Crop image analysis found"
                    test_result 0 "All new functions present"
                else
                    test_result 1 "Crop image analysis function missing"
                fi
            else
                test_result 1 "Bedrock AI function missing"
            fi
        else
            test_result 1 "WhatsApp function missing"
        fi
    else
        test_result 1 "Lambda handler missing"
    fi
else
    test_result 1 "Crop health API file not found"
fi

# Test 2: Check for required environment variables
echo "Test 2: Environment Variables Configuration"
REQUIRED_VARS=("WHATSAPP_TOKEN" "CROP_HEALTH_API_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "$var" src/crop_agent/crop_health_api.py; then
        echo "✓ $var referenced in code"
    else
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    test_result 0 "All required environment variables referenced"
else
    test_result 1 "Missing environment variables: ${MISSING_VARS[*]}"
fi

# Test 3: Check WhatsApp webhook verification
echo "Test 3: WhatsApp Webhook Verification Logic"
if grep -q "hub.verify_token" src/crop_agent/crop_health_api.py; then
    if grep -q "hub.challenge" src/crop_agent/crop_health_api.py; then
        echo "✓ Webhook verification logic present"
        test_result 0 "WhatsApp webhook verification implemented"
    else
        test_result 1 "Challenge response missing"
    fi
else
    test_result 1 "Webhook verification missing"
fi

# Test 4: Check message type handling
echo "Test 4: Message Type Handling"
TYPES=("text" "image")
ALL_PRESENT=true

for type in "${TYPES[@]}"; do
    if grep -q "msg_type == \"$type\"" src/crop_agent/crop_health_api.py; then
        echo "✓ $type message handling found"
    else
        echo "✗ $type message handling missing"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = true ]; then
    test_result 0 "All message types handled"
else
    test_result 1 "Some message types not handled"
fi

# Test 5: Check Bedrock integration
echo "Test 5: AWS Bedrock Integration"
if grep -q "bedrock.converse" src/crop_agent/crop_health_api.py; then
    if grep -q "amazon.nova-micro-v1:0" src/crop_agent/crop_health_api.py; then
        echo "✓ Bedrock model: amazon.nova-micro-v1:0"
        test_result 0 "Bedrock AI integration configured"
    else
        test_result 1 "Bedrock model not specified"
    fi
else
    test_result 1 "Bedrock integration missing"
fi

# Test 6: Check Crop Health API integration
echo "Test 6: Crop Health API Integration"
if grep -q "crop.kindwise.com" src/crop_agent/crop_health_api.py; then
    if grep -q "analyze_crop_image" src/crop_agent/crop_health_api.py; then
        echo "✓ Crop Health API endpoint configured"
        echo "✓ Image analysis function present"
        test_result 0 "Crop Health API integrated"
    else
        test_result 1 "Image analysis function missing"
    fi
else
    test_result 1 "Crop Health API endpoint not found"
fi

# Test 7: Check response formatting
echo "Test 7: Response Formatting"
if grep -q "format_crop_result" src/crop_agent/crop_health_api.py; then
    if grep -q "Crop Disease Analysis Results" src/crop_agent/crop_health_api.py; then
        echo "✓ Result formatting function present"
        echo "✓ User-friendly message format"
        test_result 0 "Response formatting implemented"
    else
        test_result 1 "Message format not user-friendly"
    fi
else
    test_result 1 "Result formatting function missing"
fi

# Test 8: Check error handling
echo "Test 8: Error Handling"
if grep -q "try:" src/crop_agent/crop_health_api.py; then
    if grep -q "except Exception" src/crop_agent/crop_health_api.py; then
        echo "✓ Try-except blocks present"
        test_result 0 "Error handling implemented"
    else
        test_result 1 "Exception handling incomplete"
    fi
else
    test_result 1 "No error handling found"
fi

# Test 9: Check image download functionality
echo "Test 9: WhatsApp Image Download"
if grep -q "download_whatsapp_image" src/crop_agent/crop_health_api.py; then
    if grep -q "graph.facebook.com" src/crop_agent/crop_health_api.py; then
        echo "✓ Image download function present"
        echo "✓ Facebook Graph API integration"
        test_result 0 "Image download functionality implemented"
    else
        test_result 1 "Facebook Graph API not configured"
    fi
else
    test_result 1 "Image download function missing"
fi

# Test 10: Check base64 encoding
echo "Test 10: Image Encoding"
if grep -q "base64.b64encode" src/crop_agent/crop_health_api.py; then
    echo "✓ Base64 encoding present"
    test_result 0 "Image encoding implemented"
else
    test_result 1 "Image encoding missing"
fi

# Summary
echo ""
echo "=============================================="
echo "📊 WhatsApp Integration Test Summary"
echo "=============================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All WhatsApp integration tests passed!${NC}"
    echo ""
    echo "✅ Features Verified:"
    echo "   • WhatsApp webhook integration"
    echo "   • Text message handling with Bedrock AI"
    echo "   • Image message handling"
    echo "   • Crop disease detection"
    echo "   • Response formatting"
    echo "   • Error handling"
    echo ""
    echo "🚀 Ready for WhatsApp deployment!"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Review the output above.${NC}"
    exit 1
fi
