"""Weekly price forecast job.

Reads the 5 year mandi price history for each crop from S3, makes a
30 day forecast and stores it in DynamoDB, where forecast_reply.py reads it.

FORECAST_METHOD:
  trend  - recent average plus linear trend (default, no extra libraries)
  automl - starts a SageMaker AutoML training job and returns
  batch  - runs batch transform with an already trained model
"""
import csv
import io
import json
import os
import statistics
import sys
import traceback
from datetime import datetime, timedelta
from decimal import Decimal

import boto3
import urllib3

sys.path.insert(0, '/opt/python')
sys.path.insert(0, os.path.dirname(__file__))

S3_BUCKET = os.environ.get('S3_BUCKET', 'kisaanmitra-ml-data')
SAGEMAKER_ROLE_ARN = os.environ.get('SAGEMAKER_ROLE_ARN')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'kisaanmitra-price-forecasts')
FORECAST_METHOD = os.environ.get('FORECAST_METHOD', 'trend').lower()
MODEL_NAME = os.environ.get('SAGEMAKER_MODEL_NAME', 'kisaanmitra-forecast-model')
AGMARKNET_API_KEY = os.environ.get('AGMARKNET_API_KEY', '')

# same crops the bot answers for (general_agent.py)
CROPS = ['Onion', 'Rice', 'Sugarcane', 'Tomato', 'Wheat']
FORECAST_DAYS = 30
TREND_WINDOW = 90

s3 = boto3.client('s3', region_name='ap-south-1')
table = boto3.resource('dynamodb', region_name='ap-south-1').Table(DYNAMODB_TABLE)


def load_history(crop):
    """Returns [(date, price)] sorted by date from historical-prices/<crop>.csv"""
    key = f"historical-prices/{crop}.csv"
    body = s3.get_object(Bucket=S3_BUCKET, Key=key)['Body'].read().decode('utf-8')

    # first line is the report title, second is the header
    lines = body.splitlines()[1:]
    rows = []
    for r in csv.DictReader(lines):
        price_col = next((k for k in r if k and k.startswith('Modal Price')), None)
        try:
            d = datetime.strptime(r['Date'], '%d-%m-%Y').date()
            p = float(r[price_col])
        except (TypeError, ValueError, KeyError):
            continue  # footer lines
        rows.append((d, p))

    rows.sort()
    print(f"  {crop}: {len(rows)} days ({rows[0][0]} to {rows[-1][0]})" if rows else f"  {crop}: no rows")
    return rows


def fetch_latest(crop, days=7):
    """Recent modal prices from data.gov.in, if a key is set."""
    if not AGMARKNET_API_KEY:
        return []

    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    fields = {
        'api-key': AGMARKNET_API_KEY,
        'format': 'json',
        'filters[commodity]': crop,
        'filters[state]': 'Maharashtra',
        'limit': '100',
    }
    try:
        resp = urllib3.PoolManager().request('GET', url, fields=fields, timeout=10.0)
        records = json.loads(resp.data.decode('utf-8')).get('records', [])
    except Exception as e:
        print(f"  AgMarkNet error for {crop}: {e}")
        return []

    cutoff = datetime.now().date() - timedelta(days=days)
    rows = []
    for rec in records:
        try:
            d = datetime.strptime(rec['arrival_date'], '%d/%m/%Y').date()
            p = float(rec['modal_price'])
        except (KeyError, ValueError):
            continue
        if d >= cutoff:
            rows.append((d, p))
    print(f"  {crop}: {len(rows)} new rows from AgMarkNet")
    return rows


def merge(history, latest):
    by_date = dict(history)
    by_date.update(dict(latest))  # newer value wins
    return sorted(by_date.items())


def trend_forecast(history):
    """Average of the last 90 days plus the daily trend over that window."""
    recent = [p for _, p in history[-TREND_WINDOW:]]
    avg = statistics.mean(recent)
    std = statistics.stdev(recent) if len(recent) > 1 else 0
    trend = (recent[-1] - recent[0]) / len(recent)

    start = datetime.now() + timedelta(days=1)
    out = []
    for i in range(FORECAST_DAYS):
        day = start + timedelta(days=i)
        price = avg + trend * i
        if day.weekday() >= 5:
            price *= 0.98  # weekend arrivals are lower

        lower = max(price - 1.5 * std, 5)
        price = max(price, 10)
        upper = max(price + 1.5 * std, price * 1.1)
        out.append(forecast_row(day, price, lower, upper))
    return out


def forecast_row(day, price, lower, upper):
    # format read by forecast_reply.py; DynamoDB needs Decimal, not float
    return {
        'date': day.strftime('%Y-%m-%d'),
        'day': day.strftime('%A'),
        'price': Decimal(str(round(price, 2))),
        'lower': Decimal(str(round(lower, 2))),
        'upper': Decimal(str(round(upper, 2))),
    }


def store_forecasts(forecasts_by_crop, model, records_by_crop=None):
    stored = 0
    for crop, forecasts in forecasts_by_crop.items():
        item = {
            'commodity': crop.lower(),
            'forecasts': forecasts,
            'model': model,
            'last_updated': datetime.now().isoformat(),
        }
        if records_by_crop:
            item['training_records'] = records_by_crop.get(crop, 0)
        try:
            table.put_item(Item=item)
            stored += 1
            print(f"  stored {len(forecasts)} days for {crop}")
        except Exception as e:
            print(f"  failed to store {crop}: {e}")
    return stored


def to_dataframe(history_by_crop):
    # data_preparer wants {crop: DataFrame(date, price)}
    import pandas as pd
    return {
        crop: pd.DataFrame({
            'date': pd.to_datetime([d for d, _ in rows]),
            'price': [p for _, p in rows],
        })
        for crop, rows in history_by_crop.items()
    }


def run_sagemaker(history_by_crop):
    from sagemaker_forecasting.data_preparer import SageMakerDataPreparer
    from sagemaker_forecasting.automl_trainer import SageMakerAutoMLTrainer
    from sagemaker_forecasting.batch_predictor import SageMakerBatchPredictor

    preparer = SageMakerDataPreparer(s3_bucket=S3_BUCKET)
    train_df = preparer.prepare_training_data(to_dataframe(history_by_crop))
    preparer.validate_data(train_df)
    train_uri = preparer.upload_to_s3(train_df, filename='train.csv')

    if FORECAST_METHOD == 'automl':
        # job names are limited to 32 chars
        job_name = f"km-{datetime.now().strftime('%y%m%d%H%M%S')}"
        SageMakerAutoMLTrainer(role_arn=SAGEMAKER_ROLE_ARN).create_forecasting_job(
            job_name=job_name,
            train_s3_uri=train_uri,
            output_s3_uri=f"s3://{S3_BUCKET}/sagemaker-forecasting/output",
            forecast_horizon=FORECAST_DAYS,
            forecast_frequency='D',
        )
        # training takes 1-2 hours, so we don't wait here
        return {'statusCode': 202, 'body': json.dumps({'training_job': job_name})}

    predictor = SageMakerBatchPredictor()
    input_uri = preparer.upload_to_s3(train_df.groupby('item_id').tail(1), filename='inference_input.csv')
    job_name = f"km-tr-{datetime.now().strftime('%y%m%d%H%M%S')}"
    predictor.create_transform_job(
        job_name=job_name,
        model_name=MODEL_NAME,
        input_s3_uri=input_uri,
        output_s3_uri=f"s3://{S3_BUCKET}/sagemaker-forecasting/predictions/",
    )
    predictor.wait_for_transform_job(job_name, max_wait_time=800)

    preds = predictor.get_predictions(None, S3_BUCKET, 'sagemaker-forecasting/predictions/inference_input.csv.out')
    forecasts = predictor.format_predictions_for_dynamodb(preds)
    stored = store_forecasts(forecasts, 'sagemaker_automl')
    return {'statusCode': 200, 'body': json.dumps({'method': 'batch', 'stored': stored})}


def lambda_handler(event, context):
    print(f"Forecast run {datetime.now().isoformat()} method={FORECAST_METHOD}")

    try:
        history = {}
        for crop in CROPS:
            try:
                rows = merge(load_history(crop), fetch_latest(crop))
            except Exception as e:
                print(f"  skipping {crop}: {e}")
                continue
            if len(rows) >= 30:
                history[crop] = rows
            else:
                print(f"  skipping {crop}: only {len(rows)} rows")

        if not history:
            raise RuntimeError("no price history loaded from S3")

        if FORECAST_METHOD in ('automl', 'batch'):
            return run_sagemaker(history)

        forecasts = {crop: trend_forecast(rows) for crop, rows in history.items()}
        records = {crop: len(rows) for crop, rows in history.items()}
        stored = store_forecasts(forecasts, 'Statistical Trend Analysis', records)
        return {
            'statusCode': 200,
            'body': json.dumps({'method': 'trend', 'crops': list(history), 'stored': stored}),
        }

    except Exception as e:
        traceback.print_exc()
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


if __name__ == '__main__':
    print(json.dumps(lambda_handler({}, None), indent=2))
