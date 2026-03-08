# Deploy SageMaker Forecasting Solution - Windows PowerShell
# No Docker required!

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SAGEMAKER FORECASTING DEPLOYMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$AWS_REGION = "ap-south-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$S3_BUCKET = "kisaanmitra-ml-data"
$LAMBDA_FUNCTION_NAME = "kisaanmitra-sagemaker-forecaster"
$SAGEMAKER_ROLE_NAME = "KisaanMitra-SageMaker-Role"
$LAMBDA_ROLE_NAME = "KisaanMitra-Lambda-SageMaker-Role"

Write-Host "AWS Account: $AWS_ACCOUNT_ID" -ForegroundColor Yellow
Write-Host "Region: $AWS_REGION" -ForegroundColor Yellow
Write-Host "S3 Bucket: $S3_BUCKET" -ForegroundColor Yellow
Write-Host ""

# Step 1: Create S3 bucket
Write-Host "Step 1: Creating S3 bucket..." -ForegroundColor Cyan
try {
    aws s3 mb s3://$S3_BUCKET --region $AWS_REGION 2>$null
    Write-Host "  ✅ S3 bucket created" -ForegroundColor Green
} catch {
    Write-Host "  ℹ️  Bucket already exists" -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Create SageMaker execution role
Write-Host "Step 2: Creating SageMaker execution role..." -ForegroundColor Cyan

$sagemakerTrustPolicyPath = "$env:TEMP\sagemaker-trust-policy.json"
@'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
'@ | Out-File -FilePath $sagemakerTrustPolicyPath -Encoding utf8

# Create role if it doesn't exist
try {
    aws iam get-role --role-name $SAGEMAKER_ROLE_NAME 2>$null | Out-Null
    Write-Host "  ℹ️  SageMaker role already exists" -ForegroundColor Yellow
} catch {
    aws iam create-role `
        --role-name $SAGEMAKER_ROLE_NAME `
        --assume-role-policy-document "file://$sagemakerTrustPolicyPath"
    Write-Host "  ✅ SageMaker role created" -ForegroundColor Green
}

# Attach policies
aws iam attach-role-policy `
    --role-name $SAGEMAKER_ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess 2>$null

aws iam attach-role-policy `
    --role-name $SAGEMAKER_ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess 2>$null

$SAGEMAKER_ROLE_ARN = "arn:aws:iam::${AWS_ACCOUNT_ID}:role/$SAGEMAKER_ROLE_NAME"
Write-Host "  ✅ SageMaker role: $SAGEMAKER_ROLE_ARN" -ForegroundColor Green
Write-Host ""

# Step 3: Create Lambda execution role
Write-Host "Step 3: Creating Lambda execution role..." -ForegroundColor Cyan

$lambdaTrustPolicyPath = "$env:TEMP\lambda-trust-policy.json"
@'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
'@ | Out-File -FilePath $lambdaTrustPolicyPath -Encoding utf8

# Create role if it doesn't exist
try {
    aws iam get-role --role-name $LAMBDA_ROLE_NAME 2>$null | Out-Null
    Write-Host "  ℹ️  Lambda role already exists" -ForegroundColor Yellow
} catch {
    aws iam create-role `
        --role-name $LAMBDA_ROLE_NAME `
        --assume-role-policy-document "file://$lambdaTrustPolicyPath"
    Write-Host "  ✅ Lambda role created" -ForegroundColor Green
}

# Attach policies
aws iam attach-role-policy `
    --role-name $LAMBDA_ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>$null

aws iam attach-role-policy `
    --role-name $LAMBDA_ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess 2>$null

aws iam attach-role-policy `
    --role-name $LAMBDA_ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess 2>$null

aws iam attach-role-policy `
    --role-name $LAMBDA_ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess 2>$null

$LAMBDA_ROLE_ARN = "arn:aws:iam::${AWS_ACCOUNT_ID}:role/$LAMBDA_ROLE_NAME"
Write-Host "  ✅ Lambda role: $LAMBDA_ROLE_ARN" -ForegroundColor Green
Write-Host ""

# Wait for roles to propagate
Write-Host "Waiting for IAM roles to propagate..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Step 4: Package Lambda function
Write-Host "Step 4: Packaging Lambda function..." -ForegroundColor Cyan

# Create temp directory for packaging
$tempDir = "$env:TEMP\lambda_sagemaker_package"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy Lambda function
Copy-Item "src\lambda\lambda_sagemaker_forecaster.py" "$tempDir\"

# Copy sagemaker_forecasting module
Copy-Item -Recurse "src\sagemaker_forecasting" "$tempDir\"

# Create zip
$zipPath = "$env:TEMP\lambda_sagemaker.zip"
if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}

# Use PowerShell compression
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath

Write-Host "  ✅ Lambda package created" -ForegroundColor Green
Write-Host ""

# Step 5: Create or update Lambda function
Write-Host "Step 5: Creating/updating Lambda function..." -ForegroundColor Cyan

$functionExists = $false
try {
    aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION 2>$null | Out-Null
    $functionExists = $true
} catch {}

if ($functionExists) {
    Write-Host "  Updating existing Lambda function..." -ForegroundColor Yellow
    aws lambda update-function-code `
        --function-name $LAMBDA_FUNCTION_NAME `
        --zip-file fileb://$zipPath `
        --region $AWS_REGION
} else {
    Write-Host "  Creating new Lambda function..." -ForegroundColor Yellow
    aws lambda create-function `
        --function-name $LAMBDA_FUNCTION_NAME `
        --runtime python3.11 `
        --role $LAMBDA_ROLE_ARN `
        --handler lambda_sagemaker_forecaster.lambda_handler `
        --zip-file fileb://$zipPath `
        --timeout 900 `
        --memory-size 512 `
        --environment ("Variables={S3_BUCKET=" + $S3_BUCKET + ",SAGEMAKER_ROLE_ARN=" + $SAGEMAKER_ROLE_ARN + ",DYNAMODB_TABLE=kisaanmitra-price-forecasts,USE_EXISTING_MODEL=false}") `
        --region $AWS_REGION
}

Write-Host "  ✅ Lambda function deployed" -ForegroundColor Green
Write-Host ""

# Step 6: Create EventBridge rule for weekly training
Write-Host "Step 6: Setting up weekly schedule..." -ForegroundColor Cyan

$RULE_NAME = "kisaanmitra-weekly-training"

# Create rule (runs every Sunday at 2 AM IST = Saturday 8:30 PM UTC)
aws events put-rule `
    --name $RULE_NAME `
    --schedule-expression 'cron(30 20 ? * SUN *)' `
    --state ENABLED `
    --region $AWS_REGION `
    --description "Weekly price forecasting training"

# Add Lambda permission
try {
    aws lambda add-permission `
        --function-name $LAMBDA_FUNCTION_NAME `
        --statement-id AllowEventBridgeInvoke `
        --action lambda:InvokeFunction `
        --principal events.amazonaws.com `
        --source-arn "arn:aws:events:${AWS_REGION}:${AWS_ACCOUNT_ID}:rule/$RULE_NAME" `
        --region $AWS_REGION 2>$null
} catch {
    Write-Host "  ℹ️  Permission already exists" -ForegroundColor Yellow
}

# Add Lambda as target
$LAMBDA_ARN = aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION --query 'Configuration.FunctionArn' --output text

aws events put-targets `
    --rule $RULE_NAME `
    --targets "Id=1,Arn=$LAMBDA_ARN" `
    --region $AWS_REGION

Write-Host "  ✅ Weekly schedule configured" -ForegroundColor Green
Write-Host ""

# Cleanup temp files
Remove-Item -Recurse -Force $tempDir
Remove-Item -Force $zipPath

Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Resources created:" -ForegroundColor Cyan
Write-Host "  • S3 Bucket: $S3_BUCKET"
Write-Host "  • SageMaker Role: $SAGEMAKER_ROLE_ARN"
Write-Host "  • Lambda Function: $LAMBDA_FUNCTION_NAME"
Write-Host "  • Schedule: Weekly on Sunday at 2 AM IST"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test Lambda manually:"
Write-Host "   aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --region $AWS_REGION output.json"
Write-Host ""
Write-Host "2. First run will create AutoML training job (takes 1-2 hours)"
Write-Host ""
Write-Host "3. After training completes, set USE_EXISTING_MODEL=true:"
Write-Host "   aws lambda update-function-configuration \"
Write-Host "     --function-name $LAMBDA_FUNCTION_NAME \"
Write-Host "     --environment `"Variables={S3_BUCKET=$S3_BUCKET,SAGEMAKER_ROLE_ARN=$SAGEMAKER_ROLE_ARN,DYNAMODB_TABLE=kisaanmitra-price-forecasts,USE_EXISTING_MODEL=true}`" \"
Write-Host "     --region $AWS_REGION"
Write-Host ""
Write-Host "4. Monitor SageMaker jobs in AWS Console"
Write-Host ""
