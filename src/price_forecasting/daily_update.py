"""
Daily Price Data Update Script
Runs every morning to check for new data and update forecasts
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from price_forecasting.price_predictor import CropPricePredictor
from price_forecasting.agmarknet_fetcher import AgMarkNetFetcher


class DailyPriceUpdater:
    """Handles daily price data updates"""
    
    def __init__(self):
        self.data_dir = Path("data/historical_prices")
        self.crops = ['Onion', 'Rice', 'Sugarcane', 'Tomato', 'Wheat']
        self.fetcher = AgMarkNetFetcher()
        
    def fetch_latest_data(self):
        """
        Fetch latest price data from AgMarkNet API
        Returns True if any data was updated
        """
        print(f"🔍 Fetching latest data from AgMarkNet API...")
        
        if not self.fetcher.api_key:
            print("⚠️ AgMarkNet API key not configured. Using existing data.")
            return False
        
        # Update all commodities
        return self.fetcher.update_all_commodities()
    
    def update_forecasts(self, crops_to_update=None):
        """Update forecasts for specified crops"""
        if crops_to_update is None:
            crops_to_update = self.crops
        
        print(f"\n🔄 Updating forecasts for {len(crops_to_update)} crops...")
        
        predictor = CropPricePredictor()
        
        for crop in crops_to_update:
            try:
                predictor.train_model(crop)
                predictor.predict_future(crop, days=30)
                print(f"✅ Updated forecast for {crop}")
            except Exception as e:
                print(f"❌ Error updating {crop}: {e}")
        
        # Save all forecasts
        predictor.save_forecasts()
        
        return True
    
    def run_daily_update(self):
        """Main daily update routine"""
        print("=" * 60)
        print(f"🌅 Daily Price Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Fetch latest data from AgMarkNet API
        data_updated = self.fetch_latest_data()
        
        if data_updated:
            print(f"\n📊 New data fetched from AgMarkNet API")
        else:
            print(f"\n📊 No new data from API. Using existing data.")
        
        # Always update forecasts (either with new data or existing)
        print("\n🔄 Updating price forecasts...")
        self.update_forecasts()
        
        print("\n✅ Daily update complete!")
        print("=" * 60)


def main():
    """Run daily update"""
    updater = DailyPriceUpdater()
    updater.run_daily_update()


if __name__ == "__main__":
    main()
