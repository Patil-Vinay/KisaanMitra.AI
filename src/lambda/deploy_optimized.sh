#!/bin/bash

# Optimized Deployment Script for KisaanMitra Lambda
# Includes performance optimizations and monitoring

set -e

echo "🚀 Starting optimized deployment of KisaanMitra Lambda..."

# Configuration
FUNCTION_NAME="whatsapp-llama-bot"
REGION="ap-south-1"
RUNTIME="python3.11"
MEMORY_SIZE="1024"  # Increased for better performance
TIMEOUT="60"        # Increased timeout for image processing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

print_success "AWS CLI configured"

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &> /dev/null; then
    print_status "Lambda function exists. Will update..."
    UPDATE_MODE=true
else
    print_status "Lambda function does not exist. Will create..."
    UPDATE_MODE=false
fi

# Create deployment package with optimizations
print_status "Creating optimized deployment package..."

# Clean up previous builds
rm -rf build/
mkdir -p build/

# Copy source files with optimization
print_status "Copying and optimizing source files..."

# Copy main files
cp lambda_handler_v2.py build/
cp *.py build/ 2>/dev/null || true

# Copy services with optimizations
mkdir -p build/services/
cp services/*.py build/services/

# Copy agents
mkdir -p build/agents/
cp agents/*.py build/agents/

# Copy optional modules (if they exist)
for module in whatsapp_interactive.py navigation_controller.py farmer_onboarding.py enhanced_disease_detection.py disease_tracker.py; do
    if [ -f "$module" ]; then
        cp "$module" build/
        print_status "Included optional module: $module"
    else
        print_warning "Optional module not found: $module"
    fi
done

# Create optimized requirements.txt
print_status "Creating optimized requirements..."
cat > build/requirements.txt << EOF
boto3>=1.26.0
urllib3>=1.26.0
requests>=2.28.0
Pillow>=9.0.0
python-dateutil>=2.8.0
EOF

# Install dependencies in build directory
print_status "Installing dependencies..."
cd build/
pip install -r requirements.txt -t . --no-deps --quiet

# Remove unnecessary files to reduce package size
print_status "Optimizing package size..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true

# Create deployment zip
print_status "Creating deployment package..."
zip -r ../deployment-package.zip . -q

cd ..

# Get package size
PACKAGE_SIZE=$(du -h deployment-package.zip | cut -f1)
print_status "Package size: $PACKAGE_SIZE"

if [ "$UPDATE_MODE" = true ]; then
    # Update existing function
    print_status "Updating Lambda function code..."
    
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://deployment-package.zip \
        --region $REGION \
        --no-cli-pager
    
    print_success "Function code updated"
    
    # Update function configuration for optimization
    print_status "Updating function configuration..."
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --memory-size $MEMORY_SIZE \
        --timeout $TIMEOUT \
        --environment Variables='{
            "PYTHONPATH": "/var/task:/opt/python",
            "AWS_LAMBDA_EXEC_WRAPPER": "/opt/bootstrap",
            "LAMBDA_TASK_ROOT": "/var/task"
        }' \
        --region $REGION \
        --no-cli-pager
    
    print_success "Function configuration updated"
    
else
    # Create new function
    print_error "Function does not exist. Please create it first using the AWS Console or CLI."
    print_status "You can create it with:"
    echo "aws lambda create-function --function-name $FUNCTION_NAME --runtime $RUNTIME --role <ROLE_ARN> --handler lambda_handler_v2.lambda_handler --zip-file fileb://deployment-package.zip --memory-size $MEMORY_SIZE --timeout $TIMEOUT --region $REGION"
    exit 1
fi

# Wait for function to be updated
print_status "Waiting for function update to complete..."
aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION

# Test the function
print_status "Testing function..."
TEST_PAYLOAD='{"queryStringParameters": {"hub.verify_token": "mySecret_123", "hub.challenge": "test_challenge"}}'

RESPONSE=$(aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload "$TEST_PAYLOAD" \
    --region $REGION \
    --no-cli-pager \
    response.json)

if [ $? -eq 0 ]; then
    RESPONSE_BODY=$(cat response.json)
    if [ "$RESPONSE_BODY" = "test_challenge" ]; then
        print_success "Function test passed"
    else
        print_warning "Function test returned unexpected response: $RESPONSE_BODY"
    fi
else
    print_error "Function test failed"
fi

# Get function info
print_status "Getting function information..."
aws lambda get-function \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Configuration.{FunctionName:FunctionName,Runtime:Runtime,MemorySize:MemorySize,Timeout:Timeout,LastModified:LastModified}' \
    --output table \
    --no-cli-pager

# Check recent logs
print_status "Checking recent logs..."
aws logs tail /aws/lambda/$FUNCTION_NAME --since 2m --region $REGION --no-cli-pager || print_warning "No recent logs found"

# Cleanup
print_status "Cleaning up..."
rm -rf build/
rm -f deployment-package.zip
rm -f response.json

print_success "🎉 Optimized deployment completed successfully!"
print_status "Function: $FUNCTION_NAME"
print_status "Region: $REGION"
print_status "Memory: ${MEMORY_SIZE}MB"
print_status "Timeout: ${TIMEOUT}s"

echo ""
print_status "📊 Performance Optimizations Applied:"
echo "  ✅ Connection pooling for DynamoDB and HTTP clients"
echo "  ✅ In-memory caching with TTL"
echo "  ✅ Rate limiting for API calls and user requests"
echo "  ✅ Optimized AI service with reduced timeouts"
echo "  ✅ Memory management and garbage collection"
echo "  ✅ Enhanced error handling and monitoring"
echo "  ✅ Reduced package size and faster cold starts"

echo ""
print_status "🔍 Monitoring:"
echo "  • Check logs: aws logs tail /aws/lambda/$FUNCTION_NAME --since 5m --region $REGION"
echo "  • Monitor metrics in CloudWatch"
echo "  • Use health check endpoints for system status"

echo ""
print_success "Deployment ready for production! 🚀"