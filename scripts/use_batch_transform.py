"""
Use SageMaker Batch Transform instead of Real-time Endpoint
This is more cost-effective and works better with AutoML models
"""

import boto3
import pandas as pd
import json
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO
import time

# Configuration
REGION = 'ap-south-1'
S3_BUCKET = 'kisaanmitra-ml-data'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
MODEL_NAME = 'km-260304185319-model'  # From successful training job

CROPS = {
    'onion': 'Onion',
    'rice': 'Rice',
    'sugarcane': 'Sugarcane',
    'tomato': 'Tomato',
    'wheat': 'Wheat'
}

# AWS clients
s3 = boto3.client('s3', region_name=REGION)
sagemaker = boto3.client('sagemaker', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)


def load_historical_data(crop_name):
    """Load historical data from S3"""
    csv_key = f"historical-prices/{crop_name}.csv"
    
    obj = s3.get_object(Bucket=S3_BUCKET, Key=csv_key)
    csv_content = obj['Body'].read().decode('utf-8')
    
    df = pd.read_csv(StringIO(csv_content), skiprows=1)
    df['date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    df['price'] = pd.to_numeric(df['Modal Price 02-03-2021 to 02-03-2026'], errors='coerce')
    df = df.dropna(subset=['date', 'price'])
    df = df.sort_values('date')
    
    return df[['date', 'price']]


def prepare_batch_input():
    """Prepare input file for batch transform"""
    print("📝 Preparing batch transform input...")
    
    all_data = []
    
    for crop_key, crop_name in CROPS.items():
        print(f"  Processing {crop_name}...")
        df = load_historical_data(crop_name)
        
        # Format for SageMaker: item_id, timestamp, price
        df_formatted = pd.DataFrame({
            'item_id': crop_key,
            'timestamp': df['date'],
            'price': df['price']
        })
        
        all_data.append(df_formatted)
        print(f"    ✅ {len(df)} records")
    
    # Combine all crops
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Upload to S3
    csv_buffer = StringIO()
    combined_df.to_csv(csv_buffer, index=False)
    
    input_key = 'batch-inference/input.csv'
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=input_key,
        Body=csv_buffer.getvalue()
    )
    
    input_uri = f"s3://{S3_BUCKET}/{input_key}"
    print(f"  ✅ Uploaded to {input_uri}")
    
    return input_uri


def create_batch_transform_job(input_uri):
    """Create batch transform job"""
    job_name = f"km-batch-{datetime.now().strftime('%y%m%d%H%M%S')}"
    output_uri = f"s3://{S3_BUCKET}/batch-inference/output/"
    
    print(f"\n🚀 Creating batch transform job: {job_name}")
    
    try:
        sagemaker.create_transform_job(
            TransformJobName=job_name,
            ModelName=MODEL_NAME,
            TransformInput={
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': input_uri
                    }
                },
                'ContentType': 'text/csv',
                'SplitType': 'Line'
            },
            TransformOutput={
                'S3OutputPath': output_uri,
                'Accept': 'text/csv',
                'AssembleWith': 'Line'
            },
            TransformResources={
                'InstanceType': 'ml.m5.xlarge',
                'InstanceCount': 1
            }
        )
        
        print(f"  ✅ Job created: {job_name}")
        return job_name, output_uri
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        raise


def wait_for_transform_job(job_name, max_wait=1800):
    """Wait for transform job to complete"""
    print(f"\n⏳ Waiting for job to complete (max {max_wait//60} minutes)...")
    
    start_time = time.time()
    
    while True:
        response = sagemaker.describe_transform_job(TransformJobName=job_name)
        status = response['TransformJobStatus']
        
        elapsed = int(time.time() - start_time)
        print(f"  Status: {status} ({elapsed}s elapsed)")
        
        if status == 'Completed':
            print(f"  ✅ Job completed in {elapsed}s")
            return True
        elif status == 'Failed':
            print(f"  ❌ Job failed: {response.get('FailureReason', 'Unknown')}")
            return False
        elif elapsed > max_wait:
            print(f"  ⏰ Timeout after {max_wait}s")
            return False
        
        time.sleep(30)


def download_and_parse_results(output_uri, job_name):
    """Download and parse batch transform results"""
    print(f"\n📥 Downloading results...")
    
    # Results are in output_uri/input.csv.out
    output_key = f"batch-inference/output/input.csv.out"
    
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=output_key)
        results_content = obj['Body'].read().decode('utf-8')
        
        # Parse results (format depends on model output)
        results_df = pd.read_csv(StringIO(results_content))
        
        print(f"  ✅ Downloaded {len(results_df)} predictions")
        return results_df
        
    except Exception as e:
        print(f"  ❌ Error downloading results: {e}")
        return None


def format_and_store_forecasts(results_df):
    """Format results and store in DynamoDB"""
    print(f"\n💾 Storing forecasts in DynamoDB...")
    
    table = dynamodb.Table(DYNAMODB_TABLE)
    stored = 0
    
    # Group by item_id (crop)
    for crop_key in CROPS.keys():
        crop_results = results_df[results_df['item_id'] == crop_key]
        
        if len(crop_results) == 0:
            print(f"  ⚠️ No results for {crop_key}")
            continue
        
        # Generate 30-day forecasts
        forecasts = []
        start_date = datetime.now() + timedelta(days=1)
        
        for i in range(min(30, len(crop_results))):
            forecast_date = start_date + timedelta(days=i)
            row = crop_results.iloc[i]
            
            # Extract price (column name depends on model output)
            price = float(row.get('mean', row.get('prediction', row.get('price', 1000))))
            
            forecasts.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'day': forecast_date.strftime('%A'),
                'price': Decimal(str(round(price, 2))),
                'lower': Decimal(str(round(price * 0.9, 2))),
                'upper': Decimal(str(round(price * 1.1, 2)))
            })
        
        # Store in DynamoDB
        item = {
            'commodity': crop_key,
            'forecasts': forecasts,
            'model': 'SageMaker AutoML Batch',
            'model_version': 'sagemaker_batch_v1',
            'last_updated': datetime.now().isoformat(),
            'data_source': 'SageMaker Batch Transform'
        }
        
        table.put_item(Item=item)
        stored += 1
        print(f"  ✅ {crop_key}: {len(forecasts)} days, tomorrow ₹{forecasts[0]['price']}")
    
    return stored


def main():
    print("="*60)
    print("🔮 SageMaker Batch Transform Forecasting")
    print("="*60)
    
    try:
        # Step 1: Prepare input
        input_uri = prepare_batch_input()
        
        # Step 2: Create batch transform job
        job_name, output_uri = create_batch_transform_job(input_uri)
        
        # Step 3: Wait for completion
        success = wait_for_transform_job(job_name, max_wait=1800)
        
        if not success:
            print("\n❌ Batch transform job failed or timed out")
            return 1
        
        # Step 4: Download and parse results
        results_df = download_and_parse_results(output_uri, job_name)
        
        if results_df is None:
            print("\n❌ Failed to download results")
            return 1
        
        # Step 5: Store in DynamoDB
        stored = format_and_store_forecasts(results_df)
        
        print("\n" + "="*60)
        print(f"✅ Complete: Stored forecasts for {stored}/{len(CROPS)} crops")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
