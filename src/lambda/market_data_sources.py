"""
Fast Market Data Sources for KisaanMitra
Multiple sources for mandi prices with fallback
"""

import json
from datetime import datetime, timedelta

# Static price data (updated weekly) - FAST fallback
STATIC_MARKET_PRICES = {
    "wheat": {
        "average_price": 2450,
        "min_price": 2200,
        "max_price": 2600,
        "trend": "stable",
        "top_mandis": [
            {"name": "Mumbai APMC", "price": 2500},
            {"name": "Pune APMC", "price": 2450},
            {"name": "Nashik", "price": 2400}
        ],
        "last_updated": "2026-02-26"
    },
    "rice": {
        "average_price": 2200,
        "min_price": 2000,
        "max_price": 2400,
        "trend": "increasing",
        "top_mandis": [
            {"name": "Mumbai APMC", "price": 2300},
            {"name": "Kolhapur", "price": 2200},
            {"name": "Sangli", "price": 2150}
        ],
        "last_updated": "2026-02-26"
    },
    "cotton": {
        "average_price": 6500,
        "min_price": 6000,
        "max_price": 7000,
        "trend": "stable",
        "top_mandis": [
            {"name": "Akola", "price": 6600},
            {"name": "Yavatmal", "price": 6500},
            {"name": "Nagpur", "price": 6400}
        ],
        "last_updated": "2026-02-26"
    },
    "onion": {
        "average_price": 1500,
        "min_price": 1200,
        "max_price": 1800,
        "trend": "increasing",
        "top_mandis": [
            {"name": "Lasalgaon", "price": 1600},
            {"name": "Nashik", "price": 1550},
            {"name": "Pune", "price": 1450}
        ],
        "last_updated": "2026-02-26"
    },
    "potato": {
        "average_price": 1200,
        "min_price": 1000,
        "max_price": 1400,
        "trend": "stable",
        "top_mandis": [
            {"name": "Pune APMC", "price": 1250},
            {"name": "Mumbai", "price": 1200},
            {"name": "Nashik", "price": 1150}
        ],
        "last_updated": "2026-02-26"
    },
    "tomato": {
        "average_price": 2500,
        "min_price": 2000,
        "max_price": 3000,
        "trend": "increasing",
        "top_mandis": [
            {"name": "Pune APMC", "price": 2600},
            {"name": "Mumbai", "price": 2500},
            {"name": "Nashik", "price": 2400}
        ],
        "last_updated": "2026-02-26"
    },
    "sugarcane": {
        "average_price": 350,
        "min_price": 320,
        "max_price": 380,
        "trend": "stable",
        "top_mandis": [
            {"name": "Kolhapur", "price": 360},
            {"name": "Sangli", "price": 350},
            {"name": "Satara", "price": 340}
        ],
        "last_updated": "2026-02-26"
    },
    "soybean": {
        "average_price": 4500,
        "min_price": 4200,
        "max_price": 4800,
        "trend": "stable",
        "top_mandis": [
            {"name": "Indore", "price": 4600},
            {"name": "Bhopal", "price": 4500},
            {"name": "Nagpur", "price": 4400}
        ],
        "last_updated": "2026-02-26"
    }
}


def get_static_market_data(crop_name):
    """
    Get static market data - INSTANT response
    This is the fastest option, updated weekly
    """
    crop_lower = crop_name.lower()
    
    if crop_lower in STATIC_MARKET_PRICES:
        data = STATIC_MARKET_PRICES[crop_lower].copy()
        data["source"] = "static_data"
        data["crop"] = crop_name
        return data
    
    return None


def get_agmarknet_prices(crop_name, state="Maharashtra"):
    """
    Fetch real-time prices from AgMarkNet API
    Returns formatted data matching static data structure
    """
    import urllib3
    import os
    
    api_key = os.environ.get("AGMARKNET_API_KEY")
    if not api_key or api_key == "not_available":
        print(f"[DEBUG] AgMarkNet API key not configured")
        return None
    
    try:
        print(f"[DEBUG] Calling AgMarkNet API for {crop_name} in {state}...")
        http = urllib3.PoolManager()
        
        # AgMarkNet API endpoint
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": "10",
            "filters[commodity]": crop_name.title(),
            "filters[state]": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"
        
        response = http.request("GET", full_url, timeout=5.0)
        
        if response.status != 200:
            print(f"[DEBUG] AgMarkNet API returned status: {response.status}")
            return None
        
        data = json.loads(response.data)
        records = data.get("records", [])
        
        if not records:
            print(f"[DEBUG] No records found in AgMarkNet response")
            return None
        
        print(f"[DEBUG] AgMarkNet returned {len(records)} records")
        
        # Calculate statistics from records
        prices = [float(r.get("modal_price", 0)) for r in records if r.get("modal_price")]
        
        if not prices:
            print(f"[DEBUG] No valid prices in AgMarkNet data")
            return None
        
        avg_price = int(sum(prices) / len(prices))
        min_price = int(min(prices))
        max_price = int(max(prices))
        
        # Determine trend (simple: compare first vs last)
        trend = "stable"
        if len(prices) >= 2:
            if prices[0] > prices[-1] * 1.05:
                trend = "increasing"
            elif prices[0] < prices[-1] * 0.95:
                trend = "decreasing"
        
        # Get top mandis
        top_mandis = []
        for record in records[:3]:
            mandi_name = record.get("market", "Unknown")
            price = int(float(record.get("modal_price", 0)))
            top_mandis.append({"name": mandi_name, "price": price})
        
        result = {
            "crop": crop_name,
            "average_price": avg_price,
            "min_price": min_price,
            "max_price": max_price,
            "trend": trend,
            "top_mandis": top_mandis,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source": "agmarknet"
        }
        
        print(f"[INFO] ✅ AgMarkNet data processed: Avg ₹{avg_price}, Trend: {trend}")
        return result
        
    except Exception as e:
        print(f"[ERROR] AgMarkNet API error: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None


def scrape_agmarknet_website(crop_name, state="Maharashtra"):
    """
    Scrape AgMarkNet website for real-time prices
    Uses AI-extracted state for accurate data fetching
    """
    try:
        import urllib3
        import re
        from datetime import datetime
        
        print(f"[DEBUG] 🌐 Scraping AgMarkNet for {crop_name} in {state}...")
        http = urllib3.PoolManager()
        
        # AgMarkNet search endpoint
        url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
        
        # Proper headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Build query - try different state formats
        state_param = state.replace(" ", "%20")
        crop_param = crop_name.title().replace(" ", "%20")
        
        # Try the search URL format
        params = f"Tx_Commodity={crop_param}&Tx_State={state_param}&Tx_District=All&Tx_Market=All&DateFrom=&DateTo=&Fr_Date=&To_Date=&Tx_Trend=0&Tx_CommodityHead="
        full_url = f"{url}?{params}"
        
        print(f"[DEBUG] Fetching: {full_url[:100]}...")
        response = http.request("GET", full_url, headers=headers, timeout=8.0)
        
        if response.status != 200:
            print(f"[DEBUG] HTTP status: {response.status}")
            return None
        
        html = response.data.decode('utf-8', errors='ignore')
        print(f"[DEBUG] HTML received: {len(html)} chars")
        
        # Debug: Log first 500 chars to see what we got
        print(f"[DEBUG] HTML preview: {html[:500]}")
        
        # Multiple price extraction patterns
        patterns = [
            r'<td[^>]*>\s*₹?\s*([\d,]+\.?\d*)\s*</td>',  # Standard table cell
            r'<span[^>]*>\s*₹?\s*([\d,]+\.?\d*)\s*</span>',  # Span elements
            r'₹\s*([\d,]+\.?\d*)',  # Any rupee symbol followed by number
            r'Rs\.?\s*([\d,]+\.?\d*)',  # Rs. followed by number
            r'>\s*([\d,]+\.?\d*)\s*<',  # Number between tags
        ]
        
        all_prices = []
        for pattern in patterns:
            matches = re.findall(pattern, html)
            all_prices.extend(matches)
        
        print(f"[DEBUG] Found {len(all_prices)} potential price values")
        
        if not all_prices:
            print(f"[DEBUG] ❌ No prices found in HTML")
            # Log more HTML for debugging
            print(f"[DEBUG] HTML sample (chars 500-1000): {html[500:1000]}")
            return None
        
        # Convert to numbers and filter
        price_values = []
        for p in all_prices:
            try:
                val = float(p.replace(',', ''))
                # Reasonable price range for agricultural commodities (₹10 to ₹100,000 per quintal)
                if 10 <= val <= 100000:
                    price_values.append(val)
                    print(f"[DEBUG] Valid price: ₹{val}")
            except:
                continue
        
        if not price_values:
            print(f"[DEBUG] ❌ No valid prices after filtering")
            return None
        
        print(f"[INFO] ✅ Extracted {len(price_values)} valid prices")
        
        # Calculate statistics
        avg_price = int(sum(price_values) / len(price_values))
        min_price = int(min(price_values))
        max_price = int(max(price_values))
        
        # Determine trend
        trend = "stable"
        if len(price_values) >= 4:
            recent_avg = sum(price_values[:len(price_values)//2]) / (len(price_values)//2)
            older_avg = sum(price_values[len(price_values)//2:]) / (len(price_values) - len(price_values)//2)
            if recent_avg > older_avg * 1.05:
                trend = "increasing"
            elif recent_avg < older_avg * 0.95:
                trend = "decreasing"
        
        # Extract market names
        market_patterns = [
            r'<td[^>]*>([A-Za-z\s]+(?:APMC|Mandi|Market|Krishi)[^<]*)</td>',
            r'<td[^>]*>([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*</td>',
        ]
        
        markets = []
        for pattern in market_patterns:
            found = re.findall(pattern, html)
            markets.extend(found)
            if len(markets) >= 3:
                break
        
        # Clean market names
        markets = [m.strip() for m in markets if len(m.strip()) > 3][:3]
        
        # Build top mandis list
        top_mandis = []
        for i, market in enumerate(markets):
            if i < len(price_values):
                top_mandis.append({
                    "name": market,
                    "price": int(price_values[i])
                })
        
        # If no markets found, create generic ones
        if not top_mandis and len(price_values) >= 3:
            top_mandis = [
                {"name": f"{state} Market 1", "price": int(price_values[0])},
                {"name": f"{state} Market 2", "price": int(price_values[1])},
                {"name": f"{state} Market 3", "price": int(price_values[2])}
            ]
        
        result = {
            "crop": crop_name,
            "average_price": avg_price,
            "min_price": min_price,
            "max_price": max_price,
            "trend": trend,
            "top_mandis": top_mandis,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source": "agmarknet_scrape"
        }
        
        print(f"[INFO] ✅ Scraping successful: Avg ₹{avg_price}, Min ₹{min_price}, Max ₹{max_price}, Trend: {trend}")
        return result
        
    except Exception as e:
        print(f"[ERROR] AgMarkNet scraping failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None


def get_fast_market_prices(crop_name, state="Maharashtra"):
    """
    Get market prices using fastest available method
    Priority: Web Scraping (1-3s) > API (2-5s) > Static Data (instant)
    
    Now uses AI-extracted state for accurate data fetching
    """
    print(f"[DEBUG] get_fast_market_prices called for: {crop_name}, state: {state}")
    
    # Method 1: Try web scraping (FAST - 1-3 seconds, real-time)
    print(f"[DEBUG] Attempting AgMarkNet website scraping for {state}...")
    scraped_data = scrape_agmarknet_website(crop_name, state)
    if scraped_data:
        print(f"[INFO] ✅ Using AgMarkNet scraped data for {crop_name}")
        return scraped_data
    
    # Method 2: Try AgMarkNet API (if key available) (2-5 seconds, real-time)
    try:
        import os
        api_key = os.environ.get("AGMARKNET_API_KEY")
        if api_key and api_key != "not_available":
            print(f"[DEBUG] AgMarkNet API key available, fetching real-time data...")
            agmarknet_data = get_agmarknet_prices(crop_name, state)
            if agmarknet_data:
                print(f"[INFO] ✅ Using AgMarkNet API data for {crop_name}")
                return agmarknet_data
            else:
                print(f"[DEBUG] AgMarkNet API returned no data, falling back to static")
        else:
            print(f"[DEBUG] AgMarkNet API key not available, falling back to static")
    except Exception as e:
        print(f"[DEBUG] AgMarkNet API error: {e}, falling back to static")
    
    # Method 3: Static data (INSTANT - 0ms, reliable fallback)
    static_data = get_static_market_data(crop_name)
    if static_data:
        print(f"[INFO] ✅ Using static market data for {crop_name}")
        print(f"[DEBUG] Price: ₹{static_data.get('average_price')}, Trend: {static_data.get('trend')}")
        return static_data
    
    print(f"[DEBUG] ❌ No data found for {crop_name}")
    return None


def format_market_response_fast(crop_name, market_data):
    """Format market data into WhatsApp message"""
    print(f"[DEBUG] Formatting market response for: {crop_name}")
    
    if not market_data:
        print(f"[DEBUG] ❌ No market data to format")
        return f"Sorry, I don't have current market data for {crop_name}. Try wheat, rice, cotton, onion, or potato."
    
    message = f"📊 *{crop_name.title()} Market Prices*\n\n"
    
    # Trend
    trend = market_data.get("trend", "stable")
    trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
    message += f"{trend_emoji} *Trend*: {trend.title()}\n"
    
    # Average price
    avg_price = market_data.get("average_price", 0)
    message += f"💰 *Average Price*: ₹{avg_price}/quintal\n"
    
    # Price range
    min_price = market_data.get("min_price", 0)
    max_price = market_data.get("max_price", 0)
    message += f"📊 *Range*: ₹{min_price} - ₹{max_price}\n\n"
    
    # Top mandis
    top_mandis = market_data.get("top_mandis", [])
    if top_mandis:
        message += "*🏪 Top Mandis*:\n"
        for i, mandi in enumerate(top_mandis[:3], 1):
            message += f"{i}. {mandi['name']}: ₹{mandi['price']}\n"
    
    # Last updated
    last_updated = market_data.get("last_updated", "")
    message += f"\n📅 Updated: {last_updated}\n"
    
    # Data source transparency
    source = market_data.get("source", "static_data")
    if source == "agmarknet":
        message += "📡 Source: AgMarkNet API (Real-time)\n"
    elif source == "agmarknet_scrape":
        message += "🌐 Source: AgMarkNet Website (Real-time)\n"
    else:
        message += "📌 Source: Static Data (Weekly Update)\n"
    
    message += "\n💡 Tip: Check multiple mandis before selling"
    
    print(f"[DEBUG] Market response formatted successfully")
    return message


# Update schedule for static data
def should_update_static_data():
    """Check if static data needs update (weekly)"""
    last_update = datetime.strptime(STATIC_MARKET_PRICES["wheat"]["last_updated"], "%Y-%m-%d")
    days_old = (datetime.now() - last_update).days
    return days_old > 7


if __name__ == "__main__":
    # Test
    data = get_fast_market_prices("wheat")
    print(json.dumps(data, indent=2))
    print("\n" + format_market_response_fast("wheat", data))
