"""
AWS Lambda Function for Daily Price Data Updates
Fetches data from AgMarkNet API, updates S3, retrains models, and stores forecasts
"""

import json
import os
import boto3
import requests
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import pickle

# AWS Clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
eventbridge = boto3.client('events')

# Configuration
S3_BUCKET = os.environ.get('S3_BUCKET', 'kisaanmitra-price-data')
AGMARKNET_API_KEY = os.environ.get('AGMARKNET_API_KEY', '')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
DYNAMODB_TABLE = os.environ.get('PRICE_FORECAST_TABLE', 'kisaanmitra-price-forecasts')

# Commodities to track
COMMODITIES = {
    'Onion': {'group': 'Vegetables', 'state': 'Maharashtra'},
    'Rice': {'group': 'Foodgrains', 'state': 'Maharashtra'},
    'Sugarcane': {'group': 'Cash Crops', 'state': 'Maharashtra'},
    'Tomato': {'group': 'Vegetables', 'state': 'Maharashtra'},
    'Wheat': {'group': 'Foodgrains', 'state': 'Maharashtra'}
}


def fetch_agmarknet_data(commodity, days=7):
    """
    Fetch latest price data from AgMarkNet API
    """
    if not AGMARKNET_API_KEY:
        print(f"⚠️ AgMarkNet API key not configured")
        return None
    
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    params = {
        'api-key': AGMARKNET_API_KEY,
        'format': 'json',
        'filters[commodity]': commodity,
        'filters[state]': COMMODITIES[commodity]['state'],
        'limit': 1000
    }
    
    try:
        print(f"📡 Fetching {commodity} data from AgMarkNet API...")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'records' not in data or not data['records']:
            print(f"⚠️ No data found for {commodity}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data['records'])
        
        # Parse dates and filter
        df['date'] = pd.to_datetime(df['arrival_date'], format='%d/%m/%Y', errors='coerce')
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        print(f"✅ Fetched {len(df)} records for {commodity}")
        return df
        
    except Exception as e:
        print(f"❌ Error fetching {commodity} data: {e}")
        return None


def load_csv_from_s3(commodity):
    """Load existing CSV from S3"""
    key = f"historical_prices/{commodity}.csv"
    
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Skip first row (header info)
        df = pd.read_csv(StringIO(csv_content), skiprows=1)
        print(f"📥 Loaded {len(df)} existing records for {commodity} from S3")
        return df
        
    except s3.exceptions.NoSuchKey:
        print(f"⚠️ No existing CSV found for {commodity} in S3")
        return None
    except Exception as e:
        print(f"❌ Error loading CSV from S3: {e}")
        return None


def save_csv_to_s3(commodity, df, header_row):
    """Save updated CSV to S3"""
    key = f"historical_prices/{commodity}.csv"
    
    try:
        # Create CSV with header
        csv_buffer = StringIO()
        csv_buffer.write(header_row + '\n')
        df.to_csv(csv_buffer, index=False)
        
        # Upload to S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        print(f"💾 Saved {len(df)} records for {commodity} to S3")
        return True
        
    except Exception as e:
        print(f"❌ Error saving CSV to S3: {e}")
        return False


def update_commodity_data(commodity):
    """Update CSV data for a commodity"""
    # Fetch latest data from API
    new_data = fetch_agmarknet_data(commodity, days=7)
    
    if new_data is None or len(new_data) == 0:
        print(f"⚠️ No new data for {commodity}")
        return False
    
    # Load existing CSV from S3
    existing_df = load_csv_from_s3(commodity)
    
    if existing_df is None:
        print(f"⚠️ Cannot update {commodity} - no existing data")
        return False
    
    # Get last date in existing data
    existing_df['Date'] = pd.to_datetime(existing_df['Date'], format='%d-%m-%Y', errors='coerce')
    last_date = existing_df['Date'].max()
    
    print(f"📅 Last date in CSV: {last_date.strftime('%d-%m-%Y')}")
    
    # Filter new data to only include dates after last_date
    new_data = new_data[new_data['date'] > last_date]
    
    if len(new_data) == 0:
        print(f"✅ {commodity} is already up to date")
        return False
    
    # Format new rows
    new_rows = []
    for _, row in new_data.iterrows():
        new_rows.append({
            'State': COMMODITIES[commodity]['state'],
            'Commodity Group': COMMODITIES[commodity]['group'],
            'Commodity': commodity,
            'Date': row['date'].strftime('%d-%m-%Y'),
            'Arrival Quantity 02-03-2021 to 02-03-2026': row.get('arrivals', 0),
            'Arrival Unit': 'Metric Tonnes',
            'Modal Price 02-03-2021 to 02-03-2026': row.get('modal_price', 0),
            'Price Unit': 'Rs./Quintal'
        })
    
    # Append new rows
    new_df = pd.DataFrame(new_rows)
    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Save back to S3
    header_row = f",,,,All Type of Report (All Grades) for 02-Mar-2021 to {datetime.now().strftime('%d-%b-%Y')},,,,"
    save_csv_to_s3(commodity, updated_df, header_row)
    
    print(f"✅ Added {len(new_rows)} new records for {commodity}")
    return True


def train_prophet_model(commodity):
    """
    Train Prophet model for a commodity
    Note: Prophet requires significant dependencies, so we'll use a simplified approach
    or invoke a separate Lambda with Prophet layer
    """
    print(f"🔧 Training model for {commodity}...")
    
    # Load data from S3
    df = load_csv_from_s3(commodity)
    
    if df is None or len(df) < 30:
        print(f"❌ Insufficient data for {commodity}")
        return None
    
    # Prepare data for Prophet
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    df = df[['Date', 'Modal Price 02-03-2021 to 02-03-2026']].copy()
    df.columns = ['ds', 'y']
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df = df.dropna().sort_values('ds').reset_index(drop=True)
    
    # For Lambda, we'll generate simple forecasts
    # In production, invoke a separate Lambda with Prophet layer
    # or use SageMaker for model training
    
    # Simple moving average forecast (placeholder)
    recent_prices = df['y'].tail(30).values
    avg_price = recent_prices.mean()
    std_price = recent_prices.std()
    
    # Generate 30-day forecast
    forecasts = []
    for i in range(30):
        date = datetime.now() + timedelta(days=i)
        forecasts.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%A'),
            'price': round(avg_price, 2),
            'lower': round(avg_price - std_price, 2),
            'upper': round(avg_price + std_price, 2)
        })
    
    return forecasts


def save_forecast_to_dynamodb(commodity, forecasts):
    """Save forecast to DynamoDB"""
    table = dynamodb.Table(DYNAMODB_TABLE)
    
    try:
        item = {
            'commodity': commodity.lower(),
            'generated_at': datetime.now().isoformat(),
            'forecasts': forecasts,
            'ttl': int((datetime.now() + timedelta(days=7)).timestamp())
        }
        
        table.put_item(Item=item)
        print(f"💾 Saved forecast for {commodity} to DynamoDB")
        return True
        
    except Exception as e:
        print(f"❌ Error saving forecast to DynamoDB: {e}")
        return False


def save_forecast_to_s3(commodity, forecasts):
    """Save forecast to S3 as JSON"""
    key = f"forecasts/{commodity.lower()}_forecast.json"
    
    try:
        forecast_data = {
            'crop': commodity,
            'generated_at': datetime.now().isoformat(),
            'predictions': forecasts
        }
        
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(forecast_data, indent=2),
            ContentType='application/json'
        )
        
        print(f"💾 Saved forecast for {commodity} to S3")
        return True
        
    except Exception as e:
        print(f"❌ Error saving forecast to S3: {e}")
        return False


def send_sns_notification(subject, message):
    """Send SNS notification"""
    if not SNS_TOPIC_ARN:
        return
    
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"📧 Sent SNS notification: {subject}")
    except Exception as e:
        print(f"❌ Error sending SNS: {e}")


def lambda_handler(event, context):
    """
    Main Lambda handler for daily price updates
    Triggered by EventBridge (CloudWatch Events) daily at 6 AM IST
    """
    print("=" * 60)
    print(f"🌅 Daily Price Update - {datetime.now().isoformat()}")
    print("=" * 60)
    
    updated_commodities = []
    failed_commodities = []
    
    # Update each commodity
    for commodity in COMMODITIES.keys():
        try:
            print(f"\n📊 Processing {commodity}...")
            
            # Update CSV data
            data_updated = update_commodity_data(commodity)
            
            # Train model and generate forecast
            forecasts = train_prophet_model(commodity)
            
            if forecasts:
                # Save to DynamoDB
                save_forecast_to_dynamodb(commodity, forecasts)
                
                # Save to S3
                save_forecast_to_s3(commodity, forecasts)
                
                updated_commodities.append(commodity)
            else:
                failed_commodities.append(commodity)
                
        except Exception as e:
            print(f"❌ Error processing {commodity}: {e}")
            failed_commodities.append(commodity)
    
    # Send summary notification
    summary = f"""
Daily Price Forecast Update Complete

✅ Successfully Updated: {len(updated_commodities)}
{', '.join(updated_commodities) if updated_commodities else 'None'}

❌ Failed: {len(failed_commodities)}
{', '.join(failed_commodities) if failed_commodities else 'None'}

Timestamp: {datetime.now().isoformat()}
"""
    
    send_sns_notification("KisaanMitra Price Update", summary)
    
    print("\n" + "=" * 60)
    print(f"✅ Update complete: {len(updated_commodities)}/{len(COMMODITIES)} commodities")
    print("=" * 60)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'updated': updated_commodities,
            'failed': failed_commodities,
            'timestamp': datetime.now().isoformat()
        })
    }
