"""
Deploy SageMaker Endpoint and Generate Forecasts - PROPER METHOD
This uses the correct input format for SageMaker AutoML time series models
"""

import boto3
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO

# Configuration
REGION = 'ap-south-1'
AUTOML_JOB_NAME = 'km-260304185319'
ENDPOINT_NAME = 'kisaanmitra-forecast-endpoint'
S3_BUCKET = 'kisaanmitra-ml-data'
DYNAMODB_TABLE = 'kisaanmitra-price-forecasts'
ROLE_ARN = 'arn:aws:iam::482548785371:role/KisaanMitra-SageMaker-Role'

CROPS = {
    'onion': 'Onion',
    'rice': 'Rice',
    'sugarcane': 'Sugarcane',
    'tomato': 'Tomato',
    'wheat': 'Wheat'
}

# AWS clients
sagemaker = boto3.client('sagemaker', region_name=REGION)
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)


def get_best_candidate():
    """Get best candidate from AutoML job"""
    print(f"\n📊 Fetching best candidate from: {AUTOML_JOB_NAME}")
    
    response = sagemaker.describe_auto_ml_job_v2(AutoMLJobName=AUTOML_JOB_NAME)
    
    if response['AutoMLJobStatus'] != 'Completed':
        raise Exception(f"AutoML job not completed: {response['AutoMLJobStatus']}")
    
    best_candidate = response['BestCandidate']
    print(f"✅ Best candidate: {best_candidate['CandidateName']}")
    print(f"   Metric: {best_candidate['FinalAutoMLJobObjectiveMetric']['MetricName']}")
    print(f"   Value: {best_candidate['FinalAutoMLJobObjectiveMetric']['Value']}")
    
    return best_candidate


def create_model(best_candidate):
    """Create SageMaker model"""
    model_name = f"{AUTOML_JOB_NAME}-model"
    
    print(f"\n🔨 Creating model: {model_name}")
    
    try:
        sagemaker.describe_model(ModelName=model_name)
        print(f"⚠️  Model already exists")
        return model_name
    except:
        pass
    
    inference_containers = best_candidate['InferenceContainers']
    
    response = sagemaker.create_model(
        ModelName=model_name,
        PrimaryContainer=inference_containers[0],
        ExecutionRoleArn=ROLE_ARN
    )
    
    print(f"✅ Model created: {response['ModelArn']}")
    return model_name


def create_endpoint_config(model_name):
    """Create endpoint configuration"""
    config_name = f"{model_name}-config"
    
    print(f"\n⚙️  Creating endpoint config: {config_name}")
    
    try:
        sagemaker.describe_endpoint_config(EndpointConfigName=config_name)
        print(f"⚠️  Config already exists")
        return config_name
    except:
        pass
    
    response = sagemaker.create_endpoint_config(
        EndpointConfigName=config_name,
        ProductionVariants=[
            {
                'VariantName': 'AllTraffic',
                'ModelName': model_name,
                'InstanceType': 'ml.m5.xlarge',
                'InitialInstanceCount': 1
            }
        ]
    )
    
    print(f"✅ Config created: {response['EndpointConfigArn']}")
    return config_name


def create_endpoint(config_name):
    """Create endpoint"""
    print(f"\n🚀 Creating endpoint: {ENDPOINT_NAME}")
    
    try:
        response = sagemaker.describe_endpoint(EndpointName=ENDPOINT_NAME)
        status = response['EndpointStatus']
        
        if status == 'InService':
            print(f"✅ Endpoint already InService")
            return ENDPOINT_NAME
        elif status in ['Creating', 'Updating']:
            print(f"⏳ Endpoint is {status}, waiting...")
            wait_for_endpoint()
            return ENDPOINT_NAME
    except:
        pass
    
    response = sagemaker.create_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=config_name
    )
    
    print(f"✅ Endpoint creation started")
    print(f"⏳ Waiting for endpoint (5-10 minutes)...")
    
    wait_for_endpoint()
    return ENDPOINT_NAME


def wait_for_endpoint():
    """Wait for endpoint to be InService"""
    start_time = time.time()
    
    while True:
        elapsed = int(time.time() - start_time)
        
        response = sagemaker.describe_endpoint(EndpointName=ENDPOINT_NAME)
        status = response['EndpointStatus']
        
        print(f"  [{elapsed}s] Status: {status}")
        
        if status == 'InService':
            print(f"✅ Endpoint is InService!")
            return
        elif status == 'Failed':
            raise Exception(f"Endpoint failed: {response.get('FailureReason')}")
        
        time.sleep(30)


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
    """
    Generate forecast using SageMaker endpoint
    Uses CORRECT input format for AutoML time series
    """
    print(f"\n🔮 Generating forecast for: {crop_name}")
    
    try:
        # Load historical data
        df = load_historical_data(crop_name)
        print(f"  ✅ Loaded {len(df)} days of historical data")
        
        # Prepare input in CORRECT format for SageMaker AutoML
        # The model expects historical time series data
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
        print(f"     Start date: {inference_data['instances'][0]['start']}")
        print(f"     Data points: {len(inference_data['instances'][0]['target'])}")
        
        # Invoke endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='application/json',
            Body=json.dumps(inference_data)
        )
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        print(f"  ✅ Forecast generated successfully")
        
        # Extract forecasts
        forecasts = []
        start_date = datetime.now() + timedelta(days=1)
        
        # Parse predictions based on response structure
        if 'predictions' in result:
            predictions = result['predictions'][0] if isinstance(result['predictions'], list) else result['predictions']
        elif 'forecasts' in result:
            predictions = result['forecasts']
        else:
            predictions = result
        
        # Get mean and quantiles
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
                # Fallback if not enough predictions
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
        
        return forecasts
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def store_forecasts_in_dynamodb(crop_key, forecasts):
    """Store forecasts in DynamoDB"""
    print(f"  💾 Storing in DynamoDB...")
    
    table = dynamodb.Table(DYNAMODB_TABLE)
    
    item = {
        'commodity': crop_key,
        'forecasts': forecasts,
        'model': 'SageMaker AutoML',
        'model_version': 'sagemaker_automl_v1',
        'model_job': AUTOML_JOB_NAME,
        'last_updated': datetime.now().isoformat(),
        'training_records': 'Full historical dataset',
        'data_source': 'SageMaker Real-time Endpoint'
    }
    
    table.put_item(Item=item)
    
    print(f"  ✅ Stored {len(forecasts)} days")
    print(f"     Tomorrow: {forecasts[0]['date']} - ₹{forecasts[0]['price']}")
    print(f"     Day 30: {forecasts[-1]['date']} - ₹{forecasts[-1]['price']}")


def main():
    """Main execution"""
    print("="*60)
    print("🚀 SageMaker Real-time Endpoint Deployment")
    print("="*60)
    print(f"\nThis will:")
    print(f"1. Deploy SageMaker model as real-time endpoint")
    print(f"2. Generate 30-day forecasts for {len(CROPS)} crops")
    print(f"3. Store in DynamoDB: {DYNAMODB_TABLE}")
    print(f"4. Keep endpoint running for future use")
    print(f"\n💰 Cost: ~₹4-5 per hour while endpoint is running")
    
    print("\nStarting deployment...")
    
    try:
        # Step 1: Get best candidate
        best_candidate = get_best_candidate()
        
        # Step 2: Create model
        model_name = create_model(best_candidate)
        
        # Step 3: Create endpoint config
        config_name = create_endpoint_config(model_name)
        
        # Step 4: Create endpoint
        endpoint_name = create_endpoint(config_name)
        
        # Step 5: Generate forecasts for all crops
        print("\n" + "="*60)
        print("🔮 Generating Forecasts")
        print("="*60)
        
        success_count = 0
        failed_crops = []
        
        for crop_key, crop_name in CROPS.items():
            try:
                forecasts = generate_forecast_for_crop(crop_key, crop_name)
                store_forecasts_in_dynamodb(crop_key, forecasts)
                success_count += 1
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed_crops.append(crop_name)
                continue
        
        # Summary
        print("\n" + "="*60)
        print("✅ Deployment Complete!")
        print("="*60)
        print(f"\n📊 Results:")
        print(f"   Successful: {success_count}/{len(CROPS)}")
        if failed_crops:
            print(f"   Failed: {', '.join(failed_crops)}")
        
        print(f"\n🎯 Endpoint Status:")
        print(f"   Name: {ENDPOINT_NAME}")
        print(f"   Status: InService")
        print(f"   Cost: ~₹4-5 per hour")
        
        print(f"\n📝 Next Steps:")
        print(f"1. Test via WhatsApp: 'टमाटर का भाव कल क्या होगा?'")
        print(f"2. Monitor endpoint costs")
        print(f"3. Delete endpoint when not needed:")
        print(f"   aws sagemaker delete-endpoint --endpoint-name {ENDPOINT_NAME}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
