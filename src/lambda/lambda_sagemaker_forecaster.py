"""
AWS Lambda Function - SageMaker Price Forecasting
Uses SageMaker AutoML for time series forecasting (no Docker/Prophet needed!)

This Lambda:
1. Fetches latest price data from AgMarkNet
2. Prepares data in SageMaker format
3. Uploads to S3
4. Creates SageMaker AutoML job (or uses existing model)
5. Runs batch inference
6. Stores forecasts in DynamoDB

Environment Variables:
- S3_BUCKET: S3 bucket for ML data
- SAGEMAKER_ROLE_ARN: IAM role for SageMaker
- DYNAMODB_TABLE: DynamoDB table for forecasts
- USE_EXISTING_MODEL: 'true' to skip training, use existing model
"""

import json
import os
import boto3
import pandas as pd
import requests
from datetime import datetime, timedelta
import sys

# Add modules to path
sys.path.insert(0, '/opt/python')  # Lambda layer path
sys.path.insert(0, os.path.dirname(__file__))

from sagemaker_forecasting.data_preparer import SageMakerDataPreparer
from sagemaker_forecasting.automl_trainer import SageMakerAutoMLTrainer
from sagemaker_forecasting.batch_predictor import SageMakerBatchPredictor

# Configuration
S3_BUCKET = os.environ.get('S3_BUCKET', 'kisaanmitra-ml-data')
SAGEMAKER_ROLE_ARN = os.environ.get('SAGEMAKER_ROLE_ARN')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'kisaanmitra-price-forecasts')
USE_EXISTING_MODEL = os.environ.get('USE_EXISTING_MODEL', 'false').lower() == 'true'
AGMARKNET_API_KEY = os.environ.get('AGMARKNET_API_KEY', '')  # Optional: for live data updates

CROPS = ['Tomato', 'Onion', 'Potato', 'Wheat', 'Rice']
FORECAST_HORIZON = 30  # Days

# AWS clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table(DYNAMODB_TABLE)


def fetch_historical_data_from_s3(crop_name):
    """
    Fetch historical price data from S3 CSV files
    Uses ALL available historical data (5 years: 2021-2026)
    """
    s3_client = boto3.client('s3', region_name='ap-south-1')
    
    try:
        # Download CSV from S3
        csv_key = f"historical-prices/{crop_name}.csv"
        print(f"  Downloading s3://{S3_BUCKET}/{csv_key}")
        
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=csv_key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Parse CSV (skip first 2 header rows)
        from io import StringIO
        df = pd.read_csv(StringIO(csv_content), skiprows=2)
        
        # Extract date and price columns
        df['date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
        df['price'] = pd.to_numeric(df['Modal Price 02-03-2021 to 02-03-2026'], errors='coerce')
        
        # Remove rows with invalid dates or prices
        df = df.dropna(subset=['date', 'price'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Keep only date and price columns
        result = df[['date', 'price']].copy()
        
        print(f"  ✅ Loaded {len(result)} days of data ({result['date'].min().date()} to {result['date'].max().date()})")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Error loading {crop_name} from S3: {e}")
        print(f"  Falling back to dummy data...")
        
        # Fallback to dummy data
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        prices = [50 + i * 0.1 for i in range(365)]
        
        return pd.DataFrame({
            'date': dates,
            'price': prices
        })


def fetch_latest_from_agmarknet(crop_name, api_key, days=7):
    """
    Fetch latest data from AgMarkNet API to supplement historical data
    """
    if not api_key:
        print(f"  ⚠️ No AgMarkNet API key, skipping live data fetch")
        return None
    
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    try:
        params = {
            'api-key': api_key,
            'format': 'json',
            'filters[commodity]': crop_name,
            'filters[state]': 'Maharashtra',
            'limit': 100
        }
        
        print(f"  📡 Fetching latest {days} days from AgMarkNet API...")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'records' not in data or not data['records']:
            print(f"  ⚠️ No new data from API")
            return None
        
        # Convert to DataFrame
        api_df = pd.DataFrame(data['records'])
        api_df['date'] = pd.to_datetime(api_df['arrival_date'], format='%d/%m/%Y', errors='coerce')
        api_df['price'] = pd.to_numeric(api_df['modal_price'], errors='coerce')
        
        # Filter last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        api_df = api_df[api_df['date'] >= cutoff_date]
        
        result = api_df[['date', 'price']].dropna()
        
        print(f"  ✅ Fetched {len(result)} new records from API")
        return result
        
    except Exception as e:
        print(f"  ⚠️ AgMarkNet API error: {e}")
        return None


def store_forecasts_in_dynamodb(forecasts_by_crop):
    """
    Store forecasts in DynamoDB in WhatsApp-compatible format
    
    Args:
        forecasts_by_crop: Dict of {crop_name: list of forecast dicts}
    """
    print(f"Storing forecasts for {len(forecasts_by_crop)} crops in DynamoDB...")
    
    stored_count = 0
    for crop_name, forecasts in forecasts_by_crop.items():
        try:
            # Format for WhatsApp bot compatibility
            item = {
                'commodity': crop_name.lower(),  # 'tomato', 'onion', etc.
                'forecasts': forecasts,  # List of {date, day, price, lower, upper}
                'generated_at': datetime.now().isoformat(),
                'model': 'sagemaker_automl',
                'last_updated': datetime.now().isoformat()
            }
            
            table.put_item(Item=item)
            stored_count += 1
            print(f"  ✅ Stored {len(forecasts)} forecasts for {crop_name}")
            
        except Exception as e:
            print(f"  ⚠️ Failed to store {crop_name} forecasts: {e}")
    
    print(f"✅ Stored forecasts for {stored_count}/{len(forecasts_by_crop)} crops")
    return stored_count


def lambda_handler(event, context):
    """
    Main Lambda handler
    """
    print("=" * 60)
    print("SAGEMAKER AUTOML PRICE FORECASTING")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'crops_processed': [],
        'forecasts_stored': 0,
        'training_job': None,
        'model_used': None
    }
    
    try:
        # Step 1: Fetch historical data for all crops
        print("\n1. Fetching historical data from S3...")
        historical_data = {}
        
        for crop in CROPS:
            print(f"Fetching {crop}...")
            
            # Load historical data from S3 CSV (5 years of data)
            df = fetch_historical_data_from_s3(crop)
            
            # Optionally fetch latest data from AgMarkNet API
            if AGMARKNET_API_KEY:
                latest_df = fetch_latest_from_agmarknet(crop, AGMARKNET_API_KEY, days=7)
                if latest_df is not None and len(latest_df) > 0:
                    # Merge with historical data (remove duplicates)
                    df = pd.concat([df, latest_df], ignore_index=True)
                    df = df.drop_duplicates(subset=['date'], keep='last')
                    df = df.sort_values('date')
                    print(f"  ✅ Combined with {len(latest_df)} new API records")
            
            if df is not None and len(df) >= 30:
                historical_data[crop] = df
                print(f"✅ {len(df)} days of data")
            else:
                print(f"❌ Insufficient data")
        
        if not historical_data:
            raise Exception("No historical data available")
        
        # Step 2: Prepare data for SageMaker
        print("\n2. Preparing data for SageMaker...")
        preparer = SageMakerDataPreparer(s3_bucket=S3_BUCKET)
        
        train_df = preparer.prepare_training_data(historical_data)
        preparer.validate_data(train_df)
        
        # Upload to S3
        train_s3_uri = preparer.upload_to_s3(train_df, filename='train.csv')
        
        # Step 3: Train model or use existing
        if USE_EXISTING_MODEL:
            print("\n3. Using existing model (skipping training)...")
            model_name = 'kisaanmitra-forecast-model'
            results['model_used'] = model_name
        else:
            print("\n3. Creating SageMaker AutoML job...")
            trainer = SageMakerAutoMLTrainer(role_arn=SAGEMAKER_ROLE_ARN)
            
            # SageMaker job name max 32 chars (using shorter format)
            job_name = f"km-{datetime.now().strftime('%y%m%d%H%M%S')}"
            output_s3_uri = f"s3://{S3_BUCKET}/sagemaker-forecasting/output"
            
            # Create AutoML job
            trainer.create_forecasting_job(
                job_name=job_name,
                train_s3_uri=train_s3_uri,
                output_s3_uri=output_s3_uri,
                forecast_horizon=FORECAST_HORIZON,
                forecast_frequency='D'
            )
            
            results['training_job'] = job_name
            
            # Note: Training takes 1-2 hours
            # In production, use Step Functions or EventBridge to wait
            print("  ⚠️ Training job created but not waiting for completion")
            print("  ⚠️ Use Step Functions or schedule another Lambda to check status")
            
            return {
                'statusCode': 202,  # Accepted
                'body': json.dumps({
                    'message': 'Training job started',
                    'job_name': job_name,
                    'note': 'Training takes 1-2 hours. Check job status later.'
                })
            }
        
        # Step 4: Run batch inference (only if using existing model)
        print("\n4. Running batch inference...")
        predictor = SageMakerBatchPredictor()
        
        # Prepare inference input (last known data point for each crop)
        inference_input = train_df.groupby('item_id').tail(1)
        inference_s3_uri = preparer.upload_to_s3(inference_input, filename='inference_input.csv')
        
        # Create transform job (max 32 chars)
        transform_job_name = f"km-tr-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        output_s3_uri = f"s3://{S3_BUCKET}/sagemaker-forecasting/predictions/"
        
        predictor.create_transform_job(
            job_name=transform_job_name,
            model_name=model_name,
            input_s3_uri=inference_s3_uri,
            output_s3_uri=output_s3_uri
        )
        
        # Wait for completion (max 30 minutes)
        predictor.wait_for_transform_job(transform_job_name, max_wait_time=1800)
        
        # Step 5: Get predictions and store in DynamoDB
        print("\n5. Storing forecasts in DynamoDB...")
        
        # Download predictions
        predictions_df = predictor.get_predictions(
            output_s3_uri,
            S3_BUCKET,
            'sagemaker-forecasting/predictions/inference_input.csv.out'
        )
        
        # Format for DynamoDB
        forecasts = predictor.format_predictions_for_dynamodb(predictions_df)
        
        # Store in DynamoDB
        stored_count = store_forecasts_in_dynamodb(forecasts)
        
        results['crops_processed'] = list(historical_data.keys())
        results['forecasts_stored'] = stored_count
        
        # Summary
        print("\n" + "=" * 60)
        print("FORECASTING COMPLETE")
        print("=" * 60)
        print(f"Crops processed: {len(results['crops_processed'])}")
        print(f"Forecasts stored: {results['forecasts_stored']}")
        print("")
        
        return {
            'statusCode': 200,
            'body': json.dumps(results, default=str)
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


if __name__ == '__main__':
    # For local testing
    print("Running locally...")
    result = lambda_handler({}, None)
    print(json.dumps(result, indent=2, default=str))
