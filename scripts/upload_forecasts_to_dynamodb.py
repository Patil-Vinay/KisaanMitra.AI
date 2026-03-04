#!/usr/bin/env python3
"""
Upload price forecasts to DynamoDB
Generates 30-day forecasts for 5 crops and uploads to AWS
"""
import json
import boto3
from boto3.dynamodb.types import TypeSerializer
from decimal import Decimal
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def generate_forecast_data():
    """Generate forecast data for all 5 crops"""
    crops = {
        'onion': {'base': 1800, 'volatility': 200},
        'rice': {'base': 2500, 'volatility': 150},
        'sugarcane': {'base': 350, 'volatility': 30},
        'tomato': {'base': 1200, 'volatility': 300},
        'wheat': {'base': 2200, 'volatility': 100}
    }
    
    forecasts = {}
    today = datetime.now()
    
    for crop, params in crops.items():
        forecast_list = []
        base_price = params['base']
        volatility = params['volatility']
        
        for day in range(30):
            date = today + timedelta(days=day)
            
            # Simple trend: slight increase over time with some variation
            trend = day * 2
            variation = (day % 7 - 3) * (volatility / 10)
            
            predicted_price = base_price + trend + variation
            lower_bound = predicted_price - volatility
            upper_bound = predicted_price + volatility
            
            forecast_list.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%A'),
                'price': Decimal(str(round(predicted_price, 2))),
                'lower': Decimal(str(round(lower_bound, 2))),
                'upper': Decimal(str(round(upper_bound, 2)))
            })
        
        forecasts[crop] = {
            'commodity': crop,
            'last_updated': today.isoformat(),
            'forecasts': forecast_list
        }
    
    return forecasts

def upload_to_dynamodb(forecasts, table_name='kisaanmitra-price-forecasts', region='ap-south-1'):
    """Upload forecasts to DynamoDB"""
    print(f"[UPLOAD] Connecting to DynamoDB table: {table_name}")
    
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    # Wait for table to be active
    print("[UPLOAD] Waiting for table to be active...")
    table.wait_until_exists()
    
    success_count = 0
    for crop, data in forecasts.items():
        try:
            print(f"[UPLOAD] Uploading {crop} forecast...")
            table.put_item(Item=data)
            success_count += 1
            print(f"[UPLOAD] ✅ {crop} uploaded successfully")
        except Exception as e:
            print(f"[UPLOAD] ❌ Error uploading {crop}: {e}")
    
    print(f"\n[UPLOAD] ===== SUMMARY =====")
    print(f"[UPLOAD] Total crops: {len(forecasts)}")
    print(f"[UPLOAD] Successful uploads: {success_count}")
    print(f"[UPLOAD] Failed uploads: {len(forecasts) - success_count}")
    
    return success_count == len(forecasts)

def main():
    print("=" * 60)
    print("PRICE FORECAST UPLOADER")
    print("=" * 60)
    
    # Generate forecasts
    print("\n[STEP 1] Generating forecast data...")
    forecasts = generate_forecast_data()
    print(f"[STEP 1] ✅ Generated forecasts for {len(forecasts)} crops")
    
    # Upload to DynamoDB
    print("\n[STEP 2] Uploading to DynamoDB...")
    success = upload_to_dynamodb(forecasts)
    
    if success:
        print("\n✅ ALL FORECASTS UPLOADED SUCCESSFULLY!")
        print("\nYou can now test price forecasting via WhatsApp:")
        print("  - 'week forecast for wheat'")
        print("  - '7 day prices for onion'")
        print("  - 'price forecast for rice'")
    else:
        print("\n❌ SOME UPLOADS FAILED. Check errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
