"""
SageMaker Batch Predictor for Time Series Forecasting
Runs batch inference to generate forecasts
"""

import boto3
import time
import pandas as pd
from io import StringIO
from datetime import datetime


class SageMakerBatchPredictor:
    """Run batch inference for time series forecasting"""
    
    def __init__(self, region='ap-south-1'):
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.s3_client = boto3.client('s3')
        self.region = region
    
    def create_model(self, model_name, best_candidate, role_arn):
        """
        Create SageMaker model from best candidate
        
        Args:
            model_name: Name for the model
            best_candidate: Best candidate from AutoML job
            role_arn: IAM role ARN
        
        Returns:
            str: Model ARN
        """
        print(f"Creating model: {model_name}")
        
        try:
            # Extract model data from candidate
            inference_containers = best_candidate['InferenceContainers']
            
            response = self.sagemaker_client.create_model(
                ModelName=model_name,
                PrimaryContainer=inference_containers[0],
                ExecutionRoleArn=role_arn
            )
            
            print(f"✅ Model created: {response['ModelArn']}")
            return response['ModelArn']
            
        except Exception as e:
            print(f"❌ Error creating model: {e}")
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
        """
        Create batch transform job for inference
        
        Args:
            job_name: Name for the transform job
            model_name: Name of the model to use
            input_s3_uri: S3 URI of input data
            output_s3_uri: S3 URI for output predictions
            instance_type: Instance type for inference
            instance_count: Number of instances
        
        Returns:
            dict: Transform job response
        """
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
            
            print(f"✅ Transform job created: {response['TransformJobArn']}")
            return response
            
        except Exception as e:
            print(f"❌ Error creating transform job: {e}")
            raise
    
    def wait_for_transform_job(self, job_name, check_interval=30, max_wait_time=1800):
        """
        Wait for transform job to complete
        
        Args:
            job_name: Name of the transform job
            check_interval: Seconds between checks
            max_wait_time: Maximum seconds to wait
        
        Returns:
            dict: Final job status
        """
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
                print(f"✅ Transform job completed!")
                return response
            
            elif status == 'Failed':
                failure_reason = response.get('FailureReason', 'Unknown')
                raise Exception(f"Transform job failed: {failure_reason}")
            
            elif status == 'Stopped':
                raise Exception("Transform job was stopped")
            
            time.sleep(check_interval)
    
    def get_predictions(self, output_s3_uri, s3_bucket, s3_key):
        """
        Download and parse predictions from S3
        
        Args:
            output_s3_uri: S3 URI of output directory
            s3_bucket: S3 bucket name
            s3_key: S3 key of output file
        
        Returns:
            DataFrame: Predictions
        """
        print(f"Downloading predictions from s3://{s3_bucket}/{s3_key}")
        
        try:
            # Download from S3
            obj = self.s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            content = obj['Body'].read().decode('utf-8')
            
            # Parse CSV
            df = pd.read_csv(StringIO(content))
            
            print(f"✅ Downloaded {len(df)} predictions")
            return df
            
        except Exception as e:
            print(f"❌ Error downloading predictions: {e}")
            raise
    
    def format_predictions_for_dynamodb(self, predictions_df):
        """
        Format predictions for DynamoDB storage
        
        Args:
            predictions_df: DataFrame with predictions
        
        Returns:
            list: List of items ready for DynamoDB
        """
        items = []
        
        for _, row in predictions_df.iterrows():
            item = {
                'crop_name': row['item_id'],
                'forecast_date': row['timestamp'],
                'predicted_price': float(row['p50']),  # Median forecast
                'lower_bound': float(row.get('p10', row['p50'] * 0.9)),
                'upper_bound': float(row.get('p90', row['p50'] * 1.1)),
                'confidence': 0.8,  # 80% confidence interval
                'generated_at': datetime.now().isoformat(),
                'model_version': 'sagemaker_automl_v1'
            }
            items.append(item)
        
        return items


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
