#!/usr/bin/env python3
"""
Direct test of price forecasting engine
"""

import sys
import os

# Add Lambda path
sys.path.insert(0, 'src/lambda')

from price_forecasting import forecasting_engine, format_forecast_response

def test_forecasting():
    """Test the forecasting engine"""
    
    print("=" * 60)
    print("🔮 PRICE FORECASTING ENGINE TEST")
    print("=" * 60)
    
    # Test crops
    test_cases = [
        ("Sugarcane", "Maharashtra", "hindi"),
        ("Onion", "Maharashtra", "english"),
        ("Wheat", "Maharashtra", "hindi")
    ]
    
    for crop, state, language in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {crop} in {state} ({language})")
        print(f"{'='*60}\n")
        
        try:
            # Get forecast
            forecast = forecasting_engine.get_complete_forecast(crop, state, language)
            
            if forecast:
                print("✅ Forecast generated successfully!")
                print(f"\nRaw forecast data:")
                print(f"  Current Price: ₹{forecast['current_price']}")
                print(f"  7-Day Forecast: ₹{forecast.get('forecast_7d', 'N/A')}")
                print(f"  Trend: {forecast['trend']} {forecast['trend_emoji']}")
                print(f"  Supply: {forecast['supply_signal']}")
                print(f"  Demand: {forecast['demand_signal']}")
                print(f"  Confidence: {forecast['confidence']}")
                print(f"  Recommendation: {forecast['recommendation']}")
                print(f"  Data Points: {forecast['data_points']}")
                
                # Format for user
                print(f"\n{'='*60}")
                print("Formatted User Message:")
                print(f"{'='*60}")
                message = format_forecast_response(forecast, language)
                print(message)
                
            else:
                print("❌ Forecast generation failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n")

if __name__ == "__main__":
    test_forecasting()
