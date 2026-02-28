"""
Weather-Aware Smart Recommendations
"""
import urllib3
import json
import os
from datetime import datetime

http = urllib3.PoolManager()

def get_weather_forecast(location):
    """Get weather forecast from OpenWeather API"""
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    
    print(f"[WEATHER] API key present: {bool(api_key)}, Length: {len(api_key) if api_key else 0}")
    
    if not api_key or api_key == 'not_available' or len(api_key) < 10:
        print("[WEATHER] API key not available, using mock data")
        return get_mock_weather(location)
    
    try:
        # Clean location name (remove extra words like "weather in")
        location_clean = location.lower().replace('weather in', '').replace('weather', '').strip()
        if not location_clean:
            location_clean = location
        
        print(f"[WEATHER] Fetching weather for: {location_clean}")
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={location_clean},IN&appid={api_key}&units=metric"
        response = http.request('GET', url, timeout=5.0)
        
        print(f"[WEATHER] API response status: {response.status}")
        
        if response.status == 200:
            data = json.loads(response.data)
            print(f"[WEATHER] ✅ Real weather data fetched successfully")
            return data
        else:
            print(f"[WEATHER] API error: {response.status}, {response.data[:200]}")
            return get_mock_weather(location)
    except Exception as e:
        print(f"[WEATHER] Error fetching weather: {e}")
        import traceback
        print(f"[WEATHER] Traceback: {traceback.format_exc()}")
        return get_mock_weather(location)

def get_mock_weather(location):
    """
    FALLBACK ONLY - Mock weather data
    
    ⚠️ WARNING: THIS IS NOT REAL WEATHER DATA! ⚠️
    
    This function returns fake weather data and should NEVER be used in production.
    Get a real OpenWeather API key and set it in environment variables.
    
    TODO: Get real OpenWeather API key from https://openweathermap.org/api
    """
    print(f"[WARNING] ⚠️⚠️⚠️  Using MOCK weather data for {location}")
    print(f"[CRITICAL] This is NOT real weather! Get OpenWeather API key!")
    print(f"[ACTION] Visit https://openweathermap.org/api to get API key")
    
    # FAKE DATA - DO NOT USE IN PRODUCTION
    return {
        'city': {'name': location},
        'list': [
            {
                'main': {'temp': 28, 'humidity': 65},
                'weather': [{'main': 'Clear', 'description': '⚠️ MOCK DATA - NOT REAL'}],
                'rain': None
            }
        ] * 8
    }

def analyze_weather_for_farming(forecast):
    """Analyze weather for farming decisions with 7-day forecast"""
    if not forecast or 'list' not in forecast:
        return {
            'rain_expected': False,
            'days_until_rain': 0,
            'max_temp': 30,
            'min_temp': 20,
            'recommendations': [],
            'daily_forecast': []
        }
    
    forecasts = forecast['list']
    
    # Get 7-day forecast (API gives 3-hour intervals, 8 per day)
    daily_forecast = []
    current_date = None
    day_temps = []
    day_rain = False
    
    for f in forecasts[:56]:  # 7 days * 8 intervals
        dt = datetime.fromtimestamp(f['dt'])
        date_str = dt.strftime('%Y-%m-%d')
        
        if current_date != date_str:
            # Save previous day
            if current_date and day_temps:
                daily_forecast.append({
                    'date': current_date,
                    'day': datetime.strptime(current_date, '%Y-%m-%d').strftime('%a'),
                    'max_temp': max(day_temps),
                    'min_temp': min(day_temps),
                    'rain': day_rain,
                    'weather': f['weather'][0]['main']
                })
            
            # Start new day
            current_date = date_str
            day_temps = []
            day_rain = False
        
        day_temps.append(f['main']['temp'])
        if f.get('rain'):
            day_rain = True
    
    # Add last day
    if current_date and day_temps:
        daily_forecast.append({
            'date': current_date,
            'day': datetime.strptime(current_date, '%Y-%m-%d').strftime('%a'),
            'max_temp': max(day_temps),
            'min_temp': min(day_temps),
            'rain': day_rain,
            'weather': forecasts[-1]['weather'][0]['main']
        })
    
    # Analyze first 3 days for recommendations
    forecasts_3day = forecast['list'][:24]
    
    rain_coming = False
    days_until_rain = 0
    max_temp = 0
    min_temp = 100
    
    for i, f in enumerate(forecasts_3day):
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
        'recommendations': recommendations,
        'daily_forecast': daily_forecast[:7]  # Ensure only 7 days
    }

def format_weather_response(location, analysis):
    """Format weather response with 7-day forecast"""
    message = f"🌤️ *Weather Forecast - {location.title()}*\n\n"
    
    # Show 7-day forecast if available
    if analysis.get('daily_forecast'):
        message += "📅 *7-Day Forecast*\n"
        
        weather_emoji = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Haze': '🌫️'
        }
        
        for day in analysis['daily_forecast']:
            emoji = weather_emoji.get(day['weather'], '🌤️')
            rain_icon = '💧' if day['rain'] else ''
            message += f"{day['day']}: {emoji} {int(day['min_temp'])}°-{int(day['max_temp'])}°C {rain_icon}\n"
        
        message += "\n"
    else:
        # Fallback to simple format
        message += f"📅 *Next 7 Days*\n"
        message += f"🌡️ Temperature: {analysis['min_temp']}°C - {analysis['max_temp']}°C\n"
        
        if analysis['rain_expected']:
            message += f"🌧️ Rain Expected: In {analysis['days_until_rain']} day(s)\n"
        else:
            message += "☀️ Rain: Not expected in next 3 days\n"
        
        message += "\n"
    
    message += "*🌾 Farming Advice*:\n"
    for rec in analysis['recommendations']:
        message += f"• {rec}\n"
    
    message += "\n💡 *Tip*: Check weather daily for best farming decisions!"
    
    return message
