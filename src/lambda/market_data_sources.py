"""
Real-time Market Data from AgMarkNet API + Claude AI Fallback
Optimized with caching and rate limiting
"""

import json
import os
from datetime import datetime, timedelta

# Import caching and rate limiting
try:
    from services.cache_service import CacheService, RateLimiter
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("[MARKET DATA] Cache service not available")


def get_agmarknet_api_prices(crop_name, state="Maharashtra"):
    """
    PRIMARY: Fetch real-time prices from AgMarkNet API with caching and rate limiting
    """
    import urllib3
    from urllib3.exceptions import MaxRetryError, TimeoutError

    # Input validation
    if not crop_name or not crop_name.strip():
        print(f"[AGMARKNET] Invalid crop name provided")
        return None

    # Check cache first
    if CACHE_AVAILABLE:
        cache_key = CacheService.get_market_data_key(crop_name, state)
        cached_data = CacheService.get(cache_key)
        if cached_data:
            print(f"[AGMARKNET] Using cached data for {crop_name}")
            return cached_data

        # Rate limiting for API calls
        api_key_rate = RateLimiter.get_api_key("agmarknet")
        if not RateLimiter.is_allowed(api_key_rate, max_requests=20, window_seconds=60):
            print(f"[AGMARKNET] Rate limited, using fallback")
            return None

    api_key = os.environ.get("AGMARKNET_API_KEY")
    if not api_key or api_key == "not_available":
        print(f"[AGMARKNET] API key not configured")
        return None

    try:
        print(f"[AGMARKNET] 📡 Calling API for {crop_name} in {state}...")

        # Create HTTP pool with optimized configuration
        http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=3.0, read=8.0),  # Reduced timeouts
            retries=urllib3.Retry(
                total=2,  # Reduced retries for faster response
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            ),
            maxsize=5  # Connection pool size
        )

        # AgMarkNet API endpoint with optimized parameters
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": "15",  # Reduced limit for faster response
            "filters[commodity]": crop_name.title(),
            "filters[state]": state
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"

        response = http.request("GET", full_url)

        if response.status != 200:
            print(f"[AGMARKNET] API returned status: {response.status}")
            if response.status == 429:
                print(f"[AGMARKNET] Rate limited by API")
            elif response.status >= 500:
                print(f"[AGMARKNET] Server error from API")
            return None

        if not response.data:
            print(f"[AGMARKNET] Empty response from API")
            return None

        try:
            data = json.loads(response.data)
        except json.JSONDecodeError as e:
            print(f"[AGMARKNET] Invalid JSON response: {e}")
            return None

        records = data.get("records", [])

        if not records:
            print(f"[AGMARKNET] No records found")
            return None

        print(f"[AGMARKNET] ✅ Got {len(records)} records")

        # Optimized price processing with validation
        prices = []
        mandis = []

        for r in records:
            if not isinstance(r, dict):
                continue

            try:
                price_str = r.get("modal_price", "0")
                if not price_str or price_str in ["", "0", "null", "None"]:
                    continue

                price = float(price_str)
                if 10 <= price <= 500000:  # Reasonable price range validation
                    prices.append(price)
                    mandis.append({
                        "name": r.get("market", "Unknown")[:30],  # Truncate for memory
                        "price": int(price),
                        "district": r.get("district", "")[:30]  # Truncate for memory
                    })
            except (ValueError, TypeError):
                continue

        if not prices:
            print(f"[AGMARKNET] No valid prices found")
            return None

        # Efficient statistics calculation
        avg_price = int(sum(prices) / len(prices))
        min_price = int(min(prices))
        max_price = int(max(prices))

        # Optimized trend calculation
        trend = "stable"
        if len(prices) >= 4:
            mid_point = len(prices) // 2
            recent_avg = sum(prices[:mid_point]) / mid_point
            older_avg = sum(prices[mid_point:]) / (len(prices) - mid_point)

            change_pct = ((recent_avg - older_avg) / older_avg) * 100
            if change_pct > 3:  # More sensitive threshold
                trend = "increasing"
            elif change_pct < -3:
                trend = "decreasing"

        # Get top 3 unique mandis efficiently
        seen_mandis = set()
        top_mandis = []
        for mandi in mandis:
            mandi_name = mandi["name"]
            if mandi_name and mandi_name not in seen_mandis and len(top_mandis) < 3:
                seen_mandis.add(mandi_name)
                top_mandis.append({
                    "name": mandi_name,
                    "price": mandi["price"]
                })

        # Optimized timestamp calculation
        utc_now = datetime.utcnow()
        ist_now = utc_now + timedelta(hours=5, minutes=30)

        result = {
            "crop": crop_name,
            "average_price": avg_price,
            "min_price": min_price,
            "max_price": max_price,
            "trend": trend,
            "top_mandis": top_mandis,
            "last_updated": ist_now.strftime("%Y-%m-%d %H:%M IST"),
            "source": "agmarknet_api",
            "data_points": len(prices)
        }

        # Cache the result
        if CACHE_AVAILABLE:
            cache_key = CacheService.get_market_data_key(crop_name, state)
            CacheService.set(cache_key, result, ttl_seconds=300)  # 5 minutes cache

        print(f"[AGMARKNET] ✅ Avg: ₹{avg_price}, Min: ₹{min_price}, Max: ₹{max_price}, Trend: {trend}")
        return result

    except (MaxRetryError, TimeoutError) as e:
        print(f"[AGMARKNET] Network timeout: {e}")
        return None
    except Exception as e:
        print(f"[AGMARKNET] API error: {e}")
        import traceback
        print(f"[AGMARKNET] Traceback: {traceback.format_exc()}")
        return None


def get_claude_ai_fallback(crop_name, state="Maharashtra"):
    """
    FALLBACK: Use Claude API (Anthropic) with caching and rate limiting
    """
    try:
        # Check cache first
        if CACHE_AVAILABLE:
            cache_key = f"ai_fallback:{crop_name.lower()}:{state.lower()}"
            cached_data = CacheService.get(cache_key)
            if cached_data:
                print(f"[CLAUDE FALLBACK] Using cached AI data for {crop_name}")
                return cached_data

            # Rate limiting for AI calls
            ai_rate_key = RateLimiter.get_api_key("claude_market")
            if not RateLimiter.is_allowed(ai_rate_key, max_requests=15, window_seconds=60):
                print(f"[CLAUDE FALLBACK] Rate limited")
                return None

        print(f"[CLAUDE FALLBACK] 🤖 Using Claude AI to fetch {crop_name} prices for {state}...")

        # Use Anthropic client via call_claude function
        from anthropic_client import call_claude_with_retry
        
        # Optimized prompt for faster response
        prompt = f"""Get current mandi prices for {crop_name} in {state}, India (March 2026).

Provide realistic market data in this EXACT JSON format:

{{
  "average_price": 2500,
  "min_price": 2300,
  "max_price": 2700,
  "trend": "stable",
  "top_mandis": [
    {{"name": "Kolhapur", "price": 2600}},
    {{"name": "Sangli", "price": 2500}},
    {{"name": "Satara", "price": 2400}}
  ]
}}

RULES:
1. Use REAL current market prices for March 2026
2. Mandis from {state} only
3. Prices in ₹ per quintal
4. Trend: "increasing", "decreasing", or "stable"
5. Reply with ONLY valid JSON, no explanation

{crop_name} prices for {state}:"""

        response_text = call_claude_with_retry(
            prompt=prompt,
            max_tokens=400,
            temperature=0.1,
            model="claude-sonnet-4-6"
        )

        # Optimized JSON extraction
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        data = json.loads(response_text)

        # Optimized timestamp
        utc_now = datetime.utcnow()
        ist_now = utc_now + timedelta(hours=5, minutes=30)

        # Add metadata efficiently
        data.update({
            "crop": crop_name,
            "last_updated": ist_now.strftime("%Y-%m-%d %H:%M IST"),
            "source": "claude_ai"
        })

        # Cache the result
        if CACHE_AVAILABLE:
            cache_key = f"ai_fallback:{crop_name.lower()}:{state.lower()}"
            CacheService.set(cache_key, data, ttl_seconds=600)  # 10 minutes cache for AI

        print(f"[CLAUDE FALLBACK] ✅ Got prices: Avg ₹{data['average_price']}, Trend: {data['trend']}")
        return data

    except Exception as e:
        print(f"[CLAUDE FALLBACK] Error: {e}")
        import traceback
        print(f"[CLAUDE FALLBACK] Traceback: {traceback.format_exc()}")
        return None


def get_fast_market_prices(crop_name, state="Maharashtra"):
    """
    Get real-time market prices
    Priority: AgMarkNet API > Claude AI Fallback
    NO STATIC DATA
    """
    print(f"[MARKET DATA] Fetching prices for: {crop_name}, state: {state}")
    
    # Method 1: AgMarkNet API (PRIMARY - Real-time government data)
    agmarknet_data = get_agmarknet_api_prices(crop_name, state)
    if agmarknet_data:
        print(f"[MARKET DATA] ✅ Using AgMarkNet API data")
        return agmarknet_data
    
    # Method 2: Claude AI Fallback (SECONDARY - AI-powered data)
    print(f"[MARKET DATA] AgMarkNet API failed, trying Claude AI fallback...")
    claude_data = get_claude_ai_fallback(crop_name, state)
    if claude_data:
        print(f"[MARKET DATA] ✅ Using Claude AI fallback data")
        return claude_data
    
    # No data available
    print(f"[MARKET DATA] ❌ No data available for {crop_name}")
    return None


def format_market_response_fast(crop_name, market_data, language='hindi'):
    """Format market data into WhatsApp message"""
    print(f"[FORMAT] Formatting response for: {crop_name}, Language: {language}")
    
    if not market_data:
        if language == 'english':
            return f"Sorry, I couldn't fetch current market data for {crop_name}. Please try again in a moment."
        else:
            return f"क्षमा करें, मैं {crop_name} के लिए वर्तमान बाजार डेटा नहीं ला सका। कृपया कुछ देर में फिर से प्रयास करें।"
    
    if language == 'english':
        message = f"📊 *{crop_name.title()} Market Price*\n\n"
        
        # Average price
        avg_price = market_data.get("average_price", 0)
        message += f"💰 *Current Price*: ₹{avg_price}/quintal\n"
        
        # Price range
        min_price = market_data.get("min_price", 0)
        max_price = market_data.get("max_price", 0)
        if min_price and max_price:
            message += f"📊 *Range*: ₹{min_price} - ₹{max_price}\n"
        
        # Trend
        trend = market_data.get("trend", "stable")
        trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
        message += f"{trend_emoji} *Trend*: {trend.title()}\n\n"
        
        # Top mandis
        top_mandis = market_data.get("top_mandis", [])
        if top_mandis:
            message += "*Top Mandis*:\n"
            for i, mandi in enumerate(top_mandis[:3], 1):
                message += f"{i}. {mandi['name']}: ₹{mandi['price']}\n"
        
        # Last updated
        last_updated = market_data.get("last_updated", "")
        if last_updated:
            message += f"\n🕐 *Updated*: {last_updated}"
    else:
        message = f"📊 *{crop_name.title()} बाजार भाव*\n\n"
        
        # Average price
        avg_price = market_data.get("average_price", 0)
        message += f"💰 *वर्तमान भाव*: ₹{avg_price}/क्विंटल\n"
        
        # Price range
        min_price = market_data.get("min_price", 0)
        max_price = market_data.get("max_price", 0)
        if min_price and max_price:
            message += f"📊 *रेंज*: ₹{min_price} - ₹{max_price}\n"
        
        # Trend
        trend = market_data.get("trend", "stable")
        trend_map = {"increasing": "बढ़ रहा", "decreasing": "घट रहा", "stable": "स्थिर"}
        trend_hindi = trend_map.get(trend, "स्थिर")
        trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
        message += f"{trend_emoji} *रुझान*: {trend_hindi}\n\n"
        
        # Top mandis
        top_mandis = market_data.get("top_mandis", [])
        if top_mandis:
            message += "*प्रमुख मंडियां*:\n"
            for i, mandi in enumerate(top_mandis[:3], 1):
                message += f"{i}. {mandi['name']}: ₹{mandi['price']}\n"
        
        # Last updated
        last_updated = market_data.get("last_updated", "")
        if last_updated:
            message += f"\n🕐 *अपडेट*: {last_updated}"
    
    print(f"[FORMAT] ✅ Response formatted")
    return message
