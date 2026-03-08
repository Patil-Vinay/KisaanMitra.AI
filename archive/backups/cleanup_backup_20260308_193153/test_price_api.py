"""Quick test of Price Forecasting API"""

from src.price_forecasting.price_api import get_price_api

# Get API instance
api = get_price_api()

print("=" * 60)
print("Testing Price Forecasting API")
print("=" * 60)

# Test each crop
crops = ['onion', 'rice', 'sugarcane', 'tomato', 'wheat']

for crop in crops:
    print(f"\n{crop.upper()}:")
    print("-" * 40)
    
    # English message
    msg_en = api.format_price_message(crop, 'english')
    print(msg_en)
    print()

print("\n" + "=" * 60)
print("Week Forecast Example (Wheat)")
print("=" * 60)
week_msg = api.format_week_forecast('wheat', 'english')
print(week_msg)
