"""
AI-Powered Price Forecasting & Supply-Demand Analysis
Uses AWS Bedrock Claude + Agmarknet historical data
"""

import json
import os
from datetime import datetime, timedelta
from statistics import mean, stdev


class PriceForecastingEngine:
    """
    Advanced price forecasting using:
    1. Historical price data from Agmarknet
    2. Supply/demand signal analysis
    3. AWS Bedrock AI for pattern recognition
    """
    
    def __init__(self):
        self.agmarknet_api_key = os.environ.get("AGMARKNET_API_KEY")
        
    def fetch_historical_prices(self, crop_name, state="Maharashtra", days=30):
        """
        Fetch historical price data from Agmarknet
        Returns: List of daily price records
        """
        import urllib3
        
        if not self.agmarknet_api_key or self.agmarknet_api_key == "not_available":
            print(f"[FORECAST] Agmarknet API key not configured")
            return None
        
        try:
            print(f"[FORECAST] Fetching {days} days of historical data for {crop_name}...")
            http = urllib3.PoolManager()
            
            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            params = {
                "api-key": self.agmarknet_api_key,
                "format": "json",
                "limit": "100",  # Get more records for historical analysis
                "filters[commodity]": crop_name.title(),
                "filters[state]": state
            }
            
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{query_string}"
            
            response = http.request("GET", full_url, timeout=10.0)
            
            if response.status != 200:
                print(f"[FORECAST] API returned status: {response.status}")
                return None
            
            data = json.loads(response.data)
            records = data.get("records", [])
            
            if not records:
                print(f"[FORECAST] No historical records found")
                return None
            
            # Process records into time series
            price_series = []
            for record in records:
                try:
                    price = float(record.get("modal_price", 0))
                    arrival = float(record.get("arrivals_in_qtl", 0))
                    date_str = record.get("arrival_date", "")
                    
                    if price > 0:
                        price_series.append({
                            "date": date_str,
                            "price": price,
                            "arrival": arrival,
                            "market": record.get("market", ""),
                            "district": record.get("district", "")
                        })
                except:
                    continue
            
            print(f"[FORECAST] ✅ Collected {len(price_series)} historical data points")
            return price_series
            
        except Exception as e:
            print(f"[FORECAST] Error fetching historical data: {e}")
            return None
    
    def analyze_supply_demand_signals(self, price_series):
        """
        Analyze supply/demand signals from price and arrival data
        """
        if not price_series or len(price_series) < 7:
            return None
        
        try:
            # Extract prices and arrivals
            prices = [p["price"] for p in price_series]
            arrivals = [p["arrival"] for p in price_series if p["arrival"] > 0]
            
            # Calculate statistics
            avg_price = mean(prices)
            price_volatility = stdev(prices) if len(prices) > 1 else 0
            
            # Recent vs older comparison
            recent_prices = prices[:len(prices)//3]  # Most recent 1/3
            older_prices = prices[len(prices)//3:]   # Older 2/3
            
            recent_avg = mean(recent_prices)
            older_avg = mean(older_prices)
            price_change_pct = ((recent_avg - older_avg) / older_avg) * 100
            
            # Supply analysis (arrivals)
            supply_signal = "unknown"
            if arrivals:
                avg_arrival = mean(arrivals)
                recent_arrivals = [a for p in price_series[:len(price_series)//3] if p["arrival"] > 0 for a in [p["arrival"]]]
                
                if recent_arrivals:
                    recent_supply_avg = mean(recent_arrivals)
                    if recent_supply_avg > avg_arrival * 1.2:
                        supply_signal = "high"  # Oversupply
                    elif recent_supply_avg < avg_arrival * 0.8:
                        supply_signal = "low"   # Undersupply
                    else:
                        supply_signal = "normal"
            
            # Demand signal (inverse of supply + price movement)
            demand_signal = "unknown"
            if supply_signal == "high" and price_change_pct < -5:
                demand_signal = "low"
            elif supply_signal == "low" and price_change_pct > 5:
                demand_signal = "high"
            elif abs(price_change_pct) < 5:
                demand_signal = "stable"
            else:
                demand_signal = "moderate"
            
            # Price trend
            if price_change_pct > 5:
                trend = "increasing"
                trend_emoji = "📈"
            elif price_change_pct < -5:
                trend = "decreasing"
                trend_emoji = "📉"
            else:
                trend = "stable"
                trend_emoji = "➡️"
            
            signals = {
                "current_avg_price": int(avg_price),
                "recent_avg_price": int(recent_avg),
                "price_change_pct": round(price_change_pct, 2),
                "price_volatility": round(price_volatility, 2),
                "trend": trend,
                "trend_emoji": trend_emoji,
                "supply_signal": supply_signal,
                "demand_signal": demand_signal,
                "data_points": len(price_series)
            }
            
            print(f"[FORECAST] Supply: {supply_signal}, Demand: {demand_signal}, Trend: {trend}")
            return signals
            
        except Exception as e:
            print(f"[FORECAST] Error analyzing signals: {e}")
            return None
    
    def generate_ai_forecast(self, crop_name, price_series, signals, language='hindi'):
        """
        Use AWS Bedrock Claude to generate intelligent price forecast
        """
        try:
            import boto3
            
            bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')
            
            # Prepare data summary for AI
            recent_prices = [p["price"] for p in price_series[:10]]
            
            if language == 'english':
                prompt = f"""You are an agricultural market analyst. Analyze this data and provide a 7-day price forecast.

Crop: {crop_name}
Current Average Price: ₹{signals['current_avg_price']}/quintal
Recent Prices (last 10 records): {recent_prices}
Price Trend: {signals['trend']} ({signals['price_change_pct']}%)
Supply Signal: {signals['supply_signal']}
Demand Signal: {signals['demand_signal']}
Volatility: {signals['price_volatility']}

Provide:
1. 7-day price forecast (single number)
2. Confidence level (high/medium/low)
3. Key factors (2-3 points)
4. Recommendation (sell now/wait/hold)

Format as JSON:
{{
  "forecast_7d": <price>,
  "confidence": "<level>",
  "factors": ["factor1", "factor2"],
  "recommendation": "<action>",
  "reasoning": "<brief explanation>"
}}"""
            else:
                prompt = f"""आप एक कृषि बाजार विश्लेषक हैं। इस डेटा का विश्लेषण करें और 7 दिन का मूल्य पूर्वानुमान दें।

फसल: {crop_name}
वर्तमान औसत मूल्य: ₹{signals['current_avg_price']}/क्विंटल
हाल की कीमतें (अंतिम 10 रिकॉर्ड): {recent_prices}
मूल्य रुझान: {signals['trend']} ({signals['price_change_pct']}%)
आपूर्ति संकेत: {signals['supply_signal']}
मांग संकेत: {signals['demand_signal']}
अस्थिरता: {signals['price_volatility']}

प्रदान करें:
1. 7 दिन का मूल्य पूर्वानुमान (एक संख्या)
2. विश्वास स्तर (उच्च/मध्यम/निम्न)
3. मुख्य कारक (2-3 बिंदु)
4. सिफारिश (अभी बेचें/प्रतीक्षा करें/रोकें)

JSON के रूप में प्रारूपित करें:
{{
  "forecast_7d": <मूल्य>,
  "confidence": "<स्तर>",
  "factors": ["कारक1", "कारक2"],
  "recommendation": "<कार्रवाई>",
  "reasoning": "<संक्षिप्त स्पष्टीकरण>"
}}"""
            
            # Call Bedrock Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.3,  # Lower temperature for more consistent forecasts
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text']
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                forecast_data = json.loads(json_match.group())
                print(f"[FORECAST] AI forecast: ₹{forecast_data.get('forecast_7d')} ({forecast_data.get('confidence')} confidence)")
                return forecast_data
            else:
                print(f"[FORECAST] Could not parse AI response")
                return None
                
        except Exception as e:
            print(f"[FORECAST] Error generating AI forecast: {e}")
            import traceback
            print(f"[FORECAST] Traceback: {traceback.format_exc()}")
            return None
    
    def get_complete_forecast(self, crop_name, state="Maharashtra", language='hindi'):
        """
        Complete forecasting pipeline:
        1. Fetch historical data
        2. Analyze supply/demand
        3. Generate AI forecast
        4. Format response
        """
        print(f"[FORECAST] Starting complete forecast for {crop_name} in {state}")
        
        # Step 1: Fetch historical data
        price_series = self.fetch_historical_prices(crop_name, state, days=30)
        
        # If API fails, use AI-only forecast
        if not price_series:
            print(f"[FORECAST] No historical data available, using AI-only forecast")
            return self.get_ai_only_forecast(crop_name, state, language)
        
        # Step 2: Analyze signals
        signals = self.analyze_supply_demand_signals(price_series)
        if not signals:
            print(f"[FORECAST] Signal analysis failed, using AI-only forecast")
            return self.get_ai_only_forecast(crop_name, state, language)
        
        # Step 3: Generate AI forecast
        ai_forecast = self.generate_ai_forecast(crop_name, price_series, signals, language)
        
        # Step 4: Combine results
        complete_forecast = {
            "crop": crop_name,
            "state": state,
            "current_price": signals['current_avg_price'],
            "forecast_7d": ai_forecast.get('forecast_7d') if ai_forecast else None,
            "confidence": ai_forecast.get('confidence') if ai_forecast else 'medium',
            "trend": signals['trend'],
            "trend_emoji": signals['trend_emoji'],
            "price_change_pct": signals['price_change_pct'],
            "supply_signal": signals['supply_signal'],
            "demand_signal": signals['demand_signal'],
            "factors": ai_forecast.get('factors', []) if ai_forecast else [],
            "recommendation": ai_forecast.get('recommendation') if ai_forecast else 'hold',
            "reasoning": ai_forecast.get('reasoning') if ai_forecast else '',
            "data_points": signals['data_points'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M IST")
        }
        
        print(f"[FORECAST] ✅ Complete forecast generated")
        return complete_forecast
    
    def get_ai_only_forecast(self, crop_name, state="Maharashtra", language='hindi'):
        """
        Generate forecast using AI without historical data (fallback when API fails)
        """
        try:
            import boto3
            
            print(f"[FORECAST] Generating AI-only forecast for {crop_name} in {state}")
            bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')
            
            if language == 'english':
                prompt = f"""You are an agricultural market analyst. Provide a 7-day price forecast for {crop_name} in {state}, India.

IMPORTANT: Use realistic Indian market prices. Typical ranges:
- Sugarcane: ₹2,500-3,500/ton
- Soybean: ₹40,000-50,000/ton  
- Wheat: ₹20,000-25,000/ton
- Rice: ₹25,000-35,000/ton
- Onion: ₹15,000-30,000/ton
- Tomato: ₹20,000-40,000/ton
- Cotton: ₹50,000-70,000/ton

Based on current market conditions, seasonal factors, and typical price patterns:

Provide:
1. Current estimated price (₹/ton) - MUST be within realistic range
2. 7-day forecast price (₹/ton) - MUST be within realistic range
3. Trend (increasing/decreasing/stable)
4. Supply signal (high/low/normal)
5. Demand signal (high/low/stable)
6. Confidence level (medium - since no historical data)
7. 2-3 key factors affecting prices
8. Recommendation (sell now/wait/hold)

Format as JSON:
{{
  "current_price": <price>,
  "forecast_7d": <price>,
  "trend": "<trend>",
  "supply": "<signal>",
  "demand": "<signal>",
  "confidence": "medium",
  "factors": ["factor1", "factor2"],
  "recommendation": "<action>",
  "reasoning": "<brief explanation>"
}}"""
            else:
                prompt = f"""आप एक कृषि बाजार विश्लेषक हैं। {state}, भारत में {crop_name} के लिए 7 दिन का मूल्य पूर्वानुमान प्रदान करें।

महत्वपूर्ण: वास्तविक भारतीय बाजार मूल्य का उपयोग करें। सामान्य सीमा:
- गन्ना: ₹2,500-3,500/टन
- सोयाबीन: ₹40,000-50,000/टन
- गेहूं: ₹20,000-25,000/टन
- चावल: ₹25,000-35,000/टन
- प्याज: ₹15,000-30,000/टन
- टमाटर: ₹20,000-40,000/टन
- कपास: ₹50,000-70,000/टन

वर्तमान बाजार स्थितियों, मौसमी कारकों और सामान्य मूल्य पैटर्न के आधार पर:

प्रदान करें:
1. वर्तमान अनुमानित मूल्य (₹/टन) - वास्तविक सीमा के भीतर होना चाहिए
2. 7 दिन का पूर्वानुमान मूल्य (₹/टन) - वास्तविक सीमा के भीतर होना चाहिए
3. रुझान (increasing/decreasing/stable)
4. आपूर्ति संकेत (high/low/normal)
5. मांग संकेत (high/low/stable)
6. विश्वास स्तर (medium - क्योंकि कोई ऐतिहासिक डेटा नहीं)
7. मूल्यों को प्रभावित करने वाले 2-3 मुख्य कारक
8. सिफारिश (sell now/wait/hold)

JSON के रूप में प्रारूपित करें:
{{
  "current_price": <मूल्य>,
  "forecast_7d": <मूल्य>,
  "trend": "<रुझान>",
  "supply": "<संकेत>",
  "demand": "<संकेत>",
  "confidence": "medium",
  "factors": ["कारक1", "कारक2"],
  "recommendation": "<कार्रवाई>",
  "reasoning": "<संक्षिप्त स्पष्टीकरण>"
}}"""
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.5,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body['content'][0]['text']
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                forecast_data = json.loads(json_match.group())
                
                # Format into standard structure
                current_price = forecast_data.get('current_price', 3000)
                forecast_price = forecast_data.get('forecast_7d', current_price)
                price_change = ((forecast_price - current_price) / current_price) * 100
                
                trend = forecast_data.get('trend', 'stable')
                trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
                
                complete_forecast = {
                    "crop": crop_name,
                    "state": state,
                    "current_price": int(current_price),
                    "forecast_7d": int(forecast_price),
                    "confidence": "medium",
                    "trend": trend,
                    "trend_emoji": trend_emoji,
                    "price_change_pct": round(price_change, 2),
                    "supply_signal": forecast_data.get('supply', 'normal'),
                    "demand_signal": forecast_data.get('demand', 'stable'),
                    "factors": forecast_data.get('factors', []),
                    "recommendation": forecast_data.get('recommendation', 'hold'),
                    "reasoning": forecast_data.get('reasoning', ''),
                    "data_points": 0,  # No historical data
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M IST"),
                    "ai_only": True
                }
                
                print(f"[FORECAST] ✅ AI-only forecast generated: ₹{current_price} → ₹{forecast_price}")
                return complete_forecast
            else:
                print(f"[FORECAST] Could not parse AI response")
                return None
                
        except Exception as e:
            print(f"[FORECAST] Error in AI-only forecast: {e}")
            import traceback
            print(f"[FORECAST] Traceback: {traceback.format_exc()}")
            return None


def format_forecast_response(forecast, language='hindi'):
    """
    Format forecast data into user-friendly message
    """
    if not forecast:
        if language == 'english':
            return "Unable to generate price forecast at this time. Please try again later."
        else:
            return "इस समय मूल्य पूर्वानुमान उत्पन्न करने में असमर्थ। कृपया बाद में पुनः प्रयास करें।"
    
    crop = forecast['crop']
    current = forecast['current_price']
    forecast_price = forecast.get('forecast_7d')
    trend_emoji = forecast['trend_emoji']
    confidence = forecast['confidence']
    supply = forecast['supply_signal']
    demand = forecast['demand_signal']
    recommendation = forecast['recommendation']
    
    if language == 'english':
        msg = f"📊 *Price Forecast - {crop}*\n\n"
        msg += f"💰 Current Price: ₹{current}/ton\n"
        
        if forecast_price:
            change = forecast_price - current
            change_pct = (change / current) * 100
            msg += f"🔮 7-Day Forecast: ₹{int(forecast_price)}/ton\n"
            msg += f"   ({'+' if change > 0 else ''}₹{int(change)}, {'+' if change_pct > 0 else ''}{change_pct:.1f}%)\n\n"
        
        msg += f"{trend_emoji} Trend: {forecast['trend'].title()}\n"
        msg += f"📦 Supply: {supply.title()}\n"
        msg += f"📈 Demand: {demand.title()}\n"
        msg += f"✅ Confidence: {confidence.title()}\n\n"
        
        msg += f"💡 *Recommendation*: {recommendation.title()}\n\n"
        
        if forecast.get('factors'):
            msg += f"🔍 *Key Factors*:\n"
            for factor in forecast['factors'][:3]:
                msg += f"• {factor}\n"
        
        if not forecast.get('ai_only', False):
            msg += f"\n📅 Based on {forecast['data_points']} market data points"
        
    else:
        msg = f"📊 *मूल्य पूर्वानुमान - {crop}*\n\n"
        msg += f"💰 वर्तमान मूल्य: ₹{current}/टन\n"
        
        if forecast_price:
            change = forecast_price - current
            change_pct = (change / current) * 100
            msg += f"🔮 7 दिन का पूर्वानुमान: ₹{int(forecast_price)}/टन\n"
            msg += f"   ({'+' if change > 0 else ''}₹{int(change)}, {'+' if change_pct > 0 else ''}{change_pct:.1f}%)\n\n"
        
        msg += f"{trend_emoji} रुझान: {forecast['trend']}\n"
        msg += f"📦 आपूर्ति: {supply}\n"
        msg += f"📈 मांग: {demand}\n"
        msg += f"✅ विश्वास: {confidence}\n\n"
        
        msg += f"💡 *सिफारिश*: {recommendation}\n\n"
        
        if forecast.get('factors'):
            msg += f"🔍 *मुख्य कारक*:\n"
            for factor in forecast['factors'][:3]:
                msg += f"• {factor}\n"
        
        if not forecast.get('ai_only', False):
            msg += f"\n📅 {forecast['data_points']} बाजार डेटा बिंदुओं के आधार पर"
    
    return msg


# Global instance
forecasting_engine = PriceForecastingEngine()
