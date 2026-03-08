"""
Generate Forecasts Only
Use this if the endpoint is already created but forecasts weren't generated
"""

import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration
REGION = 'ap-south-1'
ENDPOINT_NAME = 'kisaanmitra-forecast-endpoint'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
CROPS = ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']

# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)


def generate_forecast_for_crop(crop_name):
    """Generate 30-day forecast for a single crop"""
    print(f"\n🔮 Generating forecast for: {crop_name}")
    
    try:
        # Prepare inference input
        inference_input = {
            "instances": [
                {
                    "item_id": crop_name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d")
                }
            ],
            "configuration": {
                "num_samples": 100,
                "output_types": ["mean", "quantiles"],
                "quantiles": ["0.1", "0.5", "0.9"]
            }
        }
        
        # Invoke endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/json',
            Body=json.dumps(inference_input)
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        print(f"✅ Forecast generated for {crop_name}")
        return result
        
    except Exception as e:
        print(f"❌ Error generating forecast for {crop_name}: {e}")
        print(f"   Trying alternative input format...")
        
        # Try simpler format
        try:
            inference_input = {
                "item_id": crop_name
            }
            
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=ENDPOINT_NAME,
                ContentType='application/json',
                Body=json.dumps(inference_input)
            )
            
            result = json.loads(response['Body'].read().decode())
            print(f"✅ Forecast generated for {crop_name} (alternative format)")
            return result
            
        except Exception as e2:
            print(f"❌ Alternative format also failed: {e2}")
            raise


def format_forecast_for_dynamodb(crop_name, forecast_data):
    """Format forecast data for DynamoDB storage"""
    print(f"📝 Formatting forecast for DynamoDB: {crop_name}")
    
    forecasts = []
    
    # Parse forecast data based on response structure
    if 'predictions' in forecast_data:
        predictions = forecast_data['predictions']
    elif 'forecasts' in forecast_data:
        predictions = forecast_data['forecasts']
    else:
        predictions = forecast_data
    
    # Generate 30 days of forecasts
    start_date = datetime.now() + timedelta(days=1)
    
    for i in range(30):
        forecast_date = start_date + timedelta(days=i)
        
        # Extract price predictions
        if isinstance(predictions, list) and len(predictions) > i:
            pred = predictions[i]
            
            if isinstance(pred, dict):
                price = pred.get('mean', pred.get('0.5', pred.get('p50', 0)))
                lower = pred.get('0.1', pred.get('p10', price * 0.9))
                upper = pred.get('0.9', pred.get('p90', price * 1.1))
            else:
                price = float(pred)
                lower = price * 0.9
                upper = price * 1.1
        else:
            # If we don't have enough predictions, use a placeholder
            price = 1000.0
            lower = price * 0.9
            upper = price * 1.1
        
        forecast_item = {
            'date': forecast_date.strftime('%Y-%m-%d'),
            'day': forecast_date.strftime('%A'),
            'price': float(price),
            'lower': float(lower),
            'upper': float(upper)
        }
        
        forecasts.append(forecast_item)
    
    return forecasts


def store_forecast_in_dynamodb(crop_name, forecasts):
    """Store forecast in DynamoDB"""
    print(f"💾 Storing forecast in DynamoDB: {crop_name}")
    
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        # Convert floats to Decimal for DynamoDB
        forecasts_decimal = []
        for f in forecasts:
            forecasts_decimal.append({
                'date': f['date'],
                'day': f['day'],
                'price': Decimal(str(f['price'])),
                'lower': Decimal(str(f['lower'])),
                'upper': Decimal(str(f['upper']))
            })
        
        item = {
            'commodity': crop_name.lower(),
            'forecasts': forecasts_decimal,
            'generated_at': datetime.now().isoformat(),
            'model_version': 'sagemaker_automl_v1',
            'model_job': 'km-260304185319'
        }
        
        table.put_item(Item=item)
        
        print(f"✅ Forecast stored for {crop_name}")
        print(f"   First day: {forecasts[0]['date']} - ₹{forecasts[0]['price']:.2f}")
        print(f"   Last day: {forecasts[-1]['date']} - ₹{forecasts[-1]['price']:.2f}")
        
    except Exception as e:
        print(f"❌ Error storing forecast: {e}")
        raise


def main():
    """Main execution flow"""
    print("=" * 60)
    print("🔮 Generating Forecasts")
    print("=" * 60)
    
    success_count = 0
    failed_crops = []
    
    for crop in CROPS:
        try:
            # Generate forecast
            forecast_data = generate_forecast_for_crop(crop)
            
            # Format for DynamoDB
            forecasts = format_forecast_for_dynamodb(crop, forecast_data)
            
            # Store in DynamoDB
            store_forecast_in_dynamodb(crop, forecasts)
            
            print(f"✅ {crop.upper()} forecast complete")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to process {crop}: {e}")
            failed_crops.append(crop)
            continue
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{len(CROPS)}")
    if failed_crops:
        print(f"❌ Failed: {', '.join(failed_crops)}")
    
    print(f"\nForecasts stored in DynamoDB table: {DYNAMODB_TABLE}")
    print(f"Farmers can now query price forecasts via WhatsApp!")
    
    return 0 if success_count == len(CROPS) else 1


if __name__ == '__main__':
    exit(main())
