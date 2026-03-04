"""
Price Prediction API for Lambda Integration
Provides price forecasts to the WhatsApp bot
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


class PriceForecastAPI:
    """API for accessing price forecasts"""
    
    def __init__(self, forecast_dir="data/forecasts"):
        self.forecast_dir = Path(forecast_dir)
        self.crops = {
            'onion': 'Onion',
            'rice': 'Rice', 
            'sugarcane': 'Sugarcane',
            'tomato': 'Tomato',
            'wheat': 'Wheat'
        }
    
    def get_forecast(self, crop_name):
        """Load forecast from JSON file"""
        crop_name = crop_name.lower()
        
        if crop_name not in self.crops:
            return None
        
        file_path = self.forecast_dir / f"{crop_name}_forecast.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading forecast: {e}")
            return None
    
    def get_today_price(self, crop_name):
        """Get today's predicted price"""
        forecast = self.get_forecast(crop_name)
        
        if not forecast or 'predictions' not in forecast:
            return None
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        for pred in forecast['predictions']:
            if pred['date'] == today:
                return pred
        
        # If today not found, return first prediction
        return forecast['predictions'][0] if forecast['predictions'] else None
    
    def get_tomorrow_price(self, crop_name):
        """Get tomorrow's predicted price"""
        forecast = self.get_forecast(crop_name)
        
        if not forecast or 'predictions' not in forecast:
            return None
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        for pred in forecast['predictions']:
            if pred['date'] == tomorrow:
                return pred
        
        return None
    
    def get_week_forecast(self, crop_name):
        """Get 7-day forecast"""
        forecast = self.get_forecast(crop_name)
        
        if not forecast or 'predictions' not in forecast:
            return None
        
        return forecast['predictions'][:7]
    
    def format_price_message(self, crop_name, language='english'):
        """Format price prediction as WhatsApp message"""
        today_pred = self.get_today_price(crop_name)
        tomorrow_pred = self.get_tomorrow_price(crop_name)
        
        if not today_pred:
            if language == 'english':
                return f"❌ Price forecast not available for {crop_name.title()}"
            else:
                return f"❌ {crop_name.title()} के लिए मूल्य पूर्वानुमान उपलब्ध नहीं है"
        
        crop_display = self.crops.get(crop_name.lower(), crop_name.title())
        
        if language == 'english':
            msg = f"📊 *{crop_display} Price Forecast*\n\n"
            msg += f"*Today ({today_pred['day']})*\n"
            msg += f"💰 Predicted: ₹{today_pred['price']}/quintal\n"
            msg += f"📈 Range: ₹{today_pred['lower']} - ₹{today_pred['upper']}\n\n"
            
            if tomorrow_pred:
                msg += f"*Tomorrow ({tomorrow_pred['day']})*\n"
                msg += f"💰 Predicted: ₹{tomorrow_pred['price']}/quintal\n"
                msg += f"📈 Range: ₹{tomorrow_pred['lower']} - ₹{tomorrow_pred['upper']}\n\n"
            
            # Price trend
            if tomorrow_pred:
                diff = tomorrow_pred['price'] - today_pred['price']
                if diff > 0:
                    msg += f"📈 Expected to increase by ₹{abs(diff):.2f}\n"
                elif diff < 0:
                    msg += f"📉 Expected to decrease by ₹{abs(diff):.2f}\n"
                else:
                    msg += f"➡️ Expected to remain stable\n"
            
            msg += "\n💡 Type 'week forecast' for 7-day prediction"
        else:
            msg = f"📊 *{crop_display} मूल्य पूर्वानुमान*\n\n"
            msg += f"*आज ({today_pred['day']})*\n"
            msg += f"💰 अनुमानित: ₹{today_pred['price']}/क्विंटल\n"
            msg += f"📈 सीमा: ₹{today_pred['lower']} - ₹{today_pred['upper']}\n\n"
            
            if tomorrow_pred:
                msg += f"*कल ({tomorrow_pred['day']})*\n"
                msg += f"💰 अनुमानित: ₹{tomorrow_pred['price']}/क्विंटल\n"
                msg += f"📈 सीमा: ₹{tomorrow_pred['lower']} - ₹{tomorrow_pred['upper']}\n\n"
            
            # Price trend
            if tomorrow_pred:
                diff = tomorrow_pred['price'] - today_pred['price']
                if diff > 0:
                    msg += f"📈 ₹{abs(diff):.2f} की वृद्धि की उम्मीद\n"
                elif diff < 0:
                    msg += f"📉 ₹{abs(diff):.2f} की कमी की उम्मीद\n"
                else:
                    msg += f"➡️ स्थिर रहने की उम्मीद\n"
            
            msg += "\n💡 7-दिन के पूर्वानुमान के लिए 'week forecast' टाइप करें"
        
        return msg
    
    def format_week_forecast(self, crop_name, language='english'):
        """Format 7-day forecast as WhatsApp message"""
        week_data = self.get_week_forecast(crop_name)
        
        if not week_data:
            if language == 'english':
                return f"❌ Weekly forecast not available for {crop_name.title()}"
            else:
                return f"❌ {crop_name.title()} के लिए साप्ताहिक पूर्वानुमान उपलब्ध नहीं है"
        
        crop_display = self.crops.get(crop_name.lower(), crop_name.title())
        
        if language == 'english':
            msg = f"📅 *{crop_display} - 7 Day Forecast*\n\n"
            for pred in week_data:
                msg += f"*{pred['day']}, {pred['date']}*\n"
                msg += f"₹{pred['price']}/quintal (₹{pred['lower']}-₹{pred['upper']})\n\n"
        else:
            msg = f"📅 *{crop_display} - 7 दिन का पूर्वानुमान*\n\n"
            for pred in week_data:
                msg += f"*{pred['day']}, {pred['date']}*\n"
                msg += f"₹{pred['price']}/क्विंटल (₹{pred['lower']}-₹{pred['upper']})\n\n"
        
        return msg


# Singleton instance for Lambda
_api_instance = None

def get_price_api():
    """Get or create API instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = PriceForecastAPI()
    return _api_instance
