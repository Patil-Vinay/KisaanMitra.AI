# Price Forecasting System - Setup Complete ✅

## Overview
Time series forecasting system for 5 agricultural commodities using Facebook Prophet.

## Crops Covered
1. **Onion** - 1,817 historical records (2021-2026)
2. **Rice** - 1,810 historical records (2021-2026)
3. **Sugarcane** - 30 historical records (2021-2025)
4. **Tomato** - 1,817 historical records (2021-2026)
5. **Wheat** - 1,821 historical records (2021-2026)

## System Components

### 1. Price Predictor (`src/price_forecasting/price_predictor.py`)
- Loads historical CSV data
- Trains Prophet models with seasonality
- Generates 30-day forecasts
- Saves predictions to JSON files

### 2. Price API (`src/price_forecasting/price_api.py`)
- Provides easy access to forecasts
- Formats predictions for WhatsApp messages
- Supports English and Hindi
- Functions:
  - `get_today_price(crop)` - Today's prediction
  - `get_tomorrow_price(crop)` - Tomorrow's prediction
  - `get_week_forecast(crop)` - 7-day forecast
  - `format_price_message(crop, language)` - WhatsApp formatted message

### 3. Daily Updater (`src/price_forecasting/daily_update.py`)
- Checks for new data every morning
- Retrains models with updated data
- Regenerates forecasts
- Runs automatically via Task Scheduler

## Data Structure

### Input CSV Format
```csv
State,Commodity Group,Commodity,Date,Arrival Quantity,Arrival Unit,Modal Price,Price Unit
Maharashtra,Vegetables,Onion,02-03-2021,13772.00,Metric Tonnes,2279.62,Rs./Quintal
```

### Output Forecast JSON
```json
{
  "crop": "Onion",
  "generated_at": "2026-03-04T15:37:41",
  "predictions": [
    {
      "date": "2026-03-05",
      "day": "Thursday",
      "price": 190.99,
      "lower": -250.46,
      "upper": 650.98
    }
  ]
}
```

## Sample Predictions (Tomorrow - March 5, 2026)

| Crop | Predicted Price | Range |
|------|----------------|-------|
| Onion | ₹190.99/quintal | ₹-250 - ₹651 |
| Rice | ₹5,287.55/quintal | ₹4,574 - ₹6,025 |
| Sugarcane | ₹1,067.66/quintal | ₹1,061 - ₹1,074 |
| Tomato | ₹1,408.71/quintal | ₹153 - ₹2,792 |
| Wheat | ₹2,882.77/quintal | ₹2,483 - ₹3,234 |

## Daily Automation Setup

### Option 1: Windows Task Scheduler (Recommended)
```powershell
# Run as Administrator
.\scripts\setup_daily_forecast.ps1
```

This creates a scheduled task that runs every day at 6:00 AM.

### Option 2: Manual Update
```bash
python src/price_forecasting/daily_update.py
```

### Option 3: AWS EventBridge (for Lambda)
Create an EventBridge rule to trigger Lambda daily:
```json
{
  "schedule": "cron(0 6 * * ? *)",
  "target": "lambda:kisaanmitra-price-update"
}
```

## Integration with WhatsApp Bot

### Add to Lambda Handler
```python
from price_forecasting.price_api import get_price_api

# In your message handler
if "price" in user_message.lower():
    api = get_price_api()
    
    # Detect crop
    for crop in ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']:
        if crop in user_message.lower():
            response = api.format_price_message(crop, language)
            send_whatsapp_message(user_id, response)
            break
```

### Example Queries
- "What is onion price today?"
- "Tomorrow wheat price"
- "Show me rice forecast"
- "Week forecast for tomato"

## File Locations

### Data Files
- **Historical Data**: `data/historical_prices/*.csv`
- **Forecasts**: `data/forecasts/*_forecast.json`

### Source Code
- **Predictor**: `src/price_forecasting/price_predictor.py`
- **API**: `src/price_forecasting/price_api.py`
- **Updater**: `src/price_forecasting/daily_update.py`

### Scripts
- **Setup Automation**: `scripts/setup_daily_forecast.ps1`

## Updating Historical Data

### Manual Update
1. Download new CSV from AgMarkNet
2. Replace file in `data/historical_prices/`
3. Run: `python src/price_forecasting/daily_update.py`

### Automatic Update (Future Enhancement)
- Integrate with AgMarkNet API
- Fetch latest data automatically
- Append to existing CSV files

## Model Performance

### Prophet Configuration
- **Yearly Seasonality**: Enabled (captures annual patterns)
- **Weekly Seasonality**: Enabled (captures weekly market cycles)
- **Daily Seasonality**: Disabled (not relevant for daily prices)
- **Changepoint Prior Scale**: 0.05 (moderate flexibility)
- **Seasonality Prior Scale**: 10.0 (strong seasonality)

### Prediction Intervals
- **Lower Bound**: 80% confidence interval lower limit
- **Upper Bound**: 80% confidence interval upper limit
- **Predicted Price**: Most likely value (median)

## Next Steps

1. ✅ Models trained and forecasts generated
2. ⏳ Set up daily automation (run `setup_daily_forecast.ps1`)
3. ⏳ Integrate with Lambda WhatsApp bot
4. ⏳ Add price alerts for significant changes
5. ⏳ Implement AgMarkNet API integration for auto-updates

## Troubleshooting

### Prophet Installation Issues
```bash
# If Prophet fails to install
pip install pystan==2.19.1.1
pip install prophet
```

### Missing Data
- Ensure CSV files are in `data/historical_prices/`
- Check CSV format matches expected structure
- Verify date format is DD-MM-YYYY

### Forecast Not Updating
- Check Task Scheduler is running
- Verify Python path in scheduled task
- Check logs in `data/forecasts/` for errors

## API Reference

### PriceForecastAPI Methods

```python
api = get_price_api()

# Get today's price
today = api.get_today_price('onion')
# Returns: {'date': '2026-03-04', 'price': 190.99, ...}

# Get tomorrow's price
tomorrow = api.get_tomorrow_price('wheat')

# Get 7-day forecast
week = api.get_week_forecast('rice')

# Format for WhatsApp
message = api.format_price_message('tomato', 'english')
# Returns formatted WhatsApp message with emojis

# Week forecast message
week_msg = api.format_week_forecast('sugarcane', 'hindi')
```

## Maintenance

### Weekly
- Check forecast accuracy vs actual prices
- Review model performance metrics

### Monthly
- Retrain models with full historical data
- Update seasonality parameters if needed

### Quarterly
- Evaluate prediction accuracy
- Adjust model hyperparameters
- Add new crops if data available
