"""Builds the WhatsApp reply for price forecast questions.

Forecasts are written to DynamoDB by lambda_sagemaker_forecaster.py.
"""
import os
import traceback
from datetime import datetime, timedelta

import boto3

FORECAST_TABLE = os.environ.get('PRICE_FORECAST_TABLE', 'kisaanmitra-price-forecasts')


def handle_price_forecast_query(crop, user_message, language='english'):
    print(f"[PRICE] Forecast query for {crop} ({language})")

    try:
        table = boto3.resource('dynamodb').Table(FORECAST_TABLE)
        item = table.get_item(Key={'commodity': crop}).get('Item')
        forecasts = item.get('forecasts', []) if item else []

        if not forecasts:
            print(f"[PRICE] No forecast stored for {crop}")
            if language == 'english':
                return f"❌ Price forecast not available for {crop.title()} at the moment. Please try again later."
            return f"❌ {crop.title()} के लिए मूल्य पूर्वानुमान अभी उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।"

        # only show dates from tomorrow onwards
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        future = [f for f in forecasts
                  if datetime.strptime(f['date'], '%Y-%m-%d').date() >= tomorrow]

        if not future:
            print(f"[PRICE] Stored forecast for {crop} is out of date")
            if language == 'english':
                return f"❌ No future price forecasts available for {crop.title()}. Please try again later."
            return f"❌ {crop.title()} के लिए भविष्य का मूल्य पूर्वानुमान उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।"

        msg = user_message.lower()
        if 'week' in msg or 'साप्ताहिक' in msg or '7' in msg:
            return format_week_forecast(crop, future[:7], language)
        return format_daily_forecast(crop, future[:2], language)

    except Exception as e:
        print(f"[PRICE ERROR] {e}")
        traceback.print_exc()
        if language == 'english':
            return f"❌ Error fetching price forecast for {crop.title()}. Please try again later."
        return f"❌ {crop.title()} के लिए मूल्य पूर्वानुमान प्राप्त करने में त्रुटि। कृपया बाद में पुनः प्रयास करें।"


def format_daily_forecast(crop, forecasts, language='english'):
    name = crop.title()
    if not forecasts:
        if language == 'english':
            return f"❌ No forecast data available for {name}"
        return f"❌ {name} के लिए पूर्वानुमान डेटा उपलब्ध नहीं है"

    first = forecasts[0]
    second = forecasts[1] if len(forecasts) > 1 else None

    if language == 'english':
        msg = f"📊 *{name} Price Forecast*\n\n"
        msg += f"*Tomorrow ({first['day']}, {first['date']})*\n"
        msg += f"💰 Predicted: ₹{first['price']}/quintal\n"
        msg += f"📈 Range: ₹{first['lower']} - ₹{first['upper']}\n\n"
        if second:
            msg += f"*Day After ({second['day']}, {second['date']})*\n"
            msg += f"💰 Predicted: ₹{second['price']}/quintal\n"
            msg += f"📈 Range: ₹{second['lower']} - ₹{second['upper']}\n\n"
            diff = second['price'] - first['price']
            if diff > 0:
                msg += f"📈 Expected to increase by ₹{abs(diff):.2f}\n"
            elif diff < 0:
                msg += f"📉 Expected to decrease by ₹{abs(diff):.2f}\n"
            else:
                msg += "📊 Expected to remain stable\n"
        msg += f"\n💡 Type 'week forecast {crop}' for 7-day prediction"
    else:
        msg = f"📊 *{name} मूल्य पूर्वानुमान*\n\n"
        msg += f"*कल ({first['day']}, {first['date']})*\n"
        msg += f"💰 अनुमानित: ₹{first['price']}/क्विंटल\n"
        msg += f"📈 सीमा: ₹{first['lower']} - ₹{first['upper']}\n\n"
        if second:
            msg += f"*परसों ({second['day']}, {second['date']})*\n"
            msg += f"💰 अनुमानित: ₹{second['price']}/क्विंटल\n"
            msg += f"📈 सीमा: ₹{second['lower']} - ₹{second['upper']}\n\n"
            diff = second['price'] - first['price']
            if diff > 0:
                msg += f"📈 ₹{abs(diff):.2f} की वृद्धि की उम्मीद\n"
            elif diff < 0:
                msg += f"📉 ₹{abs(diff):.2f} की कमी की उम्मीद\n"
            else:
                msg += "📊 स्थिर रहने की उम्मीद\n"
        msg += f"\n💡 7-दिन के पूर्वानुमान के लिए 'week forecast {crop}' टाइप करें"

    return msg


def format_week_forecast(crop, forecasts, language='english'):
    name = crop.title()
    if not forecasts:
        if language == 'english':
            return f"❌ No forecast data available for {name}"
        return f"❌ {name} के लिए पूर्वानुमान डेटा उपलब्ध नहीं है"

    if language == 'english':
        msg = f"📅 *{name} - 7 Day Forecast*\n\n"
        unit = 'quintal'
    else:
        msg = f"📅 *{name} - 7 दिन का पूर्वानुमान*\n\n"
        unit = 'क्विंटल'

    for p in forecasts[:7]:
        msg += f"*{p['day']}, {p['date']}*\n"
        msg += f"₹{p['price']}/{unit} (₹{p['lower']}-₹{p['upper']})\n\n"
    return msg
