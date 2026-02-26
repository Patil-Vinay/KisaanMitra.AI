# PowerShell deployment script for Windows
# Deploy Updated Lambda with Enhanced Onboarding Check

Write-Host "Deploying Updated KisaanMitra Lambda with Enhanced Onboarding..." -ForegroundColor Green

# Configuration
$FUNCTION_NAME = "kisaanmitra-whatsapp"
$REGION = "ap-south-1"

# Clean up old package
Write-Host "Cleaning up old package..." -ForegroundColor Yellow
if (Test-Path "package") {
    Remove-Item -Recurse -Force package
}
if (Test-Path "lambda_deployment.zip") {
    Remove-Item -Force lambda_deployment.zip
}

# Create package directory
New-Item -ItemType Directory -Path package | Out-Null

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install boto3 urllib3 langgraph gremlinpython -t package -q

# Copy source files
Write-Host "Copying source files..." -ForegroundColor Yellow
Copy-Item lambda_whatsapp_kisaanmitra.py package/
Copy-Item agent_router.py package/
if (Test-Path "market_data_sources.py") {
    Copy-Item market_data_sources.py package/
}

# Copy onboarding module
Write-Host "Copying onboarding module..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path package/onboarding -Force | Out-Null
Copy-Item ../onboarding/farmer_onboarding.py package/onboarding/
New-Item -ItemType File -Path package/onboarding/__init__.py -Force | Out-Null

# Copy knowledge graph module
Write-Host "Copying knowledge graph module..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path package/knowledge_graph -Force | Out-Null
Copy-Item ../knowledge_graph/village_graph.py package/knowledge_graph/
New-Item -ItemType File -Path package/knowledge_graph/__init__.py -Force | Out-Null

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Set-Location package
Compress-Archive -Path * -DestinationPath ../lambda_deployment.zip -Force
Set-Location ..

# Check package size
$packageSize = (Get-Item lambda_deployment.zip).Length / 1MB
Write-Host "Package size: $([math]::Round($packageSize, 2)) MB" -ForegroundColor Cyan

# Upload to Lambda
Write-Host "Uploading to Lambda..." -ForegroundColor Yellow
aws lambda update-function-code `
    --function-name $FUNCTION_NAME `
    --zip-file fileb://lambda_deployment.zip `
    --region $REGION

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}

# Wait for update to complete
Write-Host "Waiting for Lambda update..." -ForegroundColor Yellow
aws lambda wait function-updated `
    --function-name $FUNCTION_NAME `
    --region $REGION

# Update timeout and memory
Write-Host "Updating Lambda configuration..." -ForegroundColor Yellow
aws lambda update-function-configuration `
    --function-name $FUNCTION_NAME `
    --timeout 60 `
    --memory-size 1024 `
    --region $REGION `
    2>$null

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Function: $FUNCTION_NAME"
Write-Host "  Region: $REGION"
Write-Host "  Package: $([math]::Round($packageSize, 2)) MB"
Write-Host ""
Write-Host "Key Changes:" -ForegroundColor Cyan
Write-Host "  - ALWAYS checks if user is new (first priority)"
Write-Host "  - Blocks non-text messages during onboarding"
Write-Host "  - Enhanced logging with emojis"
Write-Host "  - Helper function: check_user_status()"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test with new user: Send 'Hi' to WhatsApp"
Write-Host "  2. Monitor logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
Write-Host "  3. Verify onboarding flow completes"
Write-Host "  4. Check DynamoDB: kisaanmitra-user-profiles"
Write-Host ""
Write-Host "Ready to onboard farmers!" -ForegroundColor Green
