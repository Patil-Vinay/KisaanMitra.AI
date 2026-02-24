# AWS Lambda Integration Guide for KisaanMitra.AI Crop Agent

## Overview

This guide explains how to deploy the Crop Health API as an AWS Lambda function for serverless, scalable disease detection.

## Architecture

```
WhatsApp → API Gateway → Lambda (Crop Agent) → Crop Health API
                              ↓
                         S3 (Images)
                              ↓
                    Secrets Manager (API Key)
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.11** installed locally
4. **Crop Health API Key** from Kindwise

## Files Created

- `lambda_crop_agent.py` - Main Lambda handler
- `lambda_requirements.txt` - Python dependencies
- `deploy_lambda.sh` - Automated deployment script
- `test_event.json` - Sample test event
- `LAMBDA_SETUP.md` - This guide

## Step-by-Step Deployment

### 1. Store API Key in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
    --name kisaanmitra/crop-health-api \
    --secret-string '{"CROP_HEALTH_API_KEY":"your_api_key_here"}' \
    --region ap-south-1
```

### 2. Create S3 Bucket for Images

```bash
aws s3 mb s3://kisaanmitra-images --region ap-south-1

# Enable versioning (optional)
aws s3api put-bucket-versioning \
    --bucket kisaanmitra-images \
    --versioning-configuration Status=Enabled
```

### 3. Deploy Lambda Function

Make the deployment script executable:
```bash
chmod +x deploy_lambda.sh
```

Run deployment:
```bash
./deploy_lambda.sh
```

This script will:
- Create deployment package with dependencies
- Create IAM role with necessary permissions
- Deploy Lambda function
- Configure environment variables

### 4. Test Lambda Function

Upload a test image to S3:
```bash
aws s3 cp 2.jpg s3://kisaanmitra-images/test/crop_image.jpg
```

Update `test_event.json` with your S3 path:
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

Invoke Lambda:
```bash
aws lambda invoke \
    --function-name kisaanmitra-crop-agent \
    --payload file://test_event.json \
    --region ap-south-1 \
    response.json

# View response
cat response.json | jq .
```

### 5. Create API Gateway (Optional)

For HTTP endpoint access:

```bash
# Create REST API
aws apigateway create-rest-api \
    --name "KisaanMitra Crop Agent API" \
    --region ap-south-1

# Get API ID
API_ID=$(aws apigateway get-rest-apis \
    --query "items[?name=='KisaanMitra Crop Agent API'].id" \
    --output text \
    --region ap-south-1)

# Create resource and method (POST)
# ... (detailed steps in AWS Console or CLI)
```

Or use AWS Console:
1. Go to API Gateway
2. Create REST API
3. Create resource `/detect-disease`
4. Create POST method
5. Integrate with Lambda function
6. Deploy to stage (e.g., `prod`)

## Lambda Function Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET` | S3 bucket for images | `kisaanmitra-images` |
| `SECRET_NAME` | Secrets Manager secret name | `kisaanmitra/crop-health-api` |
| `AWS_REGION` | AWS region | `ap-south-1` |

### IAM Permissions Required

- `AWSLambdaBasicExecutionRole` - CloudWatch Logs
- `AmazonS3ReadOnlyAccess` - Read images from S3
- `SecretsManagerReadWrite` - Read API key

### Resource Limits

- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Concurrent Executions**: 1000 (default)

## Event Format

### Input Event

```json
{
  "image_source": "s3",
  "s3_bucket": "kisaanmitra-images",
  "s3_key": "uploads/farmer123/image.jpg",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "language": "hi"
}
```

**Alternative with Base64**:
```json
{
  "image_source": "base64",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "language": "hi"
}
```

### Output Response

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
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

## Integration with WhatsApp

### Flow

1. Farmer sends image via WhatsApp
2. WhatsApp webhook receives message
3. Download image, upload to S3
4. Invoke Lambda with S3 path
5. Lambda calls Crop Health API
6. Format response in Hindi
7. Send response back to farmer

### Sample Integration Code

```python
# In your WhatsApp webhook handler
import boto3

lambda_client = boto3.client('lambda', region_name='ap-south-1')

def handle_image_message(phone_number, image_url, latitude, longitude):
    # Download image from WhatsApp
    image_data = download_whatsapp_image(image_url)
    
    # Upload to S3
    s3_key = f"uploads/{phone_number}/{timestamp}.jpg"
    upload_to_s3(image_data, s3_key)
    
    # Invoke Lambda
    event = {
        "image_source": "s3",
        "s3_bucket": "kisaanmitra-images",
        "s3_key": s3_key,
        "latitude": latitude,
        "longitude": longitude,
        "language": "hi"
    }
    
    response = lambda_client.invoke(
        FunctionName='kisaanmitra-crop-agent',
        InvocationType='RequestResponse',
        Payload=json.dumps(event)
    )
    
    result = json.loads(response['Payload'].read())
    body = json.loads(result['body'])
    
    # Send response to farmer
    send_whatsapp_message(phone_number, body['message'])
```

## Monitoring & Logging

### CloudWatch Logs

View logs:
```bash
aws logs tail /aws/lambda/kisaanmitra-crop-agent --follow --region ap-south-1
```

### Metrics

- Invocations
- Duration
- Errors
- Throttles
- Concurrent Executions

### Alarms

Create CloudWatch alarm for errors:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name kisaanmitra-crop-agent-errors \
    --alarm-description "Alert on Lambda errors" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value=kisaanmitra-crop-agent \
    --evaluation-periods 1 \
    --region ap-south-1
```

## Cost Estimation

### Lambda Costs (ap-south-1)

- **Requests**: $0.20 per 1M requests
- **Duration**: $0.0000166667 per GB-second

**Example** (100K requests/month, 512MB, 5s avg):
- Requests: 100,000 × $0.20/1M = $0.02
- Duration: 100,000 × 5s × 0.5GB × $0.0000166667 = $4.17
- **Total**: ~$4.19/month

### Additional Costs

- **S3**: $0.023/GB storage + $0.09/GB transfer
- **Secrets Manager**: $0.40/secret/month
- **API Gateway**: $3.50 per million requests

## Troubleshooting

### Common Issues

**1. "API key not found"**
- Check Secrets Manager secret exists
- Verify IAM role has SecretsManagerReadWrite permission

**2. "Image not found in S3"**
- Verify S3 bucket and key are correct
- Check IAM role has S3 read permission

**3. "Timeout"**
- Increase Lambda timeout (max 15 minutes)
- Check Crop Health API response time

**4. "Memory exceeded"**
- Increase Lambda memory (512MB → 1024MB)

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Best Practices

1. ✅ Store API keys in Secrets Manager (not environment variables)
2. ✅ Use IAM roles with least privilege
3. ✅ Enable VPC for Lambda (optional, for private resources)
4. ✅ Encrypt S3 bucket with KMS
5. ✅ Enable CloudTrail for audit logging
6. ✅ Use API Gateway with API keys/OAuth
7. ✅ Implement rate limiting

## Scaling Considerations

### Current Setup
- **Concurrent Executions**: 1000 (default)
- **Burst**: 3000 requests/second

### For High Scale (1M+ users)
1. **Reserved Concurrency**: Allocate dedicated capacity
2. **Provisioned Concurrency**: Pre-warm instances
3. **SQS Queue**: Decouple processing
4. **Lambda Layers**: Share dependencies
5. **Multi-Region**: Deploy to multiple regions

## Next Steps

1. ✅ Deploy Lambda function
2. ✅ Test with sample images
3. ⬜ Integrate with WhatsApp webhook
4. ⬜ Add treatment recommendations database
5. ⬜ Implement caching (DynamoDB)
6. ⬜ Add monitoring dashboards
7. ⬜ Set up CI/CD pipeline

## Support

For issues or questions:
- Check CloudWatch Logs
- Review AWS Lambda documentation
- Contact team: KisaanMitra.AI

---

**Status**: Production-Ready ✅  
**Last Updated**: 2024-01-15
