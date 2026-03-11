"""Batch transform with a trained AutoML model."""

import boto3
import time
import pandas as pd
from io import StringIO
from datetime import datetime
from decimal import Decimal


class SageMakerBatchPredictor:
    """Run batch inference for time series forecasting"""
    
    def __init__(self, region='ap-south-1'):
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.s3_client = boto3.client('s3')
        self.region = region
    
    def create_model(self, model_name, best_candidate, role_arn):
        """Create SageMaker model from best candidate"""
        print(f"Creating model: {model_name}")
        
        try:
            # Extract model data from candidate
            inference_containers = best_candidate['InferenceContainers']
            
            response = self.sagemaker_client.create_model(
                ModelName=model_name,
                PrimaryContainer=inference_containers[0],
                ExecutionRoleArn=role_arn
            )
            
            print(f"Model created: {response['ModelArn']}")
            return response['ModelArn']
            
        except Exception as e:
            print(f"Error creating model: {e}")
            raise
    
    def create_transform_job(
        self,
        job_name,
        model_name,
        input_s3_uri,
        output_s3_uri,
        instance_type='ml.m5.xlarge',
        instance_count=1
    ):
        """Create batch transform job for inference"""
        print(f"Creating transform job: {job_name}")
        print(f"  Model: {model_name}")
        print(f"  Input: {input_s3_uri}")
        print(f"  Output: {output_s3_uri}")
        
        try:
            response = self.sagemaker_client.create_transform_job(
                TransformJobName=job_name,
                ModelName=model_name,
                TransformInput={
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': input_s3_uri
                        }
                    },
                    'ContentType': 'text/csv',
                    'SplitType': 'Line'
                },
                TransformOutput={
                    'S3OutputPath': output_s3_uri,
                    'AssembleWith': 'Line'
                },
                TransformResources={
                    'InstanceType': instance_type,
                    'InstanceCount': instance_count
                }
            )
            
            print(f"Transform job created: {response['TransformJobArn']}")
            return response
            
        except Exception as e:
            print(f"Error creating transform job: {e}")
            raise
    
    def wait_for_transform_job(self, job_name, check_interval=30, max_wait_time=1800):
        """Wait for transform job to complete"""
        print(f"Waiting for transform job: {job_name}")
        
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > max_wait_time:
                raise TimeoutError(f"Transform job did not complete within {max_wait_time}s")
            
            response = self.sagemaker_client.describe_transform_job(
                TransformJobName=job_name
            )
            
            status = response['TransformJobStatus']
            
            print(f"  [{int(elapsed)}s] Status: {status}")
            
            if status == 'Completed':
                print(f"Transform job completed!")
                return response
            
            elif status == 'Failed':
                failure_reason = response.get('FailureReason', 'Unknown')
                raise Exception(f"Transform job failed: {failure_reason}")
            
            elif status == 'Stopped':
                raise Exception("Transform job was stopped")
            
            time.sleep(check_interval)
    
    def get_predictions(self, output_s3_uri, s3_bucket, s3_key):
        """Download and parse predictions from S3"""
        print(f"Downloading predictions from s3://{s3_bucket}/{s3_key}")
        
        try:
            # Download from S3
            obj = self.s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            content = obj['Body'].read().decode('utf-8')
            
            # Parse CSV
            df = pd.read_csv(StringIO(content))
            
            print(f"Downloaded {len(df)} predictions")
            return df
            
        except Exception as e:
            print(f"Error downloading predictions: {e}")
            raise
    
    def format_predictions_for_dynamodb(self, predictions_df):
        """Groups predictions into {crop: [{date, day, price, lower, upper}]}"""
        out = {}
        for _, row in predictions_df.iterrows():
            day = pd.to_datetime(row['timestamp'])
            p50 = float(row['p50'])
            out.setdefault(row['item_id'], []).append({
                'date': day.strftime('%Y-%m-%d'),
                'day': day.strftime('%A'),
                'price': Decimal(str(round(p50, 2))),
                'lower': Decimal(str(round(float(row.get('p10', p50 * 0.9)), 2))),
                'upper': Decimal(str(round(float(row.get('p90', p50 * 1.1)), 2))),
            })
        for rows in out.values():
            rows.sort(key=lambda r: r['date'])
        return out


if __name__ == '__main__':
    # Example usage
    predictor = SageMakerBatchPredictor()
    
    # Assume we have a trained model
    model_name = 'kisaanmitra-forecast-model'
    job_name = f"kisaanmitra-transform-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    input_uri = 's3://kisaanmitra-ml-data/sagemaker-forecasting/inference_input.csv'
    output_uri = 's3://kisaanmitra-ml-data/sagemaker-forecasting/predictions/'
    
    # Create transform job
    # response = predictor.create_transform_job(
    #     job_name=job_name,
    #     model_name=model_name,
    #     input_s3_uri=input_uri,
    #     output_s3_uri=output_uri
    # )
    
    # Wait for completion
    # status = predictor.wait_for_transform_job(job_name)
    
    # Get predictions
    # predictions = predictor.get_predictions(
    #     output_uri,
    #     'kisaanmitra-ml-data',
    #     'sagemaker-forecasting/predictions/inference_input.csv.out'
    # )
