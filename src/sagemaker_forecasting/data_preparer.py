"""
Data Preparer for SageMaker Canvas Time Series Forecasting
Converts AgMarkNet data to SageMaker-compatible format
"""

import pandas as pd
from datetime import datetime, timedelta
import boto3
from io import StringIO


class SageMakerDataPreparer:
    """Prepare data for SageMaker Canvas time series forecasting"""
    
    def __init__(self, s3_bucket, s3_prefix='sagemaker-forecasting'):
        self.s3_client = boto3.client('s3')
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
    
    def prepare_training_data(self, historical_data_dict):
        """
        Convert historical price data to SageMaker format
        
        Args:
            historical_data_dict: Dict of {crop_name: DataFrame with 'date' and 'price' columns}
        
        Returns:
            DataFrame in SageMaker format with columns: item_id, timestamp, price
        """
        all_data = []
        
        for crop_name, df in historical_data_dict.items():
            # Ensure date column is datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Create SageMaker format
            crop_data = pd.DataFrame({
                'item_id': crop_name,
                'timestamp': df['date'],
                'price': df['price']
            })
            
            all_data.append(crop_data)
        
        # Combine all crops
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Sort by item and timestamp
        combined_df = combined_df.sort_values(['item_id', 'timestamp'])
        
        # Remove duplicates
        combined_df = combined_df.drop_duplicates(subset=['item_id', 'timestamp'], keep='last')
        
        return combined_df
    
    def upload_to_s3(self, df, filename='train.csv'):
        """
        Upload DataFrame to S3 as CSV
        
        Args:
            df: DataFrame to upload
            filename: Name of file in S3
        
        Returns:
            S3 URI of uploaded file
        """
        # Format timestamp for SageMaker (yyyy-MM-dd HH:mm:ss)
        df_copy = df.copy()
        df_copy['timestamp'] = df_copy['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert to CSV
        csv_buffer = StringIO()
        df_copy.to_csv(csv_buffer, index=False)
        
        # Upload to S3
        s3_key = f"{self.s3_prefix}/{filename}"
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=s3_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        s3_uri = f"s3://{self.s3_bucket}/{s3_key}"
        print(f"✅ Uploaded to {s3_uri}")
        
        return s3_uri
    
    def validate_data(self, df):
        """
        Validate data meets SageMaker requirements
        
        Args:
            df: DataFrame to validate
        
        Returns:
            bool: True if valid, raises exception otherwise
        """
        # Check required columns
        required_cols = ['item_id', 'timestamp', 'price']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Check for null values in required columns
        null_counts = df[required_cols].isnull().sum()
        if null_counts.any():
            raise ValueError(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
        
        # Check timestamp format
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            raise ValueError("timestamp column must be datetime type")
        
        # Check price is numeric
        if not pd.api.types.is_numeric_dtype(df['price']):
            raise ValueError("price column must be numeric")
        
        # Check minimum data points per item
        item_counts = df.groupby('item_id').size()
        min_points = 30  # SageMaker recommends at least 30 data points
        
        insufficient_items = item_counts[item_counts < min_points]
        if len(insufficient_items) > 0:
            print(f"⚠️  Warning: Some items have < {min_points} data points:")
            for item, count in insufficient_items.items():
                print(f"   - {item}: {count} points")
        
        print(f"✅ Data validation passed")
        print(f"   - Total rows: {len(df)}")
        print(f"   - Unique items: {df['item_id'].nunique()}")
        print(f"   - Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return True


if __name__ == '__main__':
    # Example usage
    preparer = SageMakerDataPreparer(s3_bucket='kisaanmitra-ml-data')
    
    # Sample data
    sample_data = {
        'Tomato': pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=100, freq='D'),
            'price': [45 + i * 0.5 for i in range(100)]
        }),
        'Onion': pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=100, freq='D'),
            'price': [32 + i * 0.3 for i in range(100)]
        })
    }
    
    # Prepare data
    df = preparer.prepare_training_data(sample_data)
    
    # Validate
    preparer.validate_data(df)
    
    # Upload
    s3_uri = preparer.upload_to_s3(df)
    print(f"Training data ready at: {s3_uri}")
