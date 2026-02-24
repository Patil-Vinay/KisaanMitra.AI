# AWS Setup & Lambda Integration - Step-by-Step Guide

## Prerequisites Checklist

- [ ] AWS Account (free tier works)
- [ ] AWS CLI installed
- [ ] Python 3.11+ installed
- [ ] Crop Health API key from Kindwise
- [ ] Terminal/Command Prompt access

---

## Part 1: AWS Account Setup (10 minutes)

### Step 1: Create AWS Account (if you don't have one)

1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Fill in email, password, account name
4. Add payment method (won't be charged on free tier)
5. Verify phone number
6. Choose "Basic Support - Free"
7. Wait for account activation email

### Step 2: Create IAM User (Security Best Practice)

1. **Login to AWS Console**: https://console.aws.amazon.com/
2. **Search for "IAM"** in the top search bar
3. Click **"Users"** in left sidebar
4. Click **"Create user"**
5. **User details**:
   - Username: `kisaanmitra-admin`
   - Check: "Provide user access to AWS Management Console"
   - Choose: "I want to create an IAM user"
   - Click "Next"

6. **Set permissions**:
   - Choose: "Attach policies directly"
   - Search and select these policies:
     - ✅ `AdministratorAccess` (for full access)
     - OR for minimal permissions:
       - ✅ `AWSLambda_FullAccess`
       - ✅ `IAMFullAccess`
       - ✅ `AmazonS3FullAccess`
       - ✅ `SecretsManagerReadWrite`
   - Click "Next"

7. **Review and create**:
   - Click "Create user"
   - **IMPORTANT**: Download the CSV with credentials
   - Save the Access Key ID and Secret Access Key

---

## Part 2: Install & Configure AWS CLI (5 minutes)

### Step 1: Install AWS CLI

**macOS** (you're on macOS):
```bash
# Using Homebrew
brew install awscli

# Verify installation
aws --version
# Should show: aws-cli/2.x.x
```

**Windows**:
```powershell
# Download installer from:
# https://awscli.amazonaws.com/AWSCLIV2.msi
# Run the installer
```

**Linux**:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Step 2: Configure AWS CLI

```bash
aws configure
```

You'll be prompted for:
```
AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: ap-south-1
Default output format [None]: json
```

**Get your credentials from**:
- The CSV file you downloaded
- OR IAM Console → Users → Security credentials → Create access key

### Step 3: Verify Configuration

```bash
# Test AWS connection
aws sts get-caller-identity

# Should return:
# {
#     "UserId": "AIDAXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/kisaanmitra-admin"
# }
```

✅ If you see your account details, AWS CLI is configured correctly!

---

## Part 3: Store API Key in AWS Secrets Manager (2 minutes)

### Step 1: Create Secret

```bash
aws secretsmanager create-secret \
    --name kisaanmitra/crop-health-api \
    --description "Crop Health API key for disease detection" \
    --secret-string '{"CROP_HEALTH_API_KEY":"YOUR_CROP_HEALTH_API_KEY"}' \
    --region ap-south-1
```

**Expected output**:
```json
{
    "ARN": "arn:aws:secretsmanager:ap-south-1:123456789012:secret:kisaanmitra/crop-health-api-AbCdEf",
    "Name": "kisaanmitra/crop-health-api",
    "VersionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### Step 2: Verify Secret

```bash
aws secretsmanager get-secret-value \
    --secret-id kisaanmitra/crop-health-api \
    --region ap-south-1
```

✅ If you see your API key, secret is stored correctly!

---

## Part 4: Create S3 Bucket for Images (2 minutes)

### Step 1: Create Bucket

```bash
aws s3 mb s3://kisaanmitra-images --region ap-south-1
```

**Expected output**:
```
make_bucket: kisaanmitra-images
```

### Step 2: Enable Versioning (Optional but Recommended)

```bash
aws s3api put-bucket-versioning \
    --bucket kisaanmitra-images \
    --versioning-configuration Status=Enabled \
    --region ap-south-1
```

### Step 3: Upload Test Image

```bash
aws s3 cp assets/test_images/2.jpg s3://kisaanmitra-images/test/crop_image.jpg
```

**Expected output**:
```
upload: assets/test_images/2.jpg to s3://kisaanmitra-images/test/crop_image.jpg
```

### Step 4: Verify Upload

```bash
aws s3 ls s3://kisaanmitra-images/test/
```

✅ If you see `crop_image.jpg`, upload successful!

---

## Part 5: Deploy Lambda Function (5 minutes)

### Step 1: Navigate to Lambda Directory

```bash
cd src/lambda
```

### Step 2: Make Deployment Script Executable

```bash
chmod +x deploy_lambda.sh
```

### Step 3: Run Deployment

```bash
./deploy_lambda.sh
```

**What this script does**:
1. ✅ Creates deployment package with dependencies
2. ✅ Creates IAM role with necessary permissions
3. ✅ Deploys Lambda function
4. ✅ Configures environment variables

**Expected output** (takes 2-3 minutes):
```
🚀 Deploying KisaanMitra.AI Crop Agent to AWS Lambda...
📦 Creating deployment package...
✅ Deployment package created: lambda_deployment.zip
🔐 Checking IAM role...
✅ IAM role created
⚡ Deploying Lambda function...
✅ Lambda function deployed successfully!
🎉 Deployment complete!
```

### Step 4: Verify Lambda Function

```bash
aws lambda get-function \
    --function-name kisaanmitra-crop-agent \
    --region ap-south-1
```

✅ If you see function details, Lambda is deployed!

---

## Part 6: Test Lambda Function (3 minutes)

### Step 1: Update Test Event

Edit `test_event.json`:
```json
{
  "image_source": "s3",
  "s3_bucket": "kisaanmitra-images",
  "s3_key": "test/crop_image.jpg",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "language": "hi"
}
```

### Step 2: Invoke Lambda Function

```bash
aws lambda invoke \
    --function-name kisaanmitra-crop-agent \
    --payload file://test_event.json \
    --region ap-south-1 \
    response.json
```

**Expected output**:
```json
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
```

### Step 3: View Response

```bash
cat response.json | python3 -m json.tool
```

**Expected response**:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": {
    "message": "🌾 फसल रोग पहचान\n\nरोग: sugarcane rust\nविश्वास स्तर: 99.0%\n\n...",
    "disease": {
      "name": "sugarcane rust",
      "scientific_name": "Puccinia melanocephala",
      "confidence": 99.0,
      "id": "081a574211a34cf3"
    },
    "crop": {
      "name": "sugarcane",
      "scientific_name": "Saccharum officinarum",
      "confidence": 24.1
    }
  }
}
```

✅ **SUCCESS!** Your Lambda function is working!

---

## Part 7: Monitor Lambda Function (2 minutes)

### View CloudWatch Logs

```bash
# Get log streams
aws logs describe-log-streams \
    --log-group-name /aws/lambda/kisaanmitra-crop-agent \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --region ap-south-1

# View latest logs
aws logs tail /aws/lambda/kisaanmitra-crop-agent \
    --follow \
    --region ap-south-1
```

### Check Lambda Metrics

```bash
# Get invocation count
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=kisaanmitra-crop-agent \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum \
    --region ap-south-1
```

---

## Part 8: Test with Different Images (Optional)

### Upload Your Own Image

```bash
# Upload new image
aws s3 cp /path/to/your/crop_image.jpg s3://kisaanmitra-images/test/my_crop.jpg

# Update test_event.json
# Change "s3_key": "test/my_crop.jpg"

# Test again
aws lambda invoke \
    --function-name kisaanmitra-crop-agent \
    --payload file://test_event.json \
    --region ap-south-1 \
    response.json

# View result
cat response.json | python3 -m json.tool
```

---

## Troubleshooting

### Issue 1: "AccessDenied" Error

**Problem**: IAM permissions not set correctly

**Solution**:
```bash
# Check current user
aws sts get-caller-identity

# Verify IAM role exists
aws iam get-role --role-name kisaanmitra-lambda-role --region ap-south-1

# If role doesn't exist, run deployment script again
cd src/lambda
./deploy_lambda.sh
```

### Issue 2: "Secret not found"

**Problem**: Secret not created or wrong region

**Solution**:
```bash
# List secrets
aws secretsmanager list-secrets --region ap-south-1

# Create secret if missing
aws secretsmanager create-secret \
    --name kisaanmitra/crop-health-api \
    --secret-string '{"CROP_HEALTH_API_KEY":"YOUR_KEY"}' \
    --region ap-south-1
```

### Issue 3: "Bucket does not exist"

**Problem**: S3 bucket not created

**Solution**:
```bash
# Create bucket
aws s3 mb s3://kisaanmitra-images --region ap-south-1

# Verify
aws s3 ls
```

### Issue 4: Lambda Timeout

**Problem**: Function takes too long (>30s)

**Solution**:
```bash
# Increase timeout to 60 seconds
aws lambda update-function-configuration \
    --function-name kisaanmitra-crop-agent \
    --timeout 60 \
    --region ap-south-1
```

### Issue 5: "Module not found" in Lambda

**Problem**: Dependencies not packaged correctly

**Solution**:
```bash
cd src/lambda
rm -rf package lambda_deployment.zip
./deploy_lambda.sh
```

---

## Cost Monitoring

### Check Current Costs

```bash
# Get cost for last 7 days
aws ce get-cost-and-usage \
    --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --granularity DAILY \
    --metrics BlendedCost \
    --region us-east-1
```

### Set Budget Alert

```bash
# Create budget (via AWS Console)
# 1. Go to AWS Billing Console
# 2. Click "Budgets"
# 3. Create budget: $10/month
# 4. Set alert at 80% ($8)
```

---

## Next Steps

✅ **You've successfully**:
1. Connected AWS account
2. Configured AWS CLI
3. Stored API key securely
4. Created S3 bucket
5. Deployed Lambda function
6. Tested disease detection

🚀 **What's next**:
1. Integrate with WhatsApp Business API
2. Add more test images
3. Implement caching (DynamoDB)
4. Set up API Gateway for HTTP endpoint
5. Add monitoring dashboards
6. Deploy to production

---

## Quick Reference Commands

```bash
# Test Lambda
aws lambda invoke --function-name kisaanmitra-crop-agent --payload file://test_event.json response.json --region ap-south-1

# View logs
aws logs tail /aws/lambda/kisaanmitra-crop-agent --follow --region ap-south-1

# Upload image
aws s3 cp image.jpg s3://kisaanmitra-images/test/

# Update Lambda code
cd src/lambda && ./deploy_lambda.sh

# Check costs
aws ce get-cost-and-usage --time-period Start=2024-02-01,End=2024-02-25 --granularity MONTHLY --metrics BlendedCost
```

---

**Status**: Ready for Production ✅  
**Support**: Check CloudWatch Logs for debugging  
**Team**: KisaanMitra.AI
