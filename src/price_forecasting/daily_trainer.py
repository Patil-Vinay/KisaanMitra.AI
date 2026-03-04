#!/usr/bin/env python3
"""
Daily Price Forecasting Trainer
Runs every morning at 6 AM IST to:
1. Fetch latest data from AgMarkNet API
2. Update historical CSV files
3. Train Prophet models for 5 crops
4. Generate 30-day forecasts
5. Upload to DynamoDB

This ensures WhatsApp bot just reads pre-computed forecasts (no training on-demand)
"""
import os
import sys
import json
import boto3
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from prophet import Prophet
import requests

# Supported crops
CROPS = ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']

# AgMarkNet API configuration
AGMARKNET_API_KEY = os.environ.get('AGMARKNET_API_KEY', 'YOUR_AGMARKNET_API_KEY')
AGMARKNET_BASE_URL = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'

# AWS configuration
DYNAMODB_TABLE = os.environ.get('PRICE_FORECAST_TABLE', 'kisaanmitra-price-forecasts')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'historical_prices')


def fetch_agmarknet_data(commodity, days=30):
    """
    Fetch latest price data from AgMarkNet API
    Returns: DataFrame with date and price columns
    """
    print(f"[AGMARKNET] Fetching data for {commodity}...")
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'api-key': AGMARKNET_API_KEY,
            'format': 'json',
            'filters[commodity]': commodity.title(),
            'limit': 1000
        }
        
        response = requests.get(AGMARKNET_BASE_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                df = pd.DataFrame(records)
                print(f"[AGMARKNET] ✅ Fetched {len(df)} records for {commodity}")
                return df
            else:
                print(f"[AGMARKNET] ⚠️ No records found for {commodity}")
                return None
        else:
            print(f"[AGMARKNET] ❌ API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[AGMARKNET] ❌ Error fetching {commodity}: {e}")
        return None


def update_csv_file(commodity, new_data):
    """
    Update historical CSV file with new data
    Appends new records and removes duplicates
    """
    csv_path = os.path.join(DATA_DIR, f'{commodity.title()}.csv')
    print(f"[CSV] Updating {csv_path}...")
    
    try:
        # Read existing data - skip first row (header description)
        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path, skiprows=1)
            print(f"[CSV] Existing records: {len(existing_df)}")
            
            # Extract date and price columns
            if 'Date' in existing_df.columns:
                price_col = [col for col in existing_df.columns if 'Price' in col or 'Modal' in col][0]
                existing_df = existing_df[['Date', price_col]].copy()
                existing_df.columns = ['date', 'price']
        else:
            existing_df = pd.DataFrame(columns=['date', 'price'])
            print(f"[CSV] Creating new file")
        
        # Ensure new_data has correct columns
        if 'date' not in new_data.columns:
            print(f"[CSV] ⚠️ New data missing 'date' column, skipping update")
            return existing_df
        
        # Combine and remove duplicates
        combined_df = pd.concat([existing_df, new_data], ignore_index=True)
        combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d-%m-%Y', errors='coerce')
        combined_df['price'] = pd.to_numeric(combined_df['price'], errors='coerce')
        combined_df = combined_df.dropna()
        combined_df = combined_df.drop_duplicates(subset=['date'], keep='last')
        combined_df = combined_df.sort_values('date')
        
        # Save updated file with proper header
        with open(csv_path, 'w') as f:
            f.write(",,,,All Type of Report (All Grades),,,\n")
            f.write("State,Commodity Group,Commodity,Date,Arrival Quantity,Arrival Unit,Modal Price,Price Unit\n")
        
        # Append data
        combined_df.to_csv(csv_path, mode='a', index=False, header=False)
        print(f"[CSV] ✅ Updated with {len(combined_df)} total records")
        
        return combined_df
        
    except Exception as e:
        print(f"[CSV] ❌ Error updating {commodity}: {e}")
        import traceback
        traceback.print_exc()
        return None


def train_prophet_model(commodity):
    """
    Train Prophet model on historical data
    Returns: 30-day forecast
    """
    csv_path = os.path.join(DATA_DIR, f'{commodity.title()}.csv')
    print(f"[PROPHET] Training model for {commodity}...")
    
    try:
        # Load data - skip first row (header description)
        df = pd.read_csv(csv_path, skiprows=1)
        
        # Check actual column names
        print(f"[PROPHET] Columns: {df.columns.tolist()}")
        
        # Map to standard names (adjust based on actual CSV structure)
        # Expected columns: Date, Modal Price
        if 'Date' in df.columns and 'Modal Price 02-03-2021 to 02-03-2026' in df.columns:
            df = df[['Date', 'Modal Price 02-03-2021 to 02-03-2026']].copy()
            df.columns = ['date', 'price']
        elif 'Date' in df.columns:
            # Find price column (contains 'Price' or 'Modal')
            price_col = [col for col in df.columns if 'Price' in col or 'Modal' in col][0]
            df = df[['Date', price_col]].copy()
            df.columns = ['date', 'price']
        else:
            print(f"[PROPHET] ❌ Could not find Date column")
            return None
        
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna()
        
        if len(df) < 30:
            print(f"[PROPHET] ❌ Not enough data: {len(df)} records")
            return None
        
        print(f"[PROPHET] Training on {len(df)} records")
        
        # Prepare for Prophet (requires 'ds' and 'y' columns)
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
        
        # Extract last 30 days (future predictions)
        forecast_30d = forecast.tail(30)
        
        print(f"[PROPHET] ✅ Generated 30-day forecast for {commodity}")
        return forecast_30d
        
    except Exception as e:
        print(f"[PROPHET] ❌ Error training {commodity}: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_forecast_for_dynamodb(commodity, forecast_df):
    """
    Format Prophet forecast for DynamoDB storage
    Converts to proper structure with Decimal types
    """
    print(f"[FORMAT] Formatting forecast for {commodity}...")
    
    try:
        forecasts = []
        
        for _, row in forecast_df.iterrows():
            date = pd.to_datetime(row['ds'])
            
            forecast_item = {
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%A'),
                'price': Decimal(str(round(row['yhat'], 2))),
                'lower': Decimal(str(round(row['yhat_lower'], 2))),
                'upper': Decimal(str(round(row['yhat_upper'], 2)))
            }
            forecasts.append(forecast_item)
        
        result = {
            'commodity': commodity,
            'last_updated': datetime.now().isoformat(),
            'forecasts': forecasts,
            'model': 'Prophet',
            'training_records': len(forecast_df)
        }
        
        print(f"[FORMAT] ✅ Formatted {len(forecasts)} forecast records")
        return result
        
    except Exception as e:
        print(f"[FORMAT] ❌ Error formatting {commodity}: {e}")
        return None


def upload_to_dynamodb(forecast_data):
    """
    Upload forecast to DynamoDB
    """
    commodity = forecast_data['commodity']
    print(f"[DYNAMODB] Uploading {commodity} forecast...")
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        table.put_item(Item=forecast_data)
        
        print(f"[DYNAMODB] ✅ Uploaded {commodity} successfully")
        return True
        
    except Exception as e:
        print(f"[DYNAMODB] ❌ Error uploading {commodity}: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_crop(commodity):
    """
    Complete pipeline for one crop:
    1. Fetch new data from AgMarkNet
    2. Update CSV file
    3. Train Prophet model
    4. Format forecast
    5. Upload to DynamoDB
    """
    print(f"\n{'='*60}")
    print(f"PROCESSING: {commodity.upper()}")
    print(f"{'='*60}")
    
    # Step 1: Fetch new data (optional - can skip if API fails)
    new_data = fetch_agmarknet_data(commodity)
    if new_data is not None:
        # Step 2: Update CSV
        updated_df = update_csv_file(commodity, new_data)
    else:
        print(f"[SKIP] Using existing CSV data for {commodity}")
    
    # Step 3: Train model
    forecast_df = train_prophet_model(commodity)
    if forecast_df is None:
        print(f"[FAIL] ❌ Could not train model for {commodity}")
        return False
    
    # Step 4: Format for DynamoDB
    forecast_data = format_forecast_for_dynamodb(commodity, forecast_df)
    if forecast_data is None:
        print(f"[FAIL] ❌ Could not format forecast for {commodity}")
        return False
    
    # Step 5: Upload to DynamoDB
    success = upload_to_dynamodb(forecast_data)
    
    if success:
        print(f"[SUCCESS] ✅ {commodity.upper()} pipeline completed")
    else:
        print(f"[FAIL] ❌ {commodity.upper()} pipeline failed")
    
    return success


def main():
    """
    Main function - process all crops
    """
    print("=" * 60)
    print("DAILY PRICE FORECASTING TRAINER")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    for crop in CROPS:
        success = process_crop(crop)
        results[crop] = success
    
    # Summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    for crop, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{crop.title():15} {status}")
    
    print(f"\nTotal: {len(results)} crops")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL CROPS TRAINED SUCCESSFULLY!")
        return 0
    else:
        print(f"\n⚠️ {failed} CROP(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())

