"""
Generate Forecasts from SageMaker Model using Batch Transform
This is the CORRECT way to generate forecasts from SageMaker AutoML
"""

import boto3
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO

# Configuration
REGION = 'ap-south-1'
AUTOML_JOB_NAME = 'km-260304185319'
S3_BUCKET = 'kisaanmitra-ml-data'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
CROPS = ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']

# AWS clients
sagemaker = boto3.client('sagemaker', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)


def create_batch_transform_job():
    """
    Create batch transform job to generate forecasts
    This uses the trained SageMaker model
    """
    print("\n" + "="*60)
    print("🔮 Generating Forecasts from SageMaker Model")
    print("="*60)
    
    # Get model name from AutoML job
    print(f"\n📊 Getting model from AutoML job: {AUTOML_JOB_NAME}")
    response = sagemaker.describe_auto_ml_job_v2(AutoMLJobName=AUTOML_JOB_NAME)
    
    if response['AutoMLJobStatus'] != 'Completed':
        print(f"❌ AutoML job not completed: {response['AutoMLJobStatus']}")
        return False
    
    best_candidate = response['BestCandidate']
    model_name = f"{AUTOML_JOB_NAME}-model"
    
    print(f"✅ Model: {model_name}")
    print(f"   Candidate: {best_candidate['CandidateName']}")
    
    # Prepare input data for batch transform
    # For time series, we need to provide the historical data
    print(f"\n📝 Preparing input data for forecasting...")
    
    input_data = []
    for crop in CROPS:
        # Load historical data from S3
        try:
            csv_key = f"historical-prices/{crop.title()}.csv"
            print(f"  Loading {csv_key}...")
            
            obj = s3.get_object(Bucket=S3_BUCKET, Key=csv_key)
            csv_content = obj['Body'].read().decode('utf-8')
            
            # Parse CSV
            df = pd.read_csv(StringIO(csv_content), skiprows=2)
            df['date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
            df['price'] = pd.to_numeric(df['Modal Price 02-03-2021 to 02-03-2026'], errors='coerce')
            df = df.dropna(subset=['date', 'price'])
            df = df.sort_values('date')
            
            # Create input record for this crop
            record = {
                "item_id": crop,
                "timestamp": df['date'].dt.strftime('%Y-%m-%d').tolist(),
                "target": df['price'].tolist()
            }
            
            input_data.append(record)
            print(f"  ✅ {crop}: {len(df)} days of data")
            
        except Exception as e:
            print(f"  ❌ Error loading {crop}: {e}")
            continue
    
    if not input_data:
        print("❌ No input data prepared")
        return False
    
    # Upload input data to S3
    input_key = f"sagemaker-forecasting/batch-input-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
    print(f"\n📤 Uploading input data to S3: {input_key}")
    
    # Write as JSONL (one JSON object per line)
    jsonl_content = '\n'.join([json.dumps(record) for record in input_data])
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=input_key,
        Body=jsonl_content.encode('utf-8')
    )
    
    print(f"✅ Input data uploaded")
    
    # Create batch transform job
    transform_job_name = f"km-forecast-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    output_path = f"s3://{S3_BUCKET}/sagemaker-forecasting/batch-output/"
    
    print(f"\n🚀 Creating batch transform job: {transform_job_name}")
    print(f"   Input: s3://{S3_BUCKET}/{input_key}")
    print(f"   Output: {output_path}")
    
    try:
        sagemaker.create_transform_job(
            TransformJobName=transform_job_name,
            ModelName=model_name,
            TransformInput={
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': f"s3://{S3_BUCKET}/{input_key}"
                    }
                },
                'ContentType': 'application/jsonlines',
                'SplitType': 'Line'
            },
            TransformOutput={
                'S3OutputPath': output_path,
                'AssembleWith': 'Line'
            },
            TransformResources={
                'InstanceType': 'ml.m5.xlarge',
                'InstanceCount': 1
            }
        )
        
        print(f"✅ Batch transform job created")
        print(f"⏳ Waiting for job to complete (this may take 10-15 minutes)...")
        
        # Wait for completion
        while True:
            response = sagemaker.describe_transform_job(TransformJobName=transform_job_name)
            status = response['TransformJobStatus']
            
            print(f"   Status: {status}")
            
            if status == 'Completed':
                print(f"✅ Batch transform completed!")
                return transform_job_name, output_path
            
            elif status == 'Failed':
                failure_reason = response.get('FailureReason', 'Unknown')
                print(f"❌ Batch transform failed: {failure_reason}")
                return False
            
            time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error creating batch transform job: {e}")
        import traceback
        traceback.print_exc()
        return False


def parse_forecasts_and_store(output_path):
    """
    Parse forecast output and store in DynamoDB
    """
    print(f"\n📥 Parsing forecast results from {output_path}")
    
    # List output files
    prefix = output_path.replace(f"s3://{S3_BUCKET}/", "")
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    
    if 'Contents' not in response:
        print(f"❌ No output files found")
        return False
    
    print(f"✅ Found {len(response['Contents'])} output files")
    
    # Download and parse each output file
    for obj in response['Contents']:
        key = obj['Key']
        if not key.endswith('.out'):
            continue
        
        print(f"\n📄 Processing {key}")
        
        try:
            obj_data = s3.get_object(Bucket=S3_BUCKET, Key=key)
            content = obj_data['Body'].read().decode('utf-8')
            
            # Parse JSONL output
            for line in content.strip().split('\n'):
                if not line:
                    continue
                
                forecast_data = json.loads(line)
                
                # Extract crop name and forecasts
                crop = forecast_data.get('item_id', 'unknown')
                predictions = forecast_data.get('predictions', [])
                
                if not predictions:
                    print(f"  ⚠️  No predictions for {crop}")
                    continue
                
                # Format forecasts for DynamoDB
                forecasts = []
                start_date = datetime.now() + timedelta(days=1)
                
                for i, pred in enumerate(predictions[:30]):  # 30 days
                    forecast_date = start_date + timedelta(days=i)
                    
                    # Extract quantiles
                    if isinstance(pred, dict):
                        price = pred.get('mean', pred.get('0.5', pred.get('p50', 0)))
                        lower = pred.get('0.1', pred.get('p10', price * 0.9))
                        upper = pred.get('0.9', pred.get('p90', price * 1.1))
                    else:
                        price = float(pred)
                        lower = price * 0.9
                        upper = price * 1.1
                    
                    forecasts.append({
                        'date': forecast_date.strftime('%Y-%m-%d'),
                        'day': forecast_date.strftime('%A'),
                        'price': Decimal(str(round(price, 2))),
                        'lower': Decimal(str(round(lower, 2))),
                        'upper': Decimal(str(round(upper, 2)))
                    })
                
                # Store in DynamoDB
                table = dynamodb.Table(DYNAMODB_TABLE)
                
                item = {
                    'commodity': crop.lower(),
                    'forecasts': forecasts,
                    'model': 'SageMaker AutoML',  # ← NEW MODEL
                    'model_version': 'sagemaker_automl_v1',
                    'model_job': AUTOML_JOB_NAME,
                    'last_updated': datetime.now().isoformat(),
                    'training_records': len(predictions)
                }
                
                table.put_item(Item=item)
                
                print(f"  ✅ {crop.upper()}: Stored {len(forecasts)} days")
                print(f"     First: {forecasts[0]['date']} - ₹{forecasts[0]['price']}")
                print(f"     Last: {forecasts[-1]['date']} - ₹{forecasts[-1]['price']}")
        
        except Exception as e:
            print(f"  ❌ Error processing {key}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    return True


def main():
    """Main execution"""
    print("="*60)
    print("🚀 SageMaker Forecast Generation")
    print("="*60)
    print(f"\nThis will:")
    print(f"1. Use trained SageMaker model: {AUTOML_JOB_NAME}")
    print(f"2. Generate 30-day forecasts for {len(CROPS)} crops")
    print(f"3. Store in DynamoDB: {DYNAMODB_TABLE}")
    print(f"4. Replace OLD Prophet forecasts with NEW SageMaker forecasts")
    
    input("\nPress Enter to continue...")
    
    # Create batch transform job
    result = create_batch_transform_job()
    
    if not result:
        print("\n❌ Failed to create batch transform job")
        return 1
    
    transform_job_name, output_path = result
    
    # Parse and store forecasts
    success = parse_forecasts_and_store(output_path)
    
    if success:
        print("\n" + "="*60)
        print("✅ Forecast Generation Complete!")
        print("="*60)
        print(f"\nDynamoDB table updated: {DYNAMODB_TABLE}")
        print(f"Forecasts now use: SageMaker AutoML (NOT Prophet)")
        print(f"\nTest via WhatsApp: 'टमाटर का भाव कल क्या होगा?'")
    else:
        print("\n❌ Failed to parse and store forecasts")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
