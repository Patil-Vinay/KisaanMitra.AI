"""
Generate forecasts from existing SageMaker endpoint
"""

import boto3
import pandas as pd
import json
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO

# Configuration
REGION = 'ap-south-1'
ENDPOINT_NAME = 'kisaanmitra-forecast-endpoint'
S3_BUCKET = 'kisaanmitra-ml-data'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
AUTOML_JOB_NAME = 'km-260304185319'

CROPS = {
    'onion': 'Onion',
    'rice': 'Rice',
    'sugarcane': 'Sugarcane',
    'tomato': 'Tomato',
    'wheat': 'Wheat'
}

# AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)
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


def generate_forecast_for_crop(crop_key, crop_name):
    """Generate forecast using SageMaker endpoint"""
    print(f"\n🔮 {crop_name}...")
    
    try:
        # Load historical data
        df = load_historical_data(crop_name)
        print(f"  ✅ Loaded {len(df)} days")
        
        # Prepare input
        inference_data = {
            "instances": [
                {
                    "start": df['date'].min().strftime('%Y-%m-%d'),
                    "target": df['price'].tolist(),
                    "item_id": crop_key
                }
            ],
            "configuration": {
                "num_samples": 100,
                "output_types": ["mean", "quantiles"],
                "quantiles": ["0.1", "0.5", "0.9"]
            }
        }
        
        print(f"  📤 Invoking endpoint...")
        
        # Invoke endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/json',
            Body=json.dumps(inference_data)
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        print(f"  ✅ Got response")
        
        # Extract forecasts
        forecasts = []
        start_date = datetime.now() + timedelta(days=1)
        
        # Parse predictions
        if 'predictions' in result:
            predictions = result['predictions'][0] if isinstance(result['predictions'], list) else result['predictions']
        elif 'forecasts' in result:
            predictions = result['forecasts']
        else:
            predictions = result
        
        # Get values
        if isinstance(predictions, dict):
            mean_values = predictions.get('mean', predictions.get('0.5', []))
            quantile_10 = predictions.get('0.1', [])
            quantile_90 = predictions.get('0.9', [])
        else:
            mean_values = predictions
            quantile_10 = []
            quantile_90 = []
        
        # Generate 30-day forecasts
        for i in range(min(30, len(mean_values) if isinstance(mean_values, list) else 30)):
            forecast_date = start_date + timedelta(days=i)
            
            if isinstance(mean_values, list) and i < len(mean_values):
                price = float(mean_values[i])
                lower = float(quantile_10[i]) if i < len(quantile_10) else price * 0.9
                upper = float(quantile_90[i]) if i < len(quantile_90) else price * 1.1
            else:
                price = float(mean_values) if not isinstance(mean_values, list) else 1000.0
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
            'commodity': crop_key,
            'forecasts': forecasts,
            'model': 'SageMaker AutoML',
            'model_version': 'sagemaker_automl_v1',
            'model_job': AUTOML_JOB_NAME,
            'last_updated': datetime.now().isoformat(),
            'training_records': len(df),
            'data_source': 'SageMaker Real-time Endpoint'
        }
        
        table.put_item(Item=item)
        
        print(f"  ✅ Stored {len(forecasts)} days")
        print(f"     Tomorrow: ₹{forecasts[0]['price']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("🔮 Generating Forecasts from SageMaker Endpoint")
    print("="*60)
    
    success = 0
    failed = []
    
    for crop_key, crop_name in CROPS.items():
        if generate_forecast_for_crop(crop_key, crop_name):
            success += 1
        else:
            failed.append(crop_name)
    
    print("\n" + "="*60)
    print(f"✅ Complete: {success}/{len(CROPS)}")
    if failed:
        print(f"❌ Failed: {', '.join(failed)}")
    print("="*60)
    
    return 0 if success == len(CROPS) else 1


if __name__ == '__main__':
    exit(main())
