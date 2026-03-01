#!/bin/bash

# Deploy Farmer Count Fix to Lambda
# This script deploys the updated knowledge graph helper and Lambda handler

echo "=================================================="
echo "Deploying Farmer Count Query Fix"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "src/lambda/lambda_whatsapp_kisaanmitra.py" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Run tests first
echo ""
echo "Step 1: Running tests..."
python tests/test_farmer_count_fix.py
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Fix issues before deploying."
    exit 1
fi

echo ""
echo "✅ Tests passed!"

# Deploy to Lambda
echo ""
echo "Step 2: Deploying to Lambda..."
cd src/lambda

# Check if deploy script exists
if [ ! -f "deploy_whatsapp.sh" ]; then
    echo "❌ Error: deploy_whatsapp.sh not found"
    exit 1
fi

# Make sure it's executable
chmod +x deploy_whatsapp.sh

# Deploy
./deploy_whatsapp.sh

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ Deployment Complete!"
    echo "=================================================="
    echo ""
    echo "Next Steps:"
    echo "1. Test via WhatsApp: 'How many farmers are in my village'"
    echo "2. Expected: Should show 'Total Farmers in Village: 15'"
    echo "3. Test: 'Who else grows sugarcane'"
    echo "4. Expected: Should show 'Found 14 Other Farmer(s)'"
    echo ""
    echo "📝 See FARMER_COUNT_FIX.md for details"
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Check the error messages above"
    exit 1
fi
