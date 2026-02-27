#!/bin/bash

# KisaanMitra - Deploy System Audit Fixes
# Date: February 27, 2026

set -e  # Exit on error

echo "========================================="
echo "KisaanMitra - Deploying System Fixes"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "src/lambda/lambda_whatsapp_kisaanmitra.py" ]; then
    echo -e "${RED}Error: Must run from project root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Backing up current Lambda code...${NC}"
aws lambda get-function --function-name kisaanmitra-whatsapp \
  --query 'Code.Location' --output text | xargs curl -s -o lambda_backup_$(date +%Y%m%d_%H%M%S).zip
echo -e "${GREEN}✓ Backup created${NC}"
echo ""

echo -e "${YELLOW}Step 2: Running diagnostics...${NC}"
# Check Python syntax
python3 -m py_compile src/lambda/lambda_whatsapp_kisaanmitra.py
python3 -m py_compile src/onboarding/farmer_onboarding.py
python3 -m py_compile src/lambda/whatsapp_interactive.py
python3 -m py_compile src/lambda/ai_orchestrator.py
echo -e "${GREEN}✓ All files pass syntax check${NC}"
echo ""

echo -e "${YELLOW}Step 3: Deploying to Lambda...${NC}"
cd src/lambda
chmod +x deploy_whatsapp.sh
./deploy_whatsapp.sh
cd ../..
echo -e "${GREEN}✓ Lambda deployed${NC}"
echo ""

echo -e "${YELLOW}Step 4: Verifying deployment...${NC}"
LAST_MODIFIED=$(aws lambda get-function-configuration \
  --function-name kisaanmitra-whatsapp \
  --query 'LastModified' --output text)
echo "Last Modified: $LAST_MODIFIED"
echo -e "${GREEN}✓ Deployment verified${NC}"
echo ""

echo -e "${YELLOW}Step 5: Testing language persistence...${NC}"
echo "Checking DynamoDB for language_preference entries..."
aws dynamodb scan \
  --table-name kisaanmitra-conversations \
  --filter-expression "attribute_exists(#lang)" \
  --expression-attribute-names '{"#lang":"language"}' \
  --select COUNT \
  --output text
echo -e "${GREEN}✓ DynamoDB check complete${NC}"
echo ""

echo "========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Test language selection (English/Hindi)"
echo "2. Test budget routing (click menu → type details)"
echo "3. Test market routing (type 'बाजार भाव')"
echo "4. Test greeting (existing user says 'Hi')"
echo "5. Monitor CloudWatch logs for 24 hours"
echo ""
echo "Monitoring:"
echo "  aws logs tail /aws/lambda/kisaanmitra-whatsapp --follow"
echo ""
echo "Rollback (if needed):"
echo "  aws lambda update-function-code \\"
echo "    --function-name kisaanmitra-whatsapp \\"
echo "    --zip-file fileb://lambda_backup_*.zip"
echo ""
echo -e "${GREEN}Good luck! 🚀${NC}"
