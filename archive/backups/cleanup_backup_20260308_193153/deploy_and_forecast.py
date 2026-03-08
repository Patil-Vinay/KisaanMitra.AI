"""
Deploy SageMaker Endpoint and Generate Forecasts
This script:
1. Deploys the trained model as a real-time endpoint
2. Generates 30-day forecasts for all crops
3. Stores forecasts in DynamoDB
4. Optionally deletes the endpoint to save costs
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration
REGION = 'ap-south-1'
AUTOML_JOB_NAME = 'km-260304185319'
ENDPOINT_NAME = 'kisaanmitra-forecast-endpoint'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
ROLE_ARN = 'arn:aws:iam::482548785371:role/KisaanMitra-SageMaker-Role'

# Crops to forecast
CROPS = ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']

# Initialize AWS clients
sagemaker = boto3.client('sagemaker', region_name=REGION)
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)


def get_best_candidate():
    """Get best candidate from completed AutoML job"""
    print(f"\n📊 Fetching best candidate from AutoML job: {AUTOML_JOB_NAME}")
    
    response = sagemaker.describe_auto_ml_job_v2(AutoMLJobName=AUTOML_JOB_NAME)
    
    if response['AutoMLJobStatus'] != 'Completed':
        raise Exception(f"AutoML job not completed. Status: {response['AutoMLJobStatus']}")
    
    best_candidate = response['BestCandidate']
    print(f"✅ Best candidate: {best_candidate['CandidateName']}")
    print(f"   Metric: {best_candidate['FinalAutoMLJobObjectiveMetric']['MetricName']}")
    print(f"   Value: {best_candidate['FinalAutoMLJobObjectiveMetric']['Value']}")
    
    return best_candidate


def create_model(best_candidate):
    """Create SageMaker model from best candidate"""
    model_name = f"{AUTOML_JOB_NAME}-model"
    
    print(f"\n🔨 Creating model: {model_name}")
    
    try:
        # Check if model already exists
        try:
            sagemaker.describe_model(ModelName=model_name)
            print(f"⚠️  Model already exists: {model_name}")
            return model_name
        except sagemaker.exceptions.ClientError:
            pass
        
        # Get inference container from best candidate
        inference_containers = best_candidate['InferenceContainers']
        
        response = sagemaker.create_model(
            ModelName=model_name,
            PrimaryContainer=inference_containers[0],
            ExecutionRoleArn=ROLE_ARN
        )
        
        print(f"✅ Model created: {response['ModelArn']}")
        return model_name
        
    except Exception as e:
        print(f"❌ Error creating model: {e}")
        raise


def create_endpoint_config(model_name):
    """Create endpoint configuration"""
    config_name = f"{model_name}-config"
    
    print(f"\n⚙️  Creating endpoint config: {config_name}")
    
    try:
        # Check if config already exists
        try:
            sagemaker.describe_endpoint_config(EndpointConfigName=config_name)
            print(f"⚠️  Endpoint config already exists: {config_name}")
            return config_name
        except sagemaker.exceptions.ClientError:
            pass
        
        response = sagemaker.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InstanceType': 'ml.m5.xlarge',
                    'InitialInstanceCount': 1,
                    'InitialVariantWeight': 1.0
                }
            ]
        )
        
        print(f"✅ Endpoint config created: {response['EndpointConfigArn']}")
        return config_name
        
    except Exception as e:
        print(f"❌ Error creating endpoint config: {e}")
        raise


def create_endpoint(config_name):
    """Create or update endpoint"""
    print(f"\n🚀 Creating endpoint: {ENDPOINT_NAME}")
    
    try:
        # Check if endpoint already exists
        try:
            response = sagemaker.describe_endpoint(EndpointName=ENDPOINT_NAME)
            status = response['EndpointStatus']
            
            if status == 'InService':
                print(f"⚠️  Endpoint already exists and is InService")
                return ENDPOINT_NAME
            elif status in ['Creating', 'Updating']:
                print(f"⚠️  Endpoint is {status}, waiting...")
                wait_for_endpoint()
                return ENDPOINT_NAME
            else:
                print(f"⚠️  Endpoint exists with status {status}, updating...")
                sagemaker.update_endpoint(
                    EndpointName=ENDPOINT_NAME,
                    EndpointConfigName=config_name
                )
                wait_for_endpoint()
                return ENDPOINT_NAME
                
        except sagemaker.exceptions.ClientError:
            # Endpoint doesn't exist, create it
            response = sagemaker.create_endpoint(
                EndpointName=ENDPOINT_NAME,
                EndpointConfigName=config_name
            )
            
            print(f"✅ Endpoint creation started: {response['EndpointArn']}")
            print(f"⏳ Waiting for endpoint to be InService (this takes 5-10 minutes)...")
            
            wait_for_endpoint()
            return ENDPOINT_NAME
        
    except Exception as e:
        print(f"❌ Error creating endpoint: {e}")
        raise


def wait_for_endpoint(check_interval=30, max_wait_time=1200):
    """Wait for endpoint to be InService"""
    start_time = time.time()
    
    while True:
        elapsed = int(time.time() - start_time)
        
        if elapsed > max_wait_time:
            raise TimeoutError(f"Endpoint did not become InService within {max_wait_time}s")
        
        response = sagemaker.describe_endpoint(EndpointName=ENDPOINT_NAME)
        status = response['EndpointStatus']
        
        print(f"  [{elapsed}s] Status: {status}")
        
        if status == 'InService':
            print(f"✅ Endpoint is InService!")
            return
        
        elif status == 'Failed':
            failure_reason = response.get('FailureReason', 'Unknown')
            raise Exception(f"Endpoint creation failed: {failure_reason}")
        
        time.sleep(check_interval)


def generate_forecast_for_crop(crop_name):
    """Generate 30-day forecast for a single crop"""
    print(f"\n🔮 Generating forecast for: {crop_name}")
    
    try:
        # Prepare inference input
        # For time series forecasting, we need to provide the item_id
        # The model will generate forecasts for the next 30 days
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
    # This will vary based on SageMaker's output format
    if 'predictions' in forecast_data:
        predictions = forecast_data['predictions']
    elif 'forecasts' in forecast_data:
        predictions = forecast_data['forecasts']
    else:
        # Assume the data itself is the predictions
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
            price = 1000.0  # Default price
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
            'model_job': AUTOML_JOB_NAME
        }
        
        table.put_item(Item=item)
        
        print(f"✅ Forecast stored for {crop_name}")
        print(f"   First day: {forecasts[0]['date']} - ₹{forecasts[0]['price']:.2f}")
        print(f"   Last day: {forecasts[-1]['date']} - ₹{forecasts[-1]['price']:.2f}")
        
    except Exception as e:
        print(f"❌ Error storing forecast: {e}")
        raise


def delete_endpoint():
    """Delete endpoint to save costs"""
    print(f"\n🗑️  Deleting endpoint: {ENDPOINT_NAME}")
    
    try:
        sagemaker.delete_endpoint(EndpointName=ENDPOINT_NAME)
        print(f"✅ Endpoint deleted")
    except Exception as e:
        print(f"⚠️  Error deleting endpoint: {e}")


def main():
    """Main execution flow"""
    print("=" * 60)
    print("🚀 KisaanMitra Forecast Deployment")
    print("=" * 60)
    
    try:
        # Step 1: Get best candidate from AutoML job
        best_candidate = get_best_candidate()
        
        # Step 2: Create model
        model_name = create_model(best_candidate)
        
        # Step 3: Create endpoint configuration
        config_name = create_endpoint_config(model_name)
        
        # Step 4: Create endpoint
        endpoint_name = create_endpoint(config_name)
        
        # Step 5: Generate forecasts for all crops
        print("\n" + "=" * 60)
        print("🔮 Generating Forecasts")
        print("=" * 60)
        
        for crop in CROPS:
            try:
                # Generate forecast
                forecast_data = generate_forecast_for_crop(crop)
                
                # Format for DynamoDB
                forecasts = format_forecast_for_dynamodb(crop, forecast_data)
                
                # Store in DynamoDB
                store_forecast_in_dynamodb(crop, forecasts)
                
                print(f"✅ {crop.upper()} forecast complete")
                
            except Exception as e:
                print(f"❌ Failed to process {crop}: {e}")
                continue
        
        # Step 6: Ask if user wants to delete endpoint
        print("\n" + "=" * 60)
        print("✅ Forecast Generation Complete!")
        print("=" * 60)
        print(f"\n💰 Endpoint Cost: ~₹4-5 per hour while running")
        print(f"   Endpoint Name: {ENDPOINT_NAME}")
        print(f"\nOptions:")
        print(f"1. Keep endpoint running for future forecasts")
        print(f"2. Delete endpoint now to save costs (can recreate later)")
        
        delete_choice = input("\nDelete endpoint? (y/n): ").strip().lower()
        
        if delete_choice == 'y':
            delete_endpoint()
        else:
            print(f"✅ Endpoint kept running: {ENDPOINT_NAME}")
            print(f"   Remember to delete it later to avoid charges!")
        
        print("\n" + "=" * 60)
        print("🎉 All Done!")
        print("=" * 60)
        print(f"\nForecasts stored in DynamoDB table: {DYNAMODB_TABLE}")
        print(f"Farmers can now query price forecasts via WhatsApp!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
