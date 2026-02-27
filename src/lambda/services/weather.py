"""
Weather-Aware Smart Recommendations
"""
import urllib3
import json
import os

http = urllib3.PoolManager()

def get_weather_forecast(location):
    """Get weather forecast (simplified - uses mock data if API not available)"""
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    
    if not api_key or api_key == 'not_available':
        print("[WEATHER] API key not available, using mock data")
        return get_mock_weather(location)
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={location},IN&appid={api_key}&units=metric"
        response = http.request('GET', url, timeout=3.0)
        
        if response.status == 200:
            return json.loads(response.data)
        else:
            return get_mock_weather(location)
    except Exception as e:
        print(f"[WEATHER] Error fetching weather: {e}")
        return get_mock_weather(location)

def get_mock_weather(location):
    """Mock weather data for testing"""
    return {
        'city': {'name': location},
        'list': [
            {
                'main': {'temp': 28, 'humidity': 65},
                'weather': [{'main': 'Clear', 'description': 'clear sky'}],
                'rain': None
            }
        ] * 8
    }

def analyze_weather_for_farming(forecast):
    """Analyze weather for farming decisions"""
    if not forecast or 'list' not in forecast:
        return {
            'rain_expected': False,
            'days_until_rain': 0,
            'max_temp': 30,
            'min_temp': 20,
            'recommendations': []
        }
    
    forecasts = forecast['list'][:24]  # Next 3 days
    
    rain_coming = False
    days_until_rain = 0
    max_temp = 0
    min_temp = 100
    
    for i, f in enumerate(forecasts):
        temp = f['main']['temp']
        max_temp = max(max_temp, temp)
        min_temp = min(min_temp, temp)
        
        if f.get('rain') and not rain_coming:
            rain_coming = True
            days_until_rain = i // 8
    
    recommendations = []
    
    if rain_coming and days_until_rain <= 1:
        recommendations.append("⚠️ 24 घंटे में बारिश संभव - अभी कीटनाशक स्प्रे करें!")
    
    if max_temp > 38:
        recommendations.append("🌡️ अत्यधिक गर्मी - सिंचाई बढ़ाएं")
    
    if min_temp < 12:
        recommendations.append("❄️ ठंड - फसल को ढकें")
    
    if not recommendations:
        recommendations.append("✅ मौसम अनुकूल है")
    
    return {
        'rain_expected': rain_coming,
        'days_until_rain': days_until_rain,
        'max_temp': int(max_temp),
        'min_temp': int(min_temp),
        'recommendations': recommendations
    }

def format_weather_response(location, analysis):
    """Format weather response"""
    message = f"\n\n🌤️ *मौसम पूर्वानुमान - {location}*\n"
    message += f"🌡️ तापमान: {analysis['min_temp']}°C - {analysis['max_temp']}°C\n"
    
    if analysis['rain_expected']:
        message += f"🌧️ बारिश: {analysis['days_until_rain']} दिन में\n"
    else:
        message += "☀️ बारिश: अगले 3 दिन में नहीं\n"
    
    message += "\n*🌾 कृषि सलाह*:\n"
    for rec in analysis['recommendations']:
        message += f"• {rec}\n"
    
    return message
