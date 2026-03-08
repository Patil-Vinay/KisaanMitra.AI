#!/bin/bash

# Request AWS SageMaker Batch Transform Quota Increase
# This will allow you to use the trained SageMaker model

echo "=========================================="
echo "AWS SageMaker Quota Increase Request"
echo "=========================================="
echo ""
echo "Requesting quota increase for:"
echo "  Service: SageMaker"
echo "  Resource: ml.m5.large for transform job usage"
echo "  Current: 0 instances"
echo "  Requested: 1 instance"
echo "  Region: ap-south-1"
echo ""

# Request quota increase
aws service-quotas request-service-quota-increase \
  --service-code sagemaker \
  --quota-code L-236AE59F \
  --desired-value 1 \
  --region ap-south-1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Quota increase request submitted successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Wait 1-3 business days for AWS approval"
    echo "2. You'll receive email notification"
    echo "3. After approval, run: python scripts/sagemaker_batch_forecast.py"
    echo ""
    echo "Check request status:"
    echo "  aws service-quotas list-requested-service-quota-change-history-by-quota \\"
    echo "    --service-code sagemaker \\"
    echo "    --quota-code L-236AE59F \\"
    echo "    --region ap-south-1"
else
    echo ""
    echo "❌ Failed to submit quota increase request"
    echo ""
    echo "Alternative: Use AWS Console"
    echo "1. Go to: https://console.aws.amazon.com/servicequotas/"
    echo "2. Region: ap-south-1"
    echo "3. Search: SageMaker"
    echo "4. Find: ml.m5.large for transform job usage"
    echo "5. Click: Request quota increase"
    echo "6. New value: 1"
fi

echo ""
echo "=========================================="
echo "Meanwhile, your Statistical forecasting"
echo "is working perfectly! Test it:"
echo "  WhatsApp: 'टमाटर का भाव कल क्या होगा?'"
echo "=========================================="
