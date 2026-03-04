"""
SageMaker AutoML Trainer for Time Series Forecasting
Creates and manages AutoML jobs for price forecasting
"""

import boto3
import time
from datetime import datetime
import json


class SageMakerAutoMLTrainer:
    """Manage SageMaker AutoML time series forecasting jobs"""
    
    def __init__(self, role_arn, region='ap-south-1'):
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.role_arn = role_arn
        self.region = region
    
    def create_forecasting_job(
        self,
        job_name,
        train_s3_uri,
        output_s3_uri,
        forecast_horizon=30,
        forecast_frequency='D',
        item_id_column='item_id',
        timestamp_column='timestamp',
        target_column='price'
    ):
        """
        Create SageMaker AutoML job for time series forecasting
        
        Args:
            job_name: Unique name for the AutoML job
            train_s3_uri: S3 URI of training data CSV
            output_s3_uri: S3 URI for output artifacts
            forecast_horizon: Number of time steps to forecast (default: 30 days)
            forecast_frequency: Frequency of forecasts ('D' for daily, 'W' for weekly)
            item_id_column: Name of item identifier column
            timestamp_column: Name of timestamp column
            target_column: Name of target column to forecast
        
        Returns:
            dict: Job creation response
        """
        print(f"Creating AutoML job: {job_name}")
        print(f"  Training data: {train_s3_uri}")
        print(f"  Forecast horizon: {forecast_horizon} {forecast_frequency}")
        
        try:
            response = self.sagemaker_client.create_auto_ml_job_v2(
                AutoMLJobName=job_name,
                AutoMLJobInputDataConfig=[
                    {
                        'ChannelType': 'training',
                        'ContentType': 'text/csv;header=present',
                        'DataSource': {
                            'S3DataSource': {
                                'S3DataType': 'S3Prefix',
                                'S3Uri': train_s3_uri
                            }
                        }
                    }
                ],
                OutputDataConfig={
                    'S3OutputPath': output_s3_uri
                },
                AutoMLProblemTypeConfig={
                    'TimeSeriesForecastingJobConfig': {
                        'ForecastFrequency': forecast_frequency,
                        'ForecastHorizon': forecast_horizon,
                        'TimeSeriesConfig': {
                            'TargetAttributeName': target_column,
                            'TimestampAttributeName': timestamp_column,
                            'ItemIdentifierAttributeName': item_id_column
                        },
                        'ForecastQuantiles': ['p50', 'p60', 'p70', 'p80', 'p90']
                    }
                },
                RoleArn=self.role_arn
            )
            
            print(f"✅ AutoML job created: {response['AutoMLJobArn']}")
            return response
            
        except Exception as e:
            print(f"❌ Error creating AutoML job: {e}")
            raise
    
    def get_job_status(self, job_name):
        """
        Get status of AutoML job
        
        Args:
            job_name: Name of the AutoML job
        
        Returns:
            dict: Job status information
        """
        try:
            response = self.sagemaker_client.describe_auto_ml_job_v2(
                AutoMLJobName=job_name
            )
            
            status = response['AutoMLJobStatus']
            secondary_status = response.get('AutoMLJobSecondaryStatus', 'N/A')
            
            return {
                'status': status,
                'secondary_status': secondary_status,
                'creation_time': response['CreationTime'],
                'last_modified_time': response['LastModifiedTime'],
                'failure_reason': response.get('FailureReason'),
                'best_candidate': response.get('BestCandidate')
            }
            
        except Exception as e:
            print(f"❌ Error getting job status: {e}")
            raise
    
    def wait_for_completion(self, job_name, check_interval=60, max_wait_time=7200):
        """
        Wait for AutoML job to complete
        
        Args:
            job_name: Name of the AutoML job
            check_interval: Seconds between status checks (default: 60)
            max_wait_time: Maximum seconds to wait (default: 7200 = 2 hours)
        
        Returns:
            dict: Final job status
        """
        print(f"Waiting for job completion: {job_name}")
        print(f"  Check interval: {check_interval}s")
        print(f"  Max wait time: {max_wait_time}s")
        
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > max_wait_time:
                raise TimeoutError(f"Job did not complete within {max_wait_time}s")
            
            status_info = self.get_job_status(job_name)
            status = status_info['status']
            secondary_status = status_info['secondary_status']
            
            print(f"  [{int(elapsed)}s] Status: {status} | {secondary_status}")
            
            if status == 'Completed':
                print(f"✅ Job completed successfully!")
                return status_info
            
            elif status == 'Failed':
                failure_reason = status_info.get('failure_reason', 'Unknown')
                raise Exception(f"Job failed: {failure_reason}")
            
            elif status == 'Stopped':
                raise Exception("Job was stopped")
            
            # Still in progress
            time.sleep(check_interval)
    
    def get_best_candidate(self, job_name):
        """
        Get best model candidate from completed job
        
        Args:
            job_name: Name of the AutoML job
        
        Returns:
            dict: Best candidate information
        """
        status_info = self.get_job_status(job_name)
        
        if status_info['status'] != 'Completed':
            raise Exception(f"Job not completed. Status: {status_info['status']}")
        
        best_candidate = status_info.get('best_candidate')
        
        if not best_candidate:
            raise Exception("No best candidate found")
        
        print(f"✅ Best candidate: {best_candidate['CandidateName']}")
        print(f"   Objective metric: {best_candidate.get('FinalAutoMLJobObjectiveMetric')}")
        
        return best_candidate
    
    def list_candidates(self, job_name, max_results=10):
        """
        List all model candidates from job
        
        Args:
            job_name: Name of the AutoML job
            max_results: Maximum number of candidates to return
        
        Returns:
            list: List of candidates
        """
        try:
            response = self.sagemaker_client.list_candidates_for_auto_ml_job(
                AutoMLJobName=job_name,
                MaxResults=max_results,
                SortBy='FinalObjectiveMetricValue',
                SortOrder='Descending'
            )
            
            candidates = response['Candidates']
            
            print(f"Found {len(candidates)} candidates:")
            for i, candidate in enumerate(candidates, 1):
                name = candidate['CandidateName']
                metric = candidate.get('FinalAutoMLJobObjectiveMetric', {})
                metric_value = metric.get('Value', 'N/A')
                print(f"  {i}. {name}: {metric_value}")
            
            return candidates
            
        except Exception as e:
            print(f"❌ Error listing candidates: {e}")
            raise


if __name__ == '__main__':
    # Example usage
    role_arn = 'arn:aws:iam::482548785371:role/SageMakerExecutionRole'
    
    trainer = SageMakerAutoMLTrainer(role_arn=role_arn)
    
    # Create job
    job_name = f"kisaanmitra-forecast-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    train_uri = 's3://kisaanmitra-ml-data/sagemaker-forecasting/train.csv'
    output_uri = 's3://kisaanmitra-ml-data/sagemaker-forecasting/output'
    
    response = trainer.create_forecasting_job(
        job_name=job_name,
        train_s3_uri=train_uri,
        output_s3_uri=output_uri,
        forecast_horizon=30,
        forecast_frequency='D'
    )
    
    # Wait for completion (in production, use Step Functions or EventBridge)
    # status = trainer.wait_for_completion(job_name)
    
    # Get best candidate
    # best_candidate = trainer.get_best_candidate(job_name)
