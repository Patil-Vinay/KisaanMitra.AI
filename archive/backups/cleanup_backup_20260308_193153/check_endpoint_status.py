"""
Check SageMaker Endpoint Status
Quick script to check if endpoint is ready
"""

import boto3
import sys

REGION = 'ap-south-1'
ENDPOINT_NAME = 'kisaanmitra-forecast-endpoint'

sagemaker = boto3.client('sagemaker', region_name=REGION)

try:
    response = sagemaker.describe_endpoint(EndpointName=ENDPOINT_NAME)
    
    status = response['EndpointStatus']
    
    print(f"Endpoint: {ENDPOINT_NAME}")
    print(f"Status: {status}")
    
    if status == 'InService':
        print("✅ Endpoint is ready!")
        sys.exit(0)
    elif status == 'Creating':
        print("⏳ Endpoint is still being created...")
        print("   This usually takes 5-10 minutes")
        sys.exit(1)
    elif status == 'Failed':
        print("❌ Endpoint creation failed!")
        print(f"   Reason: {response.get('FailureReason', 'Unknown')}")
        sys.exit(2)
    else:
        print(f"⚠️  Endpoint status: {status}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(2)
