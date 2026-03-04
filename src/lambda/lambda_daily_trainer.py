"""
AWS Lambda Function - Daily Price Forecasting Trainer
Triggered by EventBridge every morning at 6 AM IST

This Lambda:
1. Fetches latest data from AgMarkNet API
2. Trains Prophet models for 5 crops
3. Generates 30-day forecasts
4. Uploads to DynamoDB

Environment Variables Required:
- AGMARKNET_API_KEY
- PRICE_FORECAST_TABLE
- S3_BUCKET (for storing historical data)
"""
import json
import os
import boto3
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO
import requests

# Note: Prophet will be in Lambda Layer
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet not available - install in Lambda Layer")

# Configuration
CROPS = ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']
AGMARKNET_API_KEY = os.environ.get('AGMARKNET_API_KEY')
DYNAMODB_TABLE = os.environ.get('PRICE_FORECAST_TABLE', 'kisaanmitra-price-forecasts')
S3_BUCKET = os.environ.get('S3_BUCKET', 'kisaanmitra-images')
S3_PREFIX = 'historical_prices/'

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')


def fetch_agmarknet_data(commodity, days=30):
    """Fetch latest price data from AgMarkNet API"""
    print(f"[AGMARKNET] Fetching {commodity}...")
    
    try:
        url = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
        params = {
            'api-key': AGMARKNET_API_KEY,
            'format': 'json',
            'filters[commodity]': commodity.title(),
            'limit': 1000
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                # Extract date and price
                df = pd.DataFrame(records)
                # Assuming API returns 'arrival_date' and 'modal_price' columns
                # Adjust based on actual API response
                if 'arrival_date' in df.columns and 'modal_price' in df.columns:
                    df = df[['arrival_date', 'modal_price']].copy()
                    df.columns = ['date', 'price']
                    df['date'] = pd.to_datetime(df['date'])
                    df['price'] = pd.to_numeric(df['price'], errors='coerce')
                    df = df.dropna()
                    print(f"[AGMARKNET] ✅ {len(df)} records")
                    return df
        
        print(f"[AGMARKNET] ⚠️ No data for {commodity}")
        return None
        
    except Exception as e:
        print(f"[AGMARKNET] ❌ Error: {e}")
        return None


def load_historical_data_from_s3(commodity):
    """Load historical CSV from S3"""
    key = f"{S3_PREFIX}{commodity.title()}.csv"
    print(f"[S3] Loading {key}...")
    
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        csv_content = obj['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        df['date'] = pd.to_datetime(df['date'])
        print(f"[S3] ✅ Loaded {len(df)} records")
        return df
    except Exception as e:
        print(f"[S3] ⚠️ File not found, creating new: {e}")
        return pd.DataFrame(columns=['date', 'price'])


def save_historical_data_to_s3(commodity, df):
    """Save updated CSV to S3"""
    key = f"{S3_PREFIX}{commodity.title()}.csv"
    print(f"[S3] Saving {key}...")
    
    try:
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        print(f"[S3] ✅ Saved {len(df)} records")
        return True
    except Exception as e:
        print(f"[S3] ❌ Error: {e}")
        return False


def train_prophet_model(df):
    """Train Prophet model and generate 30-day forecast"""
    print(f"[PROPHET] Training model...")
    
    if not PROPHET_AVAILABLE:
        print("[PROPHET] ❌ Prophet not available")
        return None
    
    try:
        # Prepare data
        prophet_df = df.rename(columns={'date': 'ds', 'price': 'y'})
        prophet_df = prophet_df.sort_values('ds')
        
        # Train model
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        model.fit(prophet_df)
        
        # Generate 30-day forecast
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        # Get last 30 days
        forecast_30d = forecast.tail(30)
        
        print(f"[PROPHET] ✅ Generated 30-day forecast")
        return forecast_30d
        
    except Exception as e:
        print(f"[PROPHET] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_for_dynamodb(commodity, forecast_df):
    """Format forecast for DynamoDB"""
    forecasts = []
    
    for _, row in forecast_df.iterrows():
        date = pd.to_datetime(row['ds'])
        forecasts.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%A'),
            'price': Decimal(str(round(row['yhat'], 2))),
            'lower': Decimal(str(round(row['yhat_lower'], 2))),
            'upper': Decimal(str(round(row['yhat_upper'], 2)))
        })
    
    return {
        'commodity': commodity,
        'last_updated': datetime.now().isoformat(),
        'forecasts': forecasts,
        'model': 'Prophet',
        'training_records': len(forecast_df)
    }


def upload_to_dynamodb(forecast_data):
    """Upload forecast to DynamoDB"""
    commodity = forecast_data['commodity']
    print(f"[DYNAMODB] Uploading {commodity}...")
    
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(Item=forecast_data)
        print(f"[DYNAMODB] ✅ Uploaded {commodity}")
        return True
    except Exception as e:
        print(f"[DYNAMODB] ❌ Error: {e}")
        return False


def process_crop(commodity):
    """Complete pipeline for one crop"""
    print(f"\n{'='*50}")
    print(f"PROCESSING: {commodity.upper()}")
    print(f"{'='*50}")
    
    # Load historical data from S3
    historical_df = load_historical_data_from_s3(commodity)
    
    # Fetch new data from AgMarkNet
    new_data = fetch_agmarknet_data(commodity)
    
    # Merge if new data available
    if new_data is not None and len(new_data) > 0:
        combined_df = pd.concat([historical_df, new_data], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['date'], keep='last')
        combined_df = combined_df.sort_values('date')
        
        # Save updated data to S3
        save_historical_data_to_s3(commodity, combined_df)
        
        training_df = combined_df
    else:
        print(f"[INFO] Using existing data for {commodity}")
        training_df = historical_df
    
    # Train model
    forecast_df = train_prophet_model(training_df)
    if forecast_df is None:
        return False
    
    # Format and upload
    forecast_data = format_for_dynamodb(commodity, forecast_df)
    success = upload_to_dynamodb(forecast_data)
    
    return success


def lambda_handler(event, context):
    """
    Lambda handler - triggered by EventBridge
    """
    print("=" * 60)
    print("DAILY PRICE FORECASTING TRAINER - LAMBDA")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {}
    
    for crop in CROPS:
        try:
            success = process_crop(crop)
            results[crop] = success
        except Exception as e:
            print(f"[ERROR] {crop}: {e}")
            results[crop] = False
    
    # Summary
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for crop, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {crop.title()}")
    
    print(f"\nSuccessful: {successful}/{len(results)}")
    
    return {
        'statusCode': 200 if failed == 0 else 500,
        'body': json.dumps({
            'message': f'Training completed: {successful}/{len(results)} successful',
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    }
