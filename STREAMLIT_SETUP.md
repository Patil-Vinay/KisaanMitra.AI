# Streamlit Dashboard Setup

## Issue
Streamlit is not installed on your system.

## Solution

### Install Dependencies

Open a new PowerShell window and run:

```powershell
pip install streamlit pandas plotly
```

Wait for installation to complete (may take 2-3 minutes).

### Run Dashboard

After installation:

```powershell
cd dashboard
streamlit run streamlit_app.py
```

The dashboard will open automatically in your browser at: http://localhost:8501

## What the Dashboard Shows

- 👨‍🌾 Total farmers onboarded
- 🏘️ Villages registered
- 🌾 Crops being grown
- 📏 Total land under cultivation
- 🕸️ Interactive knowledge graph network
- 📊 Detailed statistics and charts

## Optimizations Made

✅ Added caching (`@st.cache_data`) - loads data once every 30 seconds
✅ Added timeout (10 seconds) for AWS CLI calls
✅ Better error handling for slow connections

## Alternative: Check Data Directly

If dashboard is slow, check DynamoDB directly:

```powershell
# Check user profiles
aws dynamodb scan --table-name kisaanmitra-user-profiles --region ap-south-1

# Count items
aws dynamodb scan --table-name kisaanmitra-user-profiles --region ap-south-1 --select COUNT
```

## Troubleshooting

### If AWS CLI is slow:
1. Check your internet connection
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Try a different region if needed

### If Streamlit won't start:
1. Make sure Python is installed: `python --version`
2. Make sure pip is updated: `python -m pip install --upgrade pip`
3. Reinstall streamlit: `pip uninstall streamlit` then `pip install streamlit`

### If browser doesn't open:
Manually visit: http://localhost:8501

## Quick Test

After installation, test with:

```powershell
streamlit hello
```

This runs a demo app to verify Streamlit works.

## Current Status

- ✅ Dashboard code optimized with caching
- ✅ Timeout added for AWS calls
- ⏳ Installing streamlit, pandas, plotly (in progress)
- ⏳ Waiting for installation to complete

## Next Steps

1. Wait for pip installation to finish
2. Run: `cd dashboard && streamlit run streamlit_app.py`
3. Dashboard will open in browser
4. Refresh to see latest onboarded farmers
