"""
AgMarkNet API Data Fetcher
Fetches latest commodity price data from AgMarkNet API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os


class AgMarkNetFetcher:
    """Fetches commodity price data from AgMarkNet API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('AGMARKNET_API_KEY', '')
        self.base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        
        # Commodity mapping
        self.commodities = {
            'Onion': 'Onion',
            'Rice': 'Rice',
            'Sugarcane': 'Sugarcane',
            'Tomato': 'Tomato',
            'Wheat': 'Wheat'
        }
        
        self.data_dir = Path("data/historical_prices")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_latest_data(self, commodity, days=7):
        """
        Fetch latest price data for a commodity
        
        Args:
            commodity: Commodity name (Onion, Rice, etc.)
            days: Number of days to fetch (default 7)
        
        Returns:
            DataFrame with latest price data
        """
        if not self.api_key:
            print("⚠️ AgMarkNet API key not found. Set AGMARKNET_API_KEY environment variable.")
            return None
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API
        start_str = start_date.strftime('%d-%m-%Y')
        end_str = end_date.strftime('%d-%m-%Y')
        
        print(f"📡 Fetching {commodity} data from {start_str} to {end_str}...")
        
        # API parameters
        params = {
            'api-key': self.api_key,
            'format': 'json',
            'filters[commodity]': commodity,
            'filters[state]': 'Maharashtra',
            'limit': 1000
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'records' not in data or not data['records']:
                print(f"⚠️ No data found for {commodity}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data['records'])
            
            # Filter by date range
            df['date'] = pd.to_datetime(df['arrival_date'], format='%d/%m/%Y', errors='coerce')
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            print(f"✅ Fetched {len(df)} records for {commodity}")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data: {e}")
            return None
        except Exception as e:
            print(f"❌ Error processing data: {e}")
            return None
    
    def update_csv_file(self, commodity):
        """
        Update CSV file with latest data from API
        
        Args:
            commodity: Commodity name
        
        Returns:
            True if updated, False otherwise
        """
        csv_path = self.data_dir / f"{commodity}.csv"
        
        # Fetch latest data
        new_data = self.fetch_latest_data(commodity, days=7)
        
        if new_data is None or len(new_data) == 0:
            print(f"⚠️ No new data to update for {commodity}")
            return False
        
        # Read existing CSV
        if csv_path.exists():
            try:
                # Read existing data (skip header row)
                existing_df = pd.read_csv(csv_path, skiprows=1)
                
                # Get last date in existing data
                existing_df['Date'] = pd.to_datetime(existing_df['Date'], format='%d-%m-%Y', errors='coerce')
                last_date = existing_df['Date'].max()
                
                print(f"📅 Last date in CSV: {last_date.strftime('%d-%m-%Y')}")
                
                # Filter new data to only include dates after last_date
                new_data = new_data[new_data['date'] > last_date]
                
                if len(new_data) == 0:
                    print(f"✅ {commodity} CSV is already up to date")
                    return False
                
                # Format new data to match CSV structure
                new_rows = []
                for _, row in new_data.iterrows():
                    new_rows.append({
                        'State': 'Maharashtra',
                        'Commodity Group': 'Vegetables' if commodity in ['Onion', 'Tomato'] else 'Foodgrains',
                        'Commodity': commodity,
                        'Date': row['date'].strftime('%d-%m-%Y'),
                        'Arrival Quantity 02-03-2021 to 02-03-2026': row.get('arrivals', 0),
                        'Arrival Unit': 'Metric Tonnes',
                        'Modal Price 02-03-2021 to 02-03-2026': row.get('modal_price', 0),
                        'Price Unit': 'Rs./Quintal'
                    })
                
                # Append to existing CSV
                new_df = pd.DataFrame(new_rows)
                new_df.to_csv(csv_path, mode='a', header=False, index=False)
                
                print(f"✅ Added {len(new_rows)} new records to {commodity}.csv")
                return True
                
            except Exception as e:
                print(f"❌ Error updating CSV: {e}")
                return False
        else:
            print(f"⚠️ CSV file not found: {csv_path}")
            return False
    
    def update_all_commodities(self):
        """Update all commodity CSV files"""
        print("=" * 60)
        print(f"🔄 AgMarkNet Data Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        updated_count = 0
        
        for commodity in self.commodities.keys():
            if self.update_csv_file(commodity):
                updated_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Updated {updated_count} out of {len(self.commodities)} commodities")
        print("=" * 60)
        
        return updated_count > 0


def main():
    """Main function to update data"""
    fetcher = AgMarkNetFetcher()
    
    # Check if API key is available
    if not fetcher.api_key:
        print("⚠️ AgMarkNet API key not configured")
        print("Set environment variable: AGMARKNET_API_KEY")
        print("\nFor now, using existing CSV files...")
        return
    
    # Update all commodities
    fetcher.update_all_commodities()


if __name__ == "__main__":
    main()
