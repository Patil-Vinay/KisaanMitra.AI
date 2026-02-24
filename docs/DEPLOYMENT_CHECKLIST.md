# KisaanMitra.AI - Deployment Checklist

## Pre-Deployment Checklist

### AWS Account Setup
- [ ] AWS account created
- [ ] IAM user created with admin access
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS CLI configured (`aws configure`)
- [ ] Test AWS connection (`aws sts get-caller-identity`)

### API Keys & Secrets
- [ ] Crop Health API key obtained from Kindwise
- [ ] Secret created in AWS Secrets Manager
- [ ] Secret verified (`aws secretsmanager get-secret-value --secret-id kisaanmitra/crop-health-api`)

### S3 Setup
- [ ] S3 bucket created (`kisaanmitra-images`)
- [ ] Test image uploaded
- [ ] Bucket verified (`aws s3 ls s3://kisaanmitra-images/`)

## Deployment Checklist

### Lambda Function
- [ ] Navigate to `src/lambda` directory
- [ ] Make deploy script executable (`chmod +x deploy_lambda.sh`)
- [ ] Run deployment (`./deploy_lambda.sh`)
- [ ] Verify function exists (`aws lambda get-function --function-name kisaanmitra-crop-agent`)

### Testing
- [ ] Update `test_event.json` with correct S3 path
- [ ] Invoke Lambda function
- [ ] Check response.json for results
- [ ] Verify disease detection works (99% confidence for sugarcane rust)

### Monitoring
- [ ] CloudWatch Logs accessible
- [ ] Metrics visible in CloudWatch
- [ ] Budget alert set ($10/month)

## Post-Deployment Checklist

### Verification
- [ ] Lambda function responds in <5 seconds
- [ ] Disease detection accuracy >95%
- [ ] Hindi response formatting works
- [ ] S3 image retrieval works
- [ ] Secrets Manager integration works

### Documentation
- [ ] Team has access to AWS account
- [ ] Deployment guide shared
- [ ] Troubleshooting steps documented
- [ ] Cost monitoring set up

### Next Steps
- [ ] Integrate with WhatsApp Business API
- [ ] Add more test images
- [ ] Set up API Gateway (optional)
- [ ] Implement caching layer
- [ ] Add monitoring dashboards

## Quick Test Commands

```bash
# 1. Test AWS connection
aws sts get-caller-identity

# 2. Check secret
aws secretsmanager get-secret-value --secret-id kisaanmitra/crop-health-api --region ap-south-1

# 3. List S3 bucket
aws s3 ls s3://kisaanmitra-images/

# 4. Test Lambda
cd src/lambda
aws lambda invoke --function-name kisaanmitra-crop-agent --payload file://test_event.json response.json --region ap-south-1

# 5. View result
cat response.json | python3 -m json.tool

# 6. Check logs
aws logs tail /aws/lambda/kisaanmitra-crop-agent --follow --region ap-south-1
```

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| AccessDenied | Check IAM permissions, re-run `aws configure` |
| Secret not found | Run: `aws secretsmanager create-secret --name kisaanmitra/crop-health-api --secret-string '{"CROP_HEALTH_API_KEY":"YOUR_KEY"}' --region ap-south-1` |
| Bucket not found | Run: `aws s3 mb s3://kisaanmitra-images --region ap-south-1` |
| Lambda timeout | Run: `aws lambda update-function-configuration --function-name kisaanmitra-crop-agent --timeout 60 --region ap-south-1` |
| Module not found | Re-run: `cd src/lambda && ./deploy_lambda.sh` |

## Success Criteria

✅ Lambda function deployed  
✅ Test image processed successfully  
✅ Disease detected with 99% confidence  
✅ Response in Hindi format  
✅ Logs visible in CloudWatch  
✅ Cost under $5/month for testing  

---

**Status**: [ ] Not Started | [ ] In Progress | [ ] Complete  
**Date**: ___________  
**Deployed By**: ___________
