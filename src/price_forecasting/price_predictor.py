"""
Time Series Price Forecasting for Agricultural Commodities
Uses Prophet for robust forecasting with seasonality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️ Prophet not installed. Install with: pip install prophet")


class CropPricePredictor:
    """Forecasts crop prices using historical data"""
    
    def __init__(self, data_dir="data/historical_prices"):
        self.data_dir = Path(data_dir)
        self.models = {}
        self.crops = ['Onion', 'Rice', 'Sugarcane', 'Tomato', 'Wheat']
        self.forecasts = {}
        
    def load_data(self, crop_name):
        """Load historical price data for a crop"""
        file_path = self.data_dir / f"{crop_name}.csv"
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        # Read CSV, skip first row (header info)
        df = pd.read_csv(file_path, skiprows=1)
        
        # Clean and prepare data
        df = df[['Date', 'Modal Price 02-03-2021 to 02-03-2026']].copy()
        df.columns = ['ds', 'y']  # Prophet requires 'ds' and 'y' columns
        
        # Convert date and price
        df['ds'] = pd.to_datetime(df['ds'], format='%d-%m-%Y')
        df['y'] = pd.to_numeric(df['y'], errors='coerce')
        
        # Remove NaN values
        df = df.dropna()
        
        # Sort by date
        df = df.sort_values('ds').reset_index(drop=True)
        
        print(f"✅ Loaded {len(df)} records for {crop_name}")
        print(f"   Date range: {df['ds'].min()} to {df['ds'].max()}")
        print(f"   Price range: ₹{df['y'].min():.2f} to ₹{df['y'].max():.2f} per quintal")
        
        return df
    
    def train_model(self, crop_name, df=None):
        """Train Prophet model for a crop"""
        if not PROPHET_AVAILABLE:
            print("❌ Prophet not available")
            return None
        
        if df is None:
            df = self.load_data(crop_name)
        
        if df is None or len(df) < 30:
            print(f"❌ Insufficient data for {crop_name}")
            return None
        
        print(f"\n🔧 Training model for {crop_name}...")
        
        # Create and configure Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,  # Flexibility in trend changes
            seasonality_prior_scale=10.0,   # Strength of seasonality
        )
        
        # Fit model
        model.fit(df)
        
        self.models[crop_name] = model
        print(f"✅ Model trained for {crop_name}")
        
        return model
    
    def predict_future(self, crop_name, days=30):
        """Predict prices for next N days"""
        if crop_name not in self.models:
            print(f"⚠️ Model not trained for {crop_name}, training now...")
            self.train_model(crop_name)
        
        if crop_name not in self.models:
            return None
        
        model = self.models[crop_name]
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=days)
        
        # Make predictions
        forecast = model.predict(future)
        
        # Get only future predictions
        last_date = forecast['ds'].max() - timedelta(days=days)
        future_forecast = forecast[forecast['ds'] > last_date].copy()
        
        # Store forecast
        self.forecasts[crop_name] = future_forecast
        
        return future_forecast
    
    def get_price_prediction(self, crop_name, date=None):
        """Get price prediction for a specific date"""
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = pd.to_datetime(date)
        
        if crop_name not in self.forecasts:
            self.predict_future(crop_name)
        
        if crop_name not in self.forecasts:
            return None
        
        forecast = self.forecasts[crop_name]
        
        # Find closest date
        forecast['date_diff'] = abs((forecast['ds'] - date).dt.days)
        closest = forecast.loc[forecast['date_diff'].idxmin()]
        
        return {
            'crop': crop_name,
            'date': closest['ds'].strftime('%Y-%m-%d'),
            'predicted_price': round(closest['yhat'], 2),
            'lower_bound': round(closest['yhat_lower'], 2),
            'upper_bound': round(closest['yhat_upper'], 2),
            'unit': 'Rs./Quintal'
        }
    
    def get_weekly_forecast(self, crop_name):
        """Get 7-day price forecast"""
        if crop_name not in self.forecasts:
            self.predict_future(crop_name, days=7)
        
        if crop_name not in self.forecasts:
            return None
        
        forecast = self.forecasts[crop_name].head(7)
        
        return [{
            'date': row['ds'].strftime('%Y-%m-%d'),
            'day': row['ds'].strftime('%A'),
            'price': round(row['yhat'], 2),
            'lower': round(row['yhat_lower'], 2),
            'upper': round(row['yhat_upper'], 2)
        } for _, row in forecast.iterrows()]
    
    def train_all_models(self):
        """Train models for all crops"""
        print("=" * 60)
        print("🚀 Training Price Forecasting Models")
        print("=" * 60)
        
        for crop in self.crops:
            self.train_model(crop)
        
        print("\n" + "=" * 60)
        print(f"✅ Trained {len(self.models)} models")
        print("=" * 60)
    
    def save_forecasts(self, output_dir="data/forecasts"):
        """Save forecasts to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for crop in self.crops:
            if crop not in self.forecasts:
                self.predict_future(crop, days=30)
            
            if crop in self.forecasts:
                forecast_data = {
                    'crop': crop,
                    'generated_at': datetime.now().isoformat(),
                    'predictions': self.get_weekly_forecast(crop)
                }
                
                file_path = output_path / f"{crop.lower()}_forecast.json"
                with open(file_path, 'w') as f:
                    json.dump(forecast_data, f, indent=2)
                
                print(f"💾 Saved forecast for {crop} to {file_path}")


def main():
    """Main function to train models and generate forecasts"""
    predictor = CropPricePredictor()
    
    # Train all models
    predictor.train_all_models()
    
    # Generate and save forecasts
    print("\n📊 Generating 30-day forecasts...")
    predictor.save_forecasts()
    
    # Show sample predictions
    print("\n" + "=" * 60)
    print("📈 Sample Predictions for Tomorrow")
    print("=" * 60)
    
    tomorrow = datetime.now() + timedelta(days=1)
    for crop in predictor.crops:
        prediction = predictor.get_price_prediction(crop, tomorrow)
        if prediction:
            print(f"\n{crop}:")
            print(f"  Predicted Price: ₹{prediction['predicted_price']}/quintal")
            print(f"  Range: ₹{prediction['lower_bound']} - ₹{prediction['upper_bound']}")


if __name__ == "__main__":
    main()
