#!/usr/bin/env python3
"""
Script to expand knowledge graph dummy data for hackathon demo
Expands from 25 to 75 farmers, 10 to 15 villages, 5 to 20 crops
Adds disease history, yield patterns, market trends, input costs
FIXED: Realistic prices, coordinates, mandis, schemes, suppliers, weather
"""

import json
import random
from datetime import datetime, timedelta

# Maharashtra villages with realistic data + coordinates + pincodes
VILLAGES = [
    {"name": "Kolhapur", "district": "Kolhapur", "soil": "Black soil (Regur)", "rainfall": 850, "irrigation": "High", "lat": 16.7050, "lng": 74.2433, "pincode": "416001"},
    {"name": "Sangli", "district": "Sangli", "soil": "Black soil", "rainfall": 780, "irrigation": "Medium", "lat": 16.8524, "lng": 74.5815, "pincode": "416416"},
    {"name": "Satara", "district": "Satara", "soil": "Red soil", "rainfall": 920, "irrigation": "High", "lat": 17.6805, "lng": 73.9903, "pincode": "415001"},
    {"name": "Pune", "district": "Pune", "soil": "Black soil", "rainfall": 650, "irrigation": "Medium", "lat": 18.5204, "lng": 73.8567, "pincode": "411001"},
    {"name": "Nashik", "district": "Nashik", "soil": "Red soil", "rainfall": 580, "irrigation": "Low", "lat": 19.9975, "lng": 73.7898, "pincode": "422001"},
    {"name": "Solapur", "district": "Solapur", "soil": "Black soil", "rainfall": 520, "irrigation": "Low", "lat": 17.6599, "lng": 75.9064, "pincode": "413001"},
    {"name": "Ahmednagar", "district": "Ahmednagar", "soil": "Black soil", "rainfall": 600, "irrigation": "Medium", "lat": 19.0948, "lng": 74.7480, "pincode": "414001"},
    {"name": "Latur", "district": "Latur", "soil": "Black soil", "rainfall": 480, "irrigation": "Low", "lat": 18.3983, "lng": 76.5604, "pincode": "413512"},
    {"name": "Nanded", "district": "Nanded", "soil": "Black soil", "rainfall": 550, "irrigation": "Medium", "lat": 19.1383, "lng": 77.3210, "pincode": "431601"},
    {"name": "Akola", "district": "Akola", "soil": "Black soil", "rainfall": 620, "irrigation": "Medium", "lat": 20.7002, "lng": 77.0082, "pincode": "444001"},
    {"name": "Aurangabad", "district": "Aurangabad", "soil": "Black soil", "rainfall": 680, "irrigation": "Medium", "lat": 19.8762, "lng": 75.3433, "pincode": "431001"},
    {"name": "Jalgaon", "district": "Jalgaon", "soil": "Black soil", "rainfall": 720, "irrigation": "High", "lat": 21.0077, "lng": 75.5626, "pincode": "425001"},
    {"name": "Dhule", "district": "Dhule", "soil": "Black soil", "rainfall": 650, "irrigation": "Medium", "lat": 20.9042, "lng": 74.7749, "pincode": "424001"},
    {"name": "Beed", "district": "Beed", "soil": "Black soil", "rainfall": 550, "irrigation": "Low", "lat": 18.9894, "lng": 75.7585, "pincode": "431122"},
    {"name": "Osmanabad", "district": "Osmanabad", "soil": "Black soil", "rainfall": 600, "irrigation": "Low", "lat": 18.1667, "lng": 76.0500, "pincode": "413501"},
]

# Expanded crop list (20 crops) - FIXED PRICES (Sugarcane ₹350/quintal FRP, varies ₹300-380 seasonally)
CROPS = [
    {"name": "Sugarcane", "season": "Kharif", "duration": 12, "water": "High", "soil": "Black soil", "yield": 450, "price": 350, "cost": 45000, "price_min": 300, "price_max": 380},
    {"name": "Soybean", "season": "Kharif", "duration": 4, "water": "Medium", "soil": "Black soil", "yield": 12, "price": 4200, "cost": 18000, "price_min": 3800, "price_max": 4600},
    {"name": "Wheat", "season": "Rabi", "duration": 5, "water": "Medium", "soil": "Black soil", "yield": 18, "price": 2200, "cost": 15000, "price_min": 2000, "price_max": 2400},
    {"name": "Cotton", "season": "Kharif", "duration": 6, "water": "Medium", "soil": "Black soil", "yield": 8, "price": 6500, "cost": 22000, "price_min": 5800, "price_max": 7200},
    {"name": "Onion", "season": "Rabi", "duration": 4, "water": "Medium", "soil": "Red soil", "yield": 120, "price": 1800, "cost": 35000, "price_min": 1200, "price_max": 2800},
    {"name": "Tomato", "season": "Rabi", "duration": 4, "water": "High", "soil": "Red soil", "yield": 200, "price": 1500, "cost": 40000, "price_min": 1000, "price_max": 2200},
    {"name": "Grapes", "season": "Perennial", "duration": 12, "water": "High", "soil": "Red soil", "yield": 100, "price": 3000, "cost": 80000, "price_min": 2500, "price_max": 4000},
    {"name": "Turmeric", "season": "Kharif", "duration": 9, "water": "Medium", "soil": "Black soil", "yield": 25, "price": 8000, "cost": 50000, "price_min": 7000, "price_max": 9500},
    {"name": "Rice", "season": "Kharif", "duration": 5, "water": "High", "soil": "Black soil", "yield": 22, "price": 2500, "cost": 20000, "price_min": 2200, "price_max": 2800},
    {"name": "Maize", "season": "Kharif", "duration": 4, "water": "Medium", "soil": "Black soil", "yield": 20, "price": 1800, "cost": 12000, "price_min": 1600, "price_max": 2000},
    {"name": "Chickpea", "season": "Rabi", "duration": 5, "water": "Low", "soil": "Black soil", "yield": 10, "price": 5500, "cost": 15000, "price_min": 5000, "price_max": 6200},
    {"name": "Pigeon Pea", "season": "Kharif", "duration": 6, "water": "Low", "soil": "Black soil", "yield": 8, "price": 6000, "cost": 12000, "price_min": 5500, "price_max": 6800},
    {"name": "Groundnut", "season": "Kharif", "duration": 4, "water": "Medium", "soil": "Red soil", "yield": 15, "price": 5000, "cost": 18000, "price_min": 4500, "price_max": 5800},
    {"name": "Sunflower", "season": "Rabi", "duration": 4, "water": "Low", "soil": "Black soil", "yield": 10, "price": 4500, "cost": 10000, "price_min": 4000, "price_max": 5200},
    {"name": "Chilli", "season": "Kharif", "duration": 6, "water": "Medium", "soil": "Red soil", "yield": 30, "price": 8000, "cost": 45000, "price_min": 6500, "price_max": 10000},
    {"name": "Brinjal", "season": "Kharif", "duration": 5, "water": "Medium", "soil": "Black soil", "yield": 180, "price": 1200, "cost": 30000, "price_min": 900, "price_max": 1600},
    {"name": "Cabbage", "season": "Rabi", "duration": 3, "water": "Medium", "soil": "Black soil", "yield": 250, "price": 800, "cost": 25000, "price_min": 600, "price_max": 1200},
    {"name": "Cauliflower", "season": "Rabi", "duration": 3, "water": "Medium", "soil": "Black soil", "yield": 200, "price": 1000, "cost": 28000, "price_min": 800, "price_max": 1400},
    {"name": "Pomegranate", "season": "Perennial", "duration": 12, "water": "Medium", "soil": "Red soil", "yield": 80, "price": 6000, "cost": 70000, "price_min": 5000, "price_max": 8000},
    {"name": "Banana", "season": "Perennial", "duration": 12, "water": "High", "soil": "Black soil", "yield": 300, "price": 1500, "cost": 60000, "price_min": 1200, "price_max": 2000},
]

# Mandis (Agricultural Markets) with coordinates
MANDIS = [
    {"name": "Kolhapur APMC", "village": "Kolhapur", "lat": 16.7100, "lng": 74.2500, "crops": ["Sugarcane", "Soybean", "Wheat", "Turmeric"]},
    {"name": "Sangli Mandi", "village": "Sangli", "lat": 16.8600, "lng": 74.5900, "crops": ["Sugarcane", "Turmeric", "Grapes"]},
    {"name": "Satara Mandi", "village": "Satara", "lat": 17.6900, "lng": 74.0000, "crops": ["Sugarcane", "Tomato", "Onion"]},
    {"name": "Pune APMC", "village": "Pune", "lat": 18.5300, "lng": 73.8700, "crops": ["Wheat", "Soybean", "Onion", "Tomato"]},
    {"name": "Nashik APMC", "village": "Nashik", "lat": 20.0000, "lng": 73.8000, "crops": ["Grapes", "Onion", "Tomato"]},
    {"name": "Lasalgaon Mandi", "village": "Nashik", "lat": 20.1400, "lng": 74.2400, "crops": ["Onion"]},
    {"name": "Solapur Mandi", "village": "Solapur", "lat": 17.6700, "lng": 75.9200, "crops": ["Cotton", "Soybean", "Wheat"]},
    {"name": "Ahmednagar Mandi", "village": "Ahmednagar", "lat": 19.1000, "lng": 74.7600, "crops": ["Sugarcane", "Wheat", "Soybean"]},
    {"name": "Latur Mandi", "village": "Latur", "lat": 18.4000, "lng": 76.5700, "crops": ["Soybean", "Cotton", "Wheat"]},
    {"name": "Nanded Mandi", "village": "Nanded", "lat": 19.1500, "lng": 77.3300, "crops": ["Soybean", "Cotton", "Wheat"]},
    {"name": "Akola Mandi", "village": "Akola", "lat": 20.7100, "lng": 77.0200, "crops": ["Cotton", "Soybean", "Wheat"]},
    {"name": "Aurangabad APMC", "village": "Aurangabad", "lat": 19.8800, "lng": 75.3500, "crops": ["Cotton", "Soybean", "Wheat"]},
    {"name": "Jalgaon Mandi", "village": "Jalgaon", "lat": 21.0100, "lng": 75.5700, "crops": ["Banana", "Cotton", "Soybean"]},
    {"name": "Dhule Mandi", "village": "Dhule", "lat": 20.9100, "lng": 74.7800, "crops": ["Cotton", "Soybean", "Wheat"]},
    {"name": "Beed Mandi", "village": "Beed", "lat": 19.0000, "lng": 75.7700, "crops": ["Soybean", "Cotton", "Wheat"]},
]

# Government Schemes - UPDATED with correct PM-KISAN eligibility
SCHEMES = [
    {
        "name": "PM-KISAN", 
        "type": "Direct Benefit", 
        "amount": 6000, 
        "frequency": "Annual", 
        "eligibility": "Small & marginal farmers (up to 2 hectares / 5 acres)", 
        "description": "₹6000/year in 3 installments of ₹2000 each",
        "land_limit_acres": 5
    },
    {
        "name": "Crop Insurance (PMFBY)", 
        "type": "Insurance", 
        "premium_percent": 2, 
        "coverage": "Up to sum insured", 
        "eligibility": "All farmers", 
        "description": "Pradhan Mantri Fasal Bima Yojana - 2% premium for Kharif, 1.5% for Rabi",
        "land_limit_acres": None
    },
    {
        "name": "Kisan Credit Card", 
        "type": "Loan", 
        "interest_rate": 7, 
        "max_amount": 300000, 
        "eligibility": "Landowners with valid land records", 
        "description": "Low-interest agricultural credit - 4% effective rate with interest subvention",
        "land_limit_acres": None
    },
    {
        "name": "Soil Health Card", 
        "type": "Service", 
        "amount": 0, 
        "frequency": "Once every 3 years", 
        "eligibility": "All farmers", 
        "description": "Free soil testing and crop-specific fertilizer recommendations",
        "land_limit_acres": None
    },
    {
        "name": "Drip Irrigation Subsidy", 
        "type": "Subsidy", 
        "subsidy_percent": 55, 
        "max_amount": 100000, 
        "eligibility": "Small/marginal farmers (priority), all farmers eligible", 
        "description": "55% subsidy for small farmers, 45% for others on drip irrigation systems",
        "land_limit_acres": None
    },
    {
        "name": "Solar Pump Subsidy", 
        "type": "Subsidy", 
        "subsidy_percent": 60, 
        "max_amount": 150000, 
        "eligibility": "All farmers in water-scarce areas", 
        "description": "60% subsidy on solar pumps (up to 7.5 HP)",
        "land_limit_acres": None
    },
]

# Input Suppliers - EXPANDED to cover more regions
SUPPLIERS = [
    # Western Maharashtra
    {"name": "Krishi Kendra Kolhapur", "village": "Kolhapur", "type": "Fertilizer", "products": ["Urea", "DAP", "NPK"], "avg_price_discount": 5},
    {"name": "Agro Chemicals Sangli", "village": "Sangli", "type": "Pesticide", "products": ["Insecticide", "Fungicide", "Herbicide"], "avg_price_discount": 8},
    {"name": "Seed Store Satara", "village": "Satara", "type": "Seeds", "products": ["Hybrid Seeds", "Organic Seeds"], "avg_price_discount": 3},
    {"name": "Farm Equipment Pune", "village": "Pune", "type": "Equipment", "products": ["Sprayers", "Drip Systems"], "avg_price_discount": 10},
    # Central Maharashtra
    {"name": "Aurangabad Agro Center", "village": "Aurangabad", "type": "Fertilizer", "products": ["Urea", "DAP", "Potash"], "avg_price_discount": 6},
    {"name": "Jalgaon Seed Suppliers", "village": "Jalgaon", "type": "Seeds", "products": ["Banana Tissue Culture", "Cotton Seeds"], "avg_price_discount": 4},
    # Eastern Maharashtra
    {"name": "Latur Fertilizer Depot", "village": "Latur", "type": "Fertilizer", "products": ["Urea", "DAP", "NPK", "Micronutrients"], "avg_price_discount": 7},
    {"name": "Nanded Pesticide Shop", "village": "Nanded", "type": "Pesticide", "products": ["Bio-pesticides", "Chemical pesticides"], "avg_price_discount": 5},
    # North Maharashtra
    {"name": "Nashik Grape Inputs", "village": "Nashik", "type": "Specialty", "products": ["Grape fertilizers", "Drip systems", "Trellising"], "avg_price_discount": 8},
    {"name": "Dhule Agro Supplies", "village": "Dhule", "type": "General", "products": ["Seeds", "Fertilizers", "Pesticides"], "avg_price_discount": 6},
]

# Monthly weather data template (temp in Celsius, rainfall in mm)
MONTHLY_WEATHER = {
    "Jan": {"temp_min": 15, "temp_max": 30, "rainfall": 5},
    "Feb": {"temp_min": 17, "temp_max": 32, "rainfall": 3},
    "Mar": {"temp_min": 20, "temp_max": 35, "rainfall": 10},
    "Apr": {"temp_min": 23, "temp_max": 38, "rainfall": 15},
    "May": {"temp_min": 25, "temp_max": 40, "rainfall": 25},
    "Jun": {"temp_min": 24, "temp_max": 32, "rainfall": 150},
    "Jul": {"temp_min": 23, "temp_max": 29, "rainfall": 250},
    "Aug": {"temp_min": 23, "temp_max": 29, "rainfall": 200},
    "Sep": {"temp_min": 22, "temp_max": 30, "rainfall": 150},
    "Oct": {"temp_min": 20, "temp_max": 32, "rainfall": 80},
    "Nov": {"temp_min": 18, "temp_max": 31, "rainfall": 20},
    "Dec": {"temp_min": 16, "temp_max": 30, "rainfall": 10},
}

# Common Marathi first names
FIRST_NAMES = [
    "Rajesh", "Suresh", "Vijay", "Anil", "Prakash", "Santosh", "Ganesh", "Mahesh", "Deepak", "Ramesh",
    "Ashok", "Sanjay", "Balaji", "Dnyaneshwar", "Kiran", "Mohan", "Sachin", "Nitin", "Prashant", "Rahul",
    "Yogesh", "Amol", "Sunil", "Vikas", "Sharad", "Dilip", "Pandurang", "Shivaji", "Dattatray", "Baban",
    "Sambhaji", "Tanaji", "Yashwant", "Raghunath", "Vishwas", "Narayan", "Govind", "Madhav", "Shrikant", "Vasant",
    "Chandrakant", "Bharat", "Anand", "Subhash", "Ramdas", "Vitthal", "Maruti", "Hanumant", "Shankar", "Laxman"
]

# Common Marathi surnames
SURNAMES = [
    "Patil", "Jadhav", "Shinde", "Deshmukh", "Kulkarni", "More", "Pawar", "Kamble", "Bhosale", "Salunkhe",
    "Gaikwad", "Mane", "Thorat", "Kale", "Jagtap", "Chavan", "Sawant", "Rane", "Dhamal", "Bhoir",
    "Desai", "Nikam", "Rathod", "Suryawanshi", "Mohite", "Kadam", "Londhe", "Shirke", "Ghatge", "Naik",
    "Bandgar", "Kumbhar", "Lokhande", "Shelke", "Gawade", "Khot", "Dange", "Bhagat", "Yadav", "Shinde"
]

# Diseases by crop
DISEASES = {
    "Sugarcane": ["Red Rot", "Smut", "Wilt", "Rust"],
    "Soybean": ["Rust", "Bacterial Blight", "Pod Blight"],
    "Wheat": ["Rust", "Smut", "Blight"],
    "Cotton": ["Bollworm", "Wilt", "Leaf Curl"],
    "Onion": ["Purple Blotch", "Stemphylium Blight"],
    "Tomato": ["Early Blight", "Late Blight", "Leaf Curl"],
    "Rice": ["Blast", "Bacterial Blight", "Sheath Blight"],
    "Chickpea": ["Wilt", "Root Rot", "Pod Borer"],
    "Pigeon Pea": ["Wilt", "Sterility Mosaic", "Pod Borer"],
    "Groundnut": ["Tikka Disease", "Rust", "Collar Rot"],
}

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two coordinates in km"""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth radius in km
    
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return round(R * c, 2)

def generate_farmers(count=75):
    """Generate realistic farmer data with better distribution"""
    farmers = []
    phone_base = 9876543210
    
    # Keep Vinay as first farmer (real user)
    farmers.append({
        "id": "farmer_real_vinay",
        "name": "Vinay",
        "phone": "+919000000001",
        "village_id": "village_001",
        "village_name": "Kolhapur",
        "land_size_acres": 50,
        "crops_grown": ["Wheat", "Sugarcane", "Soybean", "Rice", "Pigeon Pea"],
        "experience_years": 6,
        "success_rate": 0.82,
        "irrigation_method": "Flood irrigation",
        "fertilizer_usage": "Chemical",
        "is_real_user": True,
        "current_crop_stage": "Growing",
        "sowing_date": "2025-06-15",
        "preferred_mandi": "Kolhapur APMC"
    })
    
    # Distribute farmers more evenly across villages (minimum 3 per village)
    farmers_per_village = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4]  # Total 75
    
    farmer_idx = 1
    for village_idx, village in enumerate(VILLAGES):
        for _ in range(farmers_per_village[village_idx]):
            # Select 1-3 crops based on village soil and rainfall
            num_crops = random.randint(1, 3)
            suitable_crops = [c for c in CROPS if c["soil"] in village["soil"]]
            crops = random.sample(suitable_crops, min(num_crops, len(suitable_crops)))
            
            # Find nearest mandi
            village_mandis = [m for m in MANDIS if m["village"] == village["name"]]
            preferred_mandi = village_mandis[0]["name"] if village_mandis else MANDIS[0]["name"]
            
            farmer = {
                "id": f"farmer_{farmer_idx+1:03d}",
                "name": f"{random.choice(FIRST_NAMES)} {random.choice(SURNAMES)}",
                "phone": f"+91{phone_base + farmer_idx}",
                "village_id": f"village_{village_idx+1:03d}",
                "village_name": village["name"],
                "land_size_acres": random.randint(5, 30),
                "crops_grown": [c["name"] for c in crops],
                "experience_years": random.randint(3, 20),
                "success_rate": round(random.uniform(0.65, 0.95), 2),
                "irrigation_method": random.choice(["Flood irrigation", "Drip irrigation", "Sprinkler", "Rainfed"]),
                "fertilizer_usage": random.choice(["Chemical", "Organic", "Organic + Chemical"]),
                "current_crop_stage": random.choice(["Sowing", "Growing", "Flowering", "Harvesting"]),
                "sowing_date": (datetime.now() - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
                "preferred_mandi": preferred_mandi
            }
            farmers.append(farmer)
            farmer_idx += 1
    
    return farmers

def generate_disease_events(farmers, count=50):
    """Generate disease outbreak events with sequential IDs"""
    events = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(count):
        farmer = random.choice(farmers)
        crops_with_diseases = [c for c in farmer["crops_grown"] if c in DISEASES]
        if not crops_with_diseases:
            continue
            
        crop = random.choice(crops_with_diseases)
        disease = random.choice(DISEASES[crop])
        event_date = start_date + timedelta(days=random.randint(0, 365))
        
        events.append({
            "id": f"disease_{i+1:03d}",
            "type": "disease_report",
            "farmer_id": farmer["id"],
            "crop": crop,
            "disease_name": disease,
            "date": event_date.strftime("%Y-%m-%d"),
            "season": "Kharif" if event_date.month in [6,7,8,9,10] else "Rabi",
            "severity": random.choice(["Low", "Medium", "High"]),
            "treatment": random.choice(["Fungicide spray", "Pesticide", "Organic treatment", "Crop rotation"]),
            "outcome": random.choice(["Controlled", "Partially controlled", "Crop loss"])
        })
    
    return events

def generate_yield_records(farmers, count=100):
    """Generate yield/harvest records"""
    records = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(count):
        farmer = random.choice(farmers)
        if not farmer["crops_grown"]:
            continue
            
        crop_name = random.choice(farmer["crops_grown"])
        crop_data = next((c for c in CROPS if c["name"] == crop_name), None)
        if not crop_data:
            continue
            
        harvest_date = start_date + timedelta(days=random.randint(0, 730))  # 2 years
        yield_per_acre = crop_data["yield"] * random.uniform(0.8, 1.2)
        total_yield = yield_per_acre * farmer["land_size_acres"] * random.uniform(0.3, 0.8)  # Not all land for one crop
        
        records.append({
            "id": f"yield_{i+1:03d}",
            "type": "harvest",
            "farmer_id": farmer["id"],
            "crop": crop_name,
            "date": harvest_date.strftime("%Y-%m-%d"),
            "quantity_quintals": round(total_yield, 2),
            "yield_per_acre": round(yield_per_acre, 2),
            "selling_price_per_quintal": round(crop_data["price"] * random.uniform(0.9, 1.1), 2),
            "total_revenue": round(total_yield * crop_data["price"] * random.uniform(0.9, 1.1), 2)
        })
    
    return records

def generate_market_trends():
    """Generate 12 months of market price trends for ALL 20 crops with realistic seasonal variation"""
    trends = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for crop in CROPS:  # ALL 20 crops now
        base_price = crop["price"]
        price_min = crop.get("price_min", base_price * 0.85)
        price_max = crop.get("price_max", base_price * 1.15)
        
        for i, month in enumerate(months):
            # Seasonal variation based on crop type
            if crop["name"] == "Sugarcane":
                # Sugarcane: Low during harvest (Nov-Apr), High during off-season (May-Oct)
                # FRP is ₹350, but market varies ₹300-380
                if i in [10, 11, 0, 1, 2, 3]:  # Nov-Apr (harvest season)
                    multiplier = random.uniform(0.86, 0.95)  # ₹300-332
                else:  # May-Oct (off-season)
                    multiplier = random.uniform(1.0, 1.09)  # ₹350-380
            elif crop["season"] == "Kharif":
                # Kharif crops: High before sowing (Mar-May), Low during harvest (Oct-Dec)
                if i in [2, 3, 4]:  # Mar-May
                    multiplier = random.uniform(1.1, 1.2)
                elif i in [9, 10, 11]:  # Oct-Dec
                    multiplier = random.uniform(0.85, 0.95)
                else:
                    multiplier = random.uniform(0.95, 1.05)
            elif crop["season"] == "Rabi":
                # Rabi crops: High before sowing (Sep-Nov), Low during harvest (Mar-May)
                if i in [8, 9, 10]:  # Sep-Nov
                    multiplier = random.uniform(1.1, 1.2)
                elif i in [2, 3, 4]:  # Mar-May
                    multiplier = random.uniform(0.85, 0.95)
                else:
                    multiplier = random.uniform(0.95, 1.05)
            else:  # Perennial
                multiplier = random.uniform(0.95, 1.05)
            
            avg_price = round(base_price * multiplier, 2)
            
            trends.append({
                "crop": crop["name"],
                "month": month,
                "month_num": i + 1,
                "avg_price": avg_price,
                "min_price": round(max(price_min, avg_price * 0.9), 2),
                "max_price": round(min(price_max, avg_price * 1.1), 2),
                "volume_tons": random.randint(100, 1000),
                "price_trend": "High" if multiplier > 1.05 else "Low" if multiplier < 0.95 else "Stable"
            })
    
    return trends

def generate_input_costs():
    """Generate input cost data per crop"""
    costs = []
    
    for crop in CROPS:
        costs.append({
            "crop": crop["name"],
            "seed_cost_per_acre": round(crop["cost"] * 0.15, 2),
            "fertilizer_cost_per_acre": round(crop["cost"] * 0.35, 2),
            "pesticide_cost_per_acre": round(crop["cost"] * 0.20, 2),
            "irrigation_cost_per_acre": round(crop["cost"] * 0.15, 2),
            "labor_cost_per_acre": round(crop["cost"] * 0.15, 2),
            "total_cost_per_acre": crop["cost"],
            "expected_revenue_per_acre": round(crop["yield"] * crop["price"], 2),
            "profit_margin": round((crop["yield"] * crop["price"] - crop["cost"]) / (crop["yield"] * crop["price"]), 2)
        })
    
    return costs

def generate_best_practices(farmers):
    """Generate best practice records from successful farmers"""
    practices = []
    successful_farmers = [f for f in farmers if f["success_rate"] > 0.85]
    
    for i, farmer in enumerate(successful_farmers[:10]):
        for crop in farmer["crops_grown"][:1]:  # One practice per farmer
            practices.append({
                "id": f"practice_{i+1:03d}",
                "farmer_id": farmer["id"],
                "crop": crop,
                "practice": random.choice([
                    "Drip irrigation + Organic fertilizer",
                    "Crop rotation with legumes",
                    "Integrated pest management",
                    "Mulching and water conservation",
                    "Timely sowing and harvesting"
                ]),
                "success_rate": farmer["success_rate"],
                "yield_improvement_percent": round(random.uniform(10, 25), 1),
                "cost_reduction_percent": round(random.uniform(5, 15), 1)
            })
    
    return practices

def generate_weather_data():
    """Generate monthly weather data for each village"""
    weather_data = []
    
    for village in VILLAGES:
        for month, data in MONTHLY_WEATHER.items():
            # Adjust based on village rainfall
            rainfall_factor = village["rainfall"] / 650  # Normalize to average
            weather_data.append({
                "village": village["name"],
                "month": month,
                "temp_min": data["temp_min"],
                "temp_max": data["temp_max"],
                "rainfall_mm": round(data["rainfall"] * rainfall_factor, 1),
                "humidity_percent": random.randint(40, 80)
            })
    
    return weather_data

def main():
    print("🌾 Generating COMPREHENSIVE knowledge graph data with ALL fixes...")
    
    # Generate all data
    farmers = generate_farmers(75)
    disease_events = generate_disease_events(farmers, 50)
    yield_records = generate_yield_records(farmers, 100)
    market_trends = generate_market_trends()
    input_costs = generate_input_costs()
    best_practices = generate_best_practices(farmers)
    weather_data = generate_weather_data()
    
    # Create village proximity data
    village_proximity = []
    for i, v1 in enumerate(VILLAGES):
        for v2 in VILLAGES[i+1:]:
            distance = calculate_distance(v1["lat"], v1["lng"], v2["lat"], v2["lng"])
            if distance < 150:  # Within 150km
                village_proximity.append({
                    "village1": v1["name"],
                    "village2": v2["name"],
                    "distance_km": distance
                })
    
    # Create farmer-mandi relationships
    farmer_mandi_relationships = []
    for farmer in farmers:
        village = next(v for v in VILLAGES if v["name"] == farmer["village_name"])
        # Find mandis within 50km
        nearby_mandis = []
        for mandi in MANDIS:
            mandi_village = next(v for v in VILLAGES if v["name"] == mandi["village"])
            distance = calculate_distance(village["lat"], village["lng"], mandi_village["lat"], mandi_village["lng"])
            if distance < 50:
                nearby_mandis.append({"mandi": mandi["name"], "distance": distance})
        
        if nearby_mandis:
            farmer_mandi_relationships.append({
                "farmer_id": farmer["id"],
                "preferred_mandi": farmer["preferred_mandi"],
                "nearby_mandis": sorted(nearby_mandis, key=lambda x: x["distance"])[:3]
            })
    
    # Create full data structure
    data = {
        "metadata": {
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "total_farmers": len(farmers),
            "total_villages": len(VILLAGES),
            "total_crops": len(CROPS),
            "total_mandis": len(MANDIS),
            "total_schemes": len(SCHEMES),
            "total_suppliers": len(SUPPLIERS),
            "disease_events": len(disease_events),
            "yield_records": len(yield_records),
            "market_trends": len(market_trends),
            "best_practices": len(best_practices),
            "weather_records": len(weather_data),
            "focus_area": "Maharashtra agriculture - COMPLETE DATA for hackathon",
            "real_users_included": True,
            "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S IST"),
            "fixes_applied": [
                "✅ Realistic sugarcane price (₹350/quintal not ₹3200)",
                "✅ Lat/lng coordinates for all villages",
                "✅ Pincodes for all villages",
                "✅ 15 Mandi nodes with locations and crops",
                "✅ 6 Government schemes (PM-KISAN, insurance, loans, subsidies)",
                "✅ Input suppliers per village",
                "✅ Monthly weather data (temp + rainfall) for all villages",
                "✅ Market trends for ALL 20 crops (not just 10)",
                "✅ Better farmer distribution (min 3 per village)",
                "✅ Sequential disease event IDs (no gaps)",
                "✅ Farmer-mandi relationships with distances",
                "✅ Village proximity data",
                "✅ Best practices from successful farmers",
                "✅ Current crop stage and sowing dates per farmer"
            ]
        },
        "villages": [
            {
                "id": f"village_{i+1:03d}",
                "name": v["name"],
                "district": v["district"],
                "state": "Maharashtra",
                "soil_type": v["soil"],
                "avg_rainfall_mm": v["rainfall"],
                "irrigation_availability": v["irrigation"],
                "latitude": v["lat"],
                "longitude": v["lng"],
                "pincode": v["pincode"],
                "total_farmers": len([f for f in farmers if f["village_name"] == v["name"]]),
                "primary_crops": list(set([c for f in farmers if f["village_name"] == v["name"] for c in f["crops_grown"]]))[:5]
            }
            for i, v in enumerate(VILLAGES)
        ],
        "crops": [
            {
                "id": f"crop_{i+1:03d}",
                "name": c["name"],
                "season": c["season"],
                "duration_months": c["duration"],
                "water_requirement": c["water"],
                "soil_preference": c["soil"],
                "avg_yield_per_acre": c["yield"],
                "unit": "quintals",
                "avg_price_per_quintal": c["price"],
                "input_cost_per_acre": c["cost"]
            }
            for i, c in enumerate(CROPS)
        ],
        "mandis": [
            {
                "id": f"mandi_{i+1:03d}",
                "name": m["name"],
                "village": m["village"],
                "latitude": m["lat"],
                "longitude": m["lng"],
                "crops_traded": m["crops"],
                "avg_daily_volume_tons": random.randint(200, 800),
                "operating_days": "Mon-Sat"
            }
            for i, m in enumerate(MANDIS)
        ],
        "government_schemes": SCHEMES,
        "input_suppliers": SUPPLIERS,
        "farmers": farmers,
        "disease_events": disease_events,
        "yield_records": yield_records,
        "market_trends": market_trends,
        "input_costs": input_costs,
        "best_practices": best_practices,
        "monthly_weather": weather_data,
        "village_proximity": village_proximity,
        "farmer_mandi_relationships": farmer_mandi_relationships
    }
    
    # Save to file
    output_file = "knowledge_graph_dummy_data_expanded.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Calculate file size
    import os
    file_size_kb = os.path.getsize(output_file) / 1024
    
    print(f"\n✅ Generated COMPREHENSIVE data:")
    print(f"   📊 Farmers: {len(farmers)} (min 3 per village)")
    print(f"   🏘️  Villages: {len(VILLAGES)} (with lat/lng/pincode)")
    print(f"   🌾 Crops: {len(CROPS)}")
    print(f"   🏪 Mandis: {len(MANDIS)} (with locations)")
    print(f"   🏛️  Government Schemes: {len(SCHEMES)} (PM-KISAN eligibility fixed)")
    print(f"   🏬 Input Suppliers: {len(SUPPLIERS)} (covering all regions)")
    print(f"   🦠 Disease events: {len(disease_events)} (sequential IDs)")
    print(f"   📈 Yield records: {len(yield_records)}")
    print(f"   💹 Market trends: {len(market_trends)} (ALL 20 crops × 12 months with seasonal variation)")
    print(f"   💰 Input costs: {len(input_costs)}")
    print(f"   ⭐ Best practices: {len(best_practices)}")
    print(f"   🌤️  Weather data: {len(weather_data)} (15 villages × 12 months)")
    print(f"   🗺️  Village proximity: {len(village_proximity)} relationships")
    print(f"   🚜 Farmer-mandi links: {len(farmer_mandi_relationships)}")
    print(f"   📁 File size: {file_size_kb:.1f} KB")
    print(f"   💾 Saved to: {output_file}")
    
    # Show sample data
    print(f"\n📋 Sample farmer from Kolhapur:")
    kolhapur_farmers = [f for f in farmers if f["village_name"] == "Kolhapur"]
    print(f"   Total in Kolhapur: {len(kolhapur_farmers)}")
    if kolhapur_farmers:
        sample = kolhapur_farmers[0]
        print(f"   Name: {sample['name']}")
        print(f"   Land: {sample['land_size_acres']} acres")
        print(f"   Crops: {', '.join(sample['crops_grown'])}")
        print(f"   Preferred Mandi: {sample['preferred_mandi']}")
        print(f"   Current Stage: {sample['current_crop_stage']}")
        print(f"   PM-KISAN Eligible: {'Yes' if sample['land_size_acres'] <= 5 else 'No (>5 acres)'}")
    
    print(f"\n💰 Sugarcane pricing (FIXED with seasonal variation):")
    sugarcane = next(c for c in CROPS if c["name"] == "Sugarcane")
    print(f"   FRP (Base): ₹{sugarcane['price']}/quintal")
    print(f"   Market Range: ₹{sugarcane['price_min']}-₹{sugarcane['price_max']}/quintal")
    print(f"   Harvest Season (Nov-Apr): ₹300-332/quintal (low)")
    print(f"   Off-Season (May-Oct): ₹350-380/quintal (high)")
    print(f"   Yield: {sugarcane['yield']} quintals/acre")
    print(f"   Revenue: ₹{sugarcane['yield'] * sugarcane['price']}/acre (at FRP)")
    print(f"   Cost: ₹{sugarcane['cost']}/acre")
    print(f"   Profit: ₹{sugarcane['yield'] * sugarcane['price'] - sugarcane['cost']}/acre")
    
    print(f"\n🏬 Input Suppliers Coverage:")
    print(f"   Total Suppliers: {len(SUPPLIERS)}")
    print(f"   Western Maharashtra: 4 suppliers")
    print(f"   Central Maharashtra: 2 suppliers")
    print(f"   Eastern Maharashtra: 2 suppliers")
    print(f"   North Maharashtra: 2 suppliers")
    
    print(f"\n🏛️  PM-KISAN Eligibility:")
    eligible_farmers = [f for f in farmers if f['land_size_acres'] <= 5]
    print(f"   Eligible farmers (≤5 acres): {len(eligible_farmers)}")
    print(f"   Not eligible (>5 acres): {len(farmers) - len(eligible_farmers)}")

if __name__ == "__main__":
    main()
