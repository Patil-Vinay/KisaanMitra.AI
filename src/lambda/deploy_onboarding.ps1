# Deploy KisaanMitra WhatsApp Lambda with Onboarding
# Simple Windows PowerShell deployment script

Write-Host "=== KisaanMitra Lambda Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$FUNCTION_NAME = "whatsapp-llama-bot"
$REGION = "ap-south-1"
$RUNTIME = "python3.11"
$HANDLER = "lambda_whatsapp_kisaanmitra.lambda_handler"
$ROLE_NAME = "kisaanmitra-lambda-role"

# Step 1: Create deployment package directory
Write-Host "Step 1: Creating deployment package..." -ForegroundColor Yellow
if (Test-Path "deployment_package") {
    Remove-Item -Recurse -Force deployment_package
}
New-Item -ItemType Directory -Path deployment_package | Out-Null

# Step 2: Copy Lambda files
Write-Host "Step 2: Copying Lambda files..." -ForegroundColor Yellow
Copy-Item lambda_whatsapp_kisaanmitra.py deployment_package/
Copy-Item agent_router.py deployment_package/
Copy-Item market_data_sources.py deployment_package/

# Step 3: Copy onboarding module
Write-Host "Step 3: Copying onboarding module..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path deployment_package/onboarding -Force | Out-Null
Copy-Item ../onboarding/farmer_onboarding.py deployment_package/onboarding/
"" | Out-File -FilePath deployment_package/onboarding/__init__.py -Encoding utf8

# Step 4: Copy knowledge graph module
Write-Host "Step 4: Copying knowledge graph module..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path deployment_package/knowledge_graph -Force | Out-Null
Copy-Item ../knowledge_graph/village_graph.py deployment_package/knowledge_graph/
"" | Out-File -FilePath deployment_package/knowledge_graph/__init__.py -Encoding utf8

# Step 5: Create ZIP file
Write-Host "Step 5: Creating ZIP file..." -ForegroundColor Yellow
$zipFile = "lambda_onboarding_deployment.zip"
if (Test-Path $zipFile) {
    Remove-Item $zipFile
}

# Use PowerShell's Compress-Archive
Compress-Archive -Path deployment_package/* -DestinationPath $zipFile -Force

Write-Host "Step 6: Checking if Lambda function exists..." -ForegroundColor Yellow
$functionExists = $false
try {
    aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>$null
    $functionExists = $true
    Write-Host "Function exists, will update..." -ForegroundColor Green
} catch {
    Write-Host "Function doesn't exist, will create..." -ForegroundColor Green
}

if ($functionExists) {
    # Update existing function
    Write-Host "Step 7: Updating Lambda function code..." -ForegroundColor Yellow
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://$zipFile `
        --region $REGION
    
    Write-Host ""
    Write-Host "✅ Lambda function updated successfully!" -ForegroundColor Green
} else {
    # Get IAM role ARN
    Write-Host "Step 7: Getting IAM role ARN..." -ForegroundColor Yellow
    $roleArn = aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text
    
    if (-not $roleArn) {
        Write-Host "❌ Error: IAM role not found. Please create role first." -ForegroundColor Red
        Write-Host "Run: aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json" -ForegroundColor Yellow
        exit 1
    }
    
    # Create new function
    Write-Host "Step 8: Creating Lambda function..." -ForegroundColor Yellow
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime $RUNTIME `
        --role $roleArn `
        --handler $HANDLER `
        --zip-file fileb://$zipFile `
        --timeout 60 `
        --memory-size 512 `
        --region $REGION `
        --environment "Variables={VERIFY_TOKEN=mySecret_123}"
    
    Write-Host ""
    Write-Host "✅ Lambda function created successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set environment variables (WHATSAPP_TOKEN, PHONE_NUMBER_ID, etc.)" -ForegroundColor White
Write-Host "2. Create DynamoDB tables if not exists:" -ForegroundColor White
Write-Host "   - kisaanmitra-onboarding" -ForegroundColor White
Write-Host "   - kisaanmitra-user-profiles" -ForegroundColor White
Write-Host "   - kisaanmitra-conversations" -ForegroundColor White
Write-Host "3. Test the function with a WhatsApp message" -ForegroundColor White
Write-Host ""
