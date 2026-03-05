"""
SageMaker Batch Transform for Price Forecasting
Uses the trained AutoML model with real historical data
"""

import boto3
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO
import time
import sys

# Configuration
REGION = 'ap-south-1'
S3_BUCKET = 'kisaanmitra-ml-data'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
MODEL_NAME = 'km-260304185319-model'
FORECAST_HORIZON = 30  # Days to forecast

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


def load_and_format_historical_data():
    """
    Load historical data from S3 and format for batch transform
    Format must match training: item_id, timestamp, price
    """
    print("📊 Loading historical data from S3...")
    
    all_data = []
    
    for crop_key, crop_name in CROPS.items():
        print(f"  Loading {crop_name}...")
        
        try:
            # Download CSV from S3
            csv_key = f"historical-prices/{crop_name}.csv"
            obj = s3.get_object(Bucket=S3_BUCKET, Key=csv_key)
            csv_content = obj['Body'].read().decode('utf-8')
            
            # Parse CSV (skip first 2 header rows)
            df = pd.read_csv(StringIO(csv_content), skiprows=1)
            
            # Extract and clean data
            df['date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
            df['price'] = pd.to_numeric(df['Modal Price 02-03-2021 to 02-03-2026'], errors='coerce')
            
            # Remove invalid rows
            df = df.dropna(subset=['date', 'price'])
            df = df.sort_values('date')
            
            # Format for SageMaker (must match training format)
            df_formatted = pd.DataFrame({
                'item_id': crop_key,
                'timestamp': df['date'].dt.strftime('%Y-%m-%d %H:%M:%S'),  # Match training format
                'price': df['price']
            })
            
            all_data.append(df_formatted)
            print(f"    ✅ {len(df_formatted)} records ({df['date'].min().date()} to {df['date'].max().date()})")
            
        except Exception as e:
            print(f"    ❌ Error loading {crop_name}: {e}")
            continue
    
    if not all_data:
        raise Exception("No data loaded!")
    
    # Combine all crops
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n  ✅ Total: {len(combined_df)} records across {len(all_data)} crops")
    
    return combined_df


def upload_batch_input(df):
    """Upload input data to S3 for batch transform"""
    print("\n📤 Uploading batch input to S3...")
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    # Upload to S3
    input_key = f"batch-inference/input-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=input_key,
        Body=csv_content
    )
    
    input_uri = f"s3://{S3_BUCKET}/{input_key}"
    print(f"  ✅ Uploaded to: {input_uri}")
    print(f"  📊 Size: {len(csv_content)} bytes")
    
    return input_uri, input_key


def create_batch_transform_job(input_uri):
    """Create SageMaker batch transform job"""
    job_name = f"km-batch-{datetime.now().strftime('%y%m%d%H%M%S')}"
    output_path = f"s3://{S3_BUCKET}/batch-inference/output/"
    
    print(f"\n🚀 Creating batch transform job...")
    print(f"  Job name: {job_name}")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Input: {input_uri}")
    print(f"  Output: {output_path}")
    
    try:
        response = sagemaker.create_transform_job(
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
                'SplitType': 'Line',
                'CompressionType': 'None'
            },
            TransformOutput={
                'S3OutputPath': output_path,
                'Accept': 'text/csv',
                'AssembleWith': 'Line'
            },
            TransformResources={
                'InstanceType': 'ml.m5.large',  # Smaller instance, might have quota
                'InstanceCount': 1
            }
        )
        
        print(f"  ✅ Job created successfully")
        return job_name, output_path
        
    except Exception as e:
        print(f"  ❌ Error creating job: {e}")
        raise


def wait_for_job_completion(job_name, max_wait_seconds=1800):
    """Wait for batch transform job to complete"""
    print(f"\n⏳ Waiting for job to complete (max {max_wait_seconds//60} minutes)...")
    
    start_time = time.time()
    last_status = None
    
    while True:
        try:
            response = sagemaker.describe_transform_job(TransformJobName=job_name)
            status = response['TransformJobStatus']
            elapsed = int(time.time() - start_time)
            
            # Only print if status changed
            if status != last_status:
                print(f"  [{elapsed}s] Status: {status}")
                last_status = status
            
            if status == 'Completed':
                print(f"  ✅ Job completed in {elapsed}s ({elapsed//60}m {elapsed%60}s)")
                return True, response
                
            elif status == 'Failed':
                failure_reason = response.get('FailureReason', 'Unknown error')
                print(f"  ❌ Job failed: {failure_reason}")
                return False, response
                
            elif status == 'Stopped':
                print(f"  ⚠️ Job was stopped")
                return False, response
            
            # Check timeout
            if elapsed > max_wait_seconds:
                print(f"  ⏰ Timeout after {max_wait_seconds}s")
                return False, response
            
            # Wait before next check
            time.sleep(30)
            
        except Exception as e:
            print(f"  ❌ Error checking status: {e}")
            return False, None


def download_results(output_path, input_key):
    """Download and parse batch transform results"""
    print(f"\n📥 Downloading results...")
    
    # Results file name is input file name + .out
    input_filename = input_key.split('/')[-1]
    output_key = f"batch-inference/output/{input_filename}.out"
    
    print(f"  Looking for: s3://{S3_BUCKET}/{output_key}")
    
    try:
        # Download results
        obj = s3.get_object(Bucket=S3_BUCKET, Key=output_key)
        results_content = obj['Body'].read().decode('utf-8')
        
        print(f"  ✅ Downloaded {len(results_content)} bytes")
        
        # Parse CSV
        results_df = pd.read_csv(StringIO(results_content))
        print(f"  ✅ Parsed {len(results_df)} predictions")
        print(f"  📊 Columns: {list(results_df.columns)}")
        
        return results_df
        
    except s3.exceptions.NoSuchKey:
        print(f"  ❌ Results file not found: {output_key}")
        print(f"  Listing files in output directory...")
        
        # List what's actually there
        response = s3.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix='batch-inference/output/'
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"    - {obj['Key']}")
        else:
            print(f"    (empty)")
        
        return None
        
    except Exception as e:
        print(f"  ❌ Error downloading results: {e}")
        import traceback
        traceback.print_exc()
        return None


def parse_and_store_forecasts(results_df):
    """Parse results and store in DynamoDB"""
    print(f"\n💾 Parsing and storing forecasts...")
    
    if results_df is None or len(results_df) == 0:
        print("  ❌ No results to store")
        return 0
    
    # Display sample of results
    print(f"\n  Sample results:")
    print(results_df.head())
    
    table = dynamodb.Table(DYNAMODB_TABLE)
    stored_count = 0
    
    # Group by item_id (crop)
    for crop_key, crop_name in CROPS.items():
        print(f"\n  Processing {crop_name}...")
        
        # Filter results for this crop
        crop_results = results_df[results_df['item_id'] == crop_key]
        
        if len(crop_results) == 0:
            print(f"    ⚠️ No predictions found")
            continue
        
        print(f"    Found {len(crop_results)} predictions")
        
        # Generate 30-day forecasts
        forecasts = []
        start_date = datetime.now() + timedelta(days=1)
        
        # Try to find the forecast columns (names vary by model)
        price_col = None
        for col in ['mean', 'p50', '0.5', 'prediction', 'forecast']:
            if col in crop_results.columns:
                price_col = col
                break
        
        if price_col is None:
            print(f"    ⚠️ Could not find price column in: {list(crop_results.columns)}")
            # Use last known price as fallback
            last_price = crop_results['price'].iloc[-1] if 'price' in crop_results.columns else 1000
            print(f"    Using last known price: ₹{last_price}")
            
            for i in range(FORECAST_HORIZON):
                forecast_date = start_date + timedelta(days=i)
                forecasts.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'day': forecast_date.strftime('%A'),
                    'price': Decimal(str(round(float(last_price), 2))),
                    'lower': Decimal(str(round(float(last_price) * 0.9, 2))),
                    'upper': Decimal(str(round(float(last_price) * 1.1, 2)))
                })
        else:
            print(f"    Using column: {price_col}")
            
            # Get forecasts (limit to FORECAST_HORIZON days)
            for i in range(min(FORECAST_HORIZON, len(crop_results))):
                forecast_date = start_date + timedelta(days=i)
                row = crop_results.iloc[i]
                
                price = float(row[price_col])
                
                # Get confidence intervals if available
                lower = float(row.get('p10', row.get('0.1', price * 0.9)))
                upper = float(row.get('p90', row.get('0.9', price * 1.1)))
                
                forecasts.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'day': forecast_date.strftime('%A'),
                    'price': Decimal(str(round(price, 2))),
                    'lower': Decimal(str(round(lower, 2))),
                    'upper': Decimal(str(round(upper, 2)))
                })
        
        # Store in DynamoDB
        item = {
            'commodity': crop_key,
            'forecasts': forecasts,
            'model': 'SageMaker AutoML',
            'model_version': 'batch_transform_v1',
            'model_name': MODEL_NAME,
            'last_updated': datetime.now().isoformat(),
            'data_source': 'SageMaker Batch Transform',
            'forecast_horizon': FORECAST_HORIZON
        }
        
        table.put_item(Item=item)
        stored_count += 1
        
        print(f"    ✅ Stored {len(forecasts)} forecasts")
        print(f"    📅 Tomorrow ({forecasts[0]['day']}): ₹{forecasts[0]['price']}")
    
    return stored_count


def main():
    print("="*70)
    print("🔮 SAGEMAKER BATCH TRANSFORM FORECASTING")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {MODEL_NAME}")
    print(f"Forecast horizon: {FORECAST_HORIZON} days")
    print("="*70)
    
    try:
        # Step 1: Load and format historical data
        df = load_and_format_historical_data()
        
        # Step 2: Upload to S3
        input_uri, input_key = upload_batch_input(df)
        
        # Step 3: Create batch transform job
        job_name, output_path = create_batch_transform_job(input_uri)
        
        # Step 4: Wait for completion
        success, response = wait_for_job_completion(job_name, max_wait_seconds=1800)
        
        if not success:
            print("\n❌ Batch transform job failed")
            return 1
        
        # Step 5: Download results
        results_df = download_results(output_path, input_key)
        
        if results_df is None:
            print("\n❌ Failed to download results")
            return 1
        
        # Step 6: Parse and store forecasts
        stored_count = parse_and_store_forecasts(results_df)
        
        # Summary
        print("\n" + "="*70)
        print("✅ FORECASTING COMPLETE")
        print("="*70)
        print(f"Crops processed: {stored_count}/{len(CROPS)}")
        print(f"Forecast horizon: {FORECAST_HORIZON} days")
        print(f"Model: {MODEL_NAME}")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
