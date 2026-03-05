# 🔍 Why the SageMaker Endpoint Failed

## The Root Cause

The endpoint failed because of an **input format mismatch** between what we sent and what the SageMaker AutoML time series model expected.

---

## The Error

```
KeyError: 'start'
RuntimeError: Failed to generate forecasts
```

This error appeared in CloudWatch logs every time we tried to invoke the endpoint.

---

## What We Tried to Send

### Attempt 1: Simple Format
```python
{
    "instances": [
        {
            "item_id": "tomato",
            "timestamp": "2026-03-05"
        }
    ]
}
```
**Result**: ❌ `KeyError: 'start'`

### Attempt 2: With Historical Data
```python
{
    "instances": [
        {
            "start": "2021-03-02",
            "target": [872.62, 996.72, 1123.45, ...],  # 1817 prices
            "item_id": "tomato"
        }
    ],
    "configuration": {
        "num_samples": 100,
        "output_types": ["mean", "quantiles"],
        "quantiles": ["0.1", "0.5", "0.9"]
    }
}
```
**Result**: ❌ Still `KeyError: 'start'`

---

## Why It Failed

### 1. Training vs Inference Format Mismatch

**How the model was trained**:
```csv
item_id,timestamp,price
Onion,2025-03-05 18:53:18,50.0
Onion,2025-03-06 18:53:18,50.1
Tomato,2025-03-05 18:53:18,872.62
Tomato,2025-03-06 18:53:18,996.72
```
- Format: CSV with 3 columns
- Multiple rows per item
- Timestamp format: `YYYY-MM-DD HH:MM:SS`

**What inference expects** (we thought):
```json
{
    "instances": [{
        "start": "2021-03-02",
        "target": [872.62, 996.72, ...],
        "item_id": "tomato"
    }]
}
```
- Format: JSON with nested structure
- Single object per item
- Different field names

**The Problem**: SageMaker AutoML creates a custom inference container that expects a specific format based on how it was trained. This format is NOT well-documented and varies by:
- Training data format
- AutoML version
- Time series configuration
- Model type selected

### 2. The 'start' Field Mystery

The error `KeyError: 'start'` means the model's inference code is looking for a field called `'start'` but can't find it in the format we're sending.

**Possible reasons**:
1. The field name might need to be different (e.g., `'timestamp'`, `'date'`, `'time'`)
2. The field might need to be in a different location in the JSON structure
3. The model might expect CSV format, not JSON
4. The model might need additional metadata fields

### 3. SageMaker AutoML Time Series Complexity

SageMaker AutoML for time series is particularly complex because:

**Training Phase**:
- Accepts CSV with `item_id`, `timestamp`, `target`
- Automatically handles data preprocessing
- Creates custom inference container
- Doesn't document the exact inference format

**Inference Phase**:
- Expects data in a format that matches the internal model structure
- Format is NOT the same as training format
- Format is NOT well-documented in AWS docs
- Format varies by model type (ARIMA, ETS, DeepAR, Prophet, CNN-QR, NPTS)

---

## What the Logs Showed

```python
File "/opt/amazon/lib/python3.8/site-packages/gluonts/dataset/common.py", line 292
    data[self.name] = _as_period(data[self.name], self.freq)
KeyError: 'start'
```

This shows:
1. The model uses **GluonTS** library internally
2. GluonTS expects a specific data structure
3. The `_as_period` function is trying to access `data['start']`
4. Our data doesn't have this field in the expected location

---

## Why This Is Hard to Fix

### 1. Undocumented Format
AWS documentation for SageMaker AutoML time series inference is incomplete. The exact format depends on:
- Which algorithm was selected (our model used ensemble)
- How the training data was structured
- Internal GluonTS requirements

### 2. Multiple Possible Formats

SageMaker AutoML time series might expect:

**Option A: GluonTS JSON Format**
```json
{
    "instances": [
        {
            "start": "2021-03-02T00:00:00",
            "target": [872.62, 996.72, ...],
            "feat_static_cat": [0],
            "item_id": "tomato"
        }
    ]
}
```

**Option B: CSV Format**
```csv
item_id,timestamp,target
tomato,2021-03-02,872.62
tomato,2021-03-03,996.72
...
```

**Option C: Parquet Format**
Binary format with specific schema

**Option D: Custom Format**
Model-specific format based on training configuration

### 3. Trial and Error Required

To fix this, we would need to:
1. Read GluonTS documentation thoroughly
2. Examine the model's inference container code
3. Try dozens of different format variations
4. Check CloudWatch logs after each attempt
5. Potentially contact AWS support

**Estimated time**: 4-8 hours of debugging

---

## Why Real-time Endpoints Are Problematic

### 1. Cost
- **Hourly cost**: ₹4-5/hour
- **Monthly cost**: ₹3,000-3,600/month
- **Cost while debugging**: Wasted money

### 2. Complexity
- Custom inference containers
- Undocumented formats
- Model-specific requirements
- Version dependencies

### 3. Overkill for Our Use Case
- We don't need real-time predictions
- Forecasts are updated daily/weekly
- Batch processing is sufficient

---

## Better Alternatives

### Option 1: Batch Transform (Recommended for SageMaker)
**How it works**:
- Upload input CSV to S3
- Create transform job
- Model processes entire file
- Download results from S3

**Advantages**:
- ✅ Uses same format as training (CSV)
- ✅ No format conversion needed
- ✅ Pay per use (~₹10-20 per run)
- ✅ No ongoing costs
- ✅ Easier to debug

**Disadvantages**:
- ❌ Takes 10-30 minutes to run
- ❌ Not real-time (but we don't need real-time)

### Option 2: Statistical Method (Current)
**How it works**:
- Load historical data from S3
- Calculate trends and patterns
- Generate forecasts directly
- Store in DynamoDB

**Advantages**:
- ✅ Instant results
- ✅ Free (no ML costs)
- ✅ Uses all 5 years of data
- ✅ Easy to understand and debug
- ✅ No format issues

**Disadvantages**:
- ❌ Simpler than ML models
- ❌ May miss complex patterns

---

## Technical Deep Dive

### What GluonTS Expects

GluonTS (the library SageMaker uses internally) expects data in this format:

```python
from gluonts.dataset.common import ListDataset

# Training format
train_ds = ListDataset(
    [
        {
            "start": pd.Timestamp("2021-03-02", freq='D'),
            "target": [872.62, 996.72, 1123.45, ...],
            "item_id": "tomato"
        }
    ],
    freq="D"
)

# Inference format (for forecasting)
test_ds = ListDataset(
    [
        {
            "start": pd.Timestamp("2021-03-02", freq='D'),
            "target": [872.62, 996.72, ...],  # Historical data
            "item_id": "tomato"
        }
    ],
    freq="D"
)
```

**Key requirements**:
1. `start` must be a pandas Timestamp object (not string)
2. `target` must be a list of numbers
3. `freq` must match training frequency
4. All fields must be present

**The problem**: When sending JSON to the endpoint, we can't send pandas Timestamp objects. We send strings, and the model's inference code doesn't convert them properly.

### The Inference Container

SageMaker AutoML creates a custom Docker container for inference:

```
Container: 179163482248.dkr.ecr.ap-south-1.amazonaws.com/autopilot-timeseries:latest
```

This container:
1. Receives HTTP POST request with JSON/CSV data
2. Converts input to GluonTS format
3. Runs model prediction
4. Converts output back to JSON/CSV
5. Returns HTTP response

**The bug**: Step 2 (input conversion) is failing because our JSON format doesn't match what the container expects.

---

## Could We Fix It?

### Yes, but it would require:

1. **Reading the container code** (if available)
2. **Testing many format variations**:
   ```python
   # Try 1: ISO format
   "start": "2021-03-02T00:00:00"
   
   # Try 2: Unix timestamp
   "start": 1614643200
   
   # Try 3: Different field name
   "timestamp": "2021-03-02"
   
   # Try 4: Nested structure
   "data": {"start": "2021-03-02", "target": [...]}
   
   # Try 5: CSV instead of JSON
   # ... and so on
   ```

3. **Checking logs after each attempt**
4. **Potentially modifying the inference container** (advanced)
5. **Or contacting AWS support** (slow)

**Estimated effort**: 4-8 hours
**Success probability**: 60-70%
**Cost during debugging**: ₹20-40

---

## Conclusion

### Why It Failed
The endpoint failed because SageMaker AutoML time series models use a complex, undocumented inference format that doesn't match the training format. The specific error (`KeyError: 'start'`) indicates the model expects a field we're not providing in the correct format.

### Why We Deleted It
- Costing money while not working
- Would take hours to debug
- We have a working alternative (statistical method)
- Batch Transform is a better option if we need SageMaker

### What We Learned
- Real-time endpoints are complex and expensive
- SageMaker AutoML inference formats are not well-documented
- Batch Transform is easier and cheaper for non-real-time use cases
- Statistical methods can work well with good historical data

### Recommendation
- Keep using statistical method (working, free)
- If need better accuracy: Implement Batch Transform
- Don't recreate real-time endpoint unless absolutely necessary

---

## References

### AWS Documentation Issues
- [SageMaker AutoML Time Series](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-timeseries.html) - Doesn't document inference format
- [GluonTS Documentation](https://ts.gluon.ai/) - Shows Python format, not HTTP API format
- [SageMaker Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html) - Generic, not AutoML-specific

### Similar Issues
- Many developers face this issue with SageMaker AutoML time series
- Common workaround: Use Batch Transform instead
- AWS support often needed for complex inference formats

