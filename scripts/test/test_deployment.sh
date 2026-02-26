#!/bin/bash

# KisaanMitra.AI - Comprehensive Deployment Test
# Tests all components: AWS connection, S3, Secrets, Lambda

set -e

echo "🧪 KisaanMitra.AI - Deployment Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test result
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

# Test 1: AWS CLI installed
echo "Test 1: AWS CLI Installation"
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    echo "AWS CLI Version: $AWS_VERSION"
    test_result 0 "AWS CLI is installed"
else
    test_result 1 "AWS CLI is not installed"
fi

# Test 2: AWS Configuration
echo "Test 2: AWS Configuration"
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    USER=$(aws sts get-caller-identity --query Arn --output text)
    echo "Account: $ACCOUNT"
    echo "User: $USER"
    test_result 0 "AWS credentials are configured"
else
    test_result 1 "AWS credentials not configured"
fi

# Test 3: Secrets Manager - API Key
echo "Test 3: Secrets Manager - API Key"
if aws secretsmanager get-secret-value --secret-id kisaanmitra/crop-health-api --region ap-south-1 &> /dev/null; then
    echo "Secret exists: kisaanmitra/crop-health-api"
    test_result 0 "API key stored in Secrets Manager"
else
    test_result 1 "API key not found in Secrets Manager"
fi

# Test 4: S3 Bucket
echo "Test 4: S3 Bucket"
if aws s3 ls s3://kisaanmitra-images &> /dev/null; then
    echo "Bucket exists: kisaanmitra-images"
    test_result 0 "S3 bucket exists"
else
    test_result 1 "S3 bucket not found"
fi

# Test 5: Test Image in S3
echo "Test 5: Test Image in S3"
if aws s3 ls s3://kisaanmitra-images/test/crop.jpg &> /dev/null; then
    SIZE=$(aws s3 ls s3://kisaanmitra-images/test/crop.jpg --human-readable | awk '{print $3, $4}')
    echo "Image found: test/crop.jpg ($SIZE)"
    test_result 0 "Test image exists in S3"
else
    echo "Uploading test image..."
    if [ -f "assets/test_images/2.jpg" ]; then
        aws s3 cp assets/test_images/2.jpg s3://kisaanmitra-images/test/crop.jpg
        test_result 0 "Test image uploaded to S3"
    else
        test_result 1 "Test image not found locally"
    fi
fi

# Test 6: IAM Role
echo "Test 6: IAM Role"
if aws iam get-role --role-name kisaanmitra-lambda-role --region ap-south-1 &> /dev/null; then
    echo "Role exists: kisaanmitra-lambda-role"
    test_result 0 "IAM role exists"
else
    test_result 1 "IAM role not found"
fi

# Test 7: Lambda Function
echo "Test 7: Lambda Function"
if aws lambda get-function --function-name kisaanmitra-crop-agent --region ap-south-1 &> /dev/null; then
    RUNTIME=$(aws lambda get-function-configuration --function-name kisaanmitra-crop-agent --region ap-south-1 --query Runtime --output text)
    MEMORY=$(aws lambda get-function-configuration --function-name kisaanmitra-crop-agent --region ap-south-1 --query MemorySize --output text)
    TIMEOUT=$(aws lambda get-function-configuration --function-name kisaanmitra-crop-agent --region ap-south-1 --query Timeout --output text)
    echo "Runtime: $RUNTIME"
    echo "Memory: ${MEMORY}MB"
    echo "Timeout: ${TIMEOUT}s"
    test_result 0 "Lambda function exists"
else
    test_result 1 "Lambda function not found"
fi

# Test 8: Lambda Invocation
echo "Test 8: Lambda Function Invocation"
if [ -f "src/lambda/test_event.json" ]; then
    echo "Invoking Lambda function..."
    if aws lambda invoke \
        --function-name kisaanmitra-crop-agent \
        --cli-binary-format raw-in-base64-out \
        --payload file://src/lambda/test_event.json \
        --region ap-south-1 \
        /tmp/response.json &> /dev/null; then
        
        # Check response
        if [ -f "/tmp/response.json" ]; then
            STATUS=$(cat /tmp/response.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('statusCode', 'N/A'))" 2>/dev/null || echo "N/A")
            
            if [ "$STATUS" = "200" ]; then
                echo "Status Code: $STATUS"
                DISEASE=$(cat /tmp/response.json | python3 -c "import sys, json; body=json.loads(json.load(sys.stdin)['body']); print(body.get('disease', {}).get('name', 'N/A'))" 2>/dev/null || echo "N/A")
                CONFIDENCE=$(cat /tmp/response.json | python3 -c "import sys, json; body=json.loads(json.load(sys.stdin)['body']); print(body.get('disease', {}).get('confidence', 'N/A'))" 2>/dev/null || echo "N/A")
                echo "Disease Detected: $DISEASE"
                echo "Confidence: $CONFIDENCE%"
                test_result 0 "Lambda function executed successfully"
            else
                echo "Status Code: $STATUS"
                test_result 1 "Lambda returned non-200 status"
            fi
        else
            test_result 1 "Response file not created"
        fi
    else
        test_result 1 "Lambda invocation failed"
    fi
else
    test_result 1 "Test event file not found"
fi

# Test 9: CloudWatch Logs
echo "Test 9: CloudWatch Logs"
if aws logs describe-log-streams \
    --log-group-name /aws/lambda/kisaanmitra-crop-agent \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --region ap-south-1 &> /dev/null; then
    echo "Log group exists: /aws/lambda/kisaanmitra-crop-agent"
    test_result 0 "CloudWatch logs accessible"
else
    test_result 1 "CloudWatch logs not found"
fi

# Test 10: Local Crop Health API
echo "Test 10: Local Crop Health API"
if [ -f "src/crop_agent/crop_health_api.py" ]; then
    echo "Crop Health API file exists"
    test_result 0 "Local API client available"
else
    test_result 1 "Local API client not found"
fi

# Summary
echo ""
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Deployment is ready.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Please review the output above.${NC}"
    exit 1
fi
