import json
import random
from datetime import datetime, timedelta

# Maharashtra districts and their villages
DISTRICTS = {
    "Pune": ["Baramati", "Indapur", "Malegaon", "Shirur", "Daund", "Purandar", "Bhor", "Velhe"],
    "Kolhapur": ["Shahuwadi", "Panhala", "Radhanagari", "Kagal", "Hatkanangle", "Shirol", "Karvir"],
    "Nashik": ["Sinnar", "Niphad", "Dindori", "Igatpuri", "Surgana", "Kalwan", "Yeola"],
    "Satara": ["Koregaon", "Wai", "Phaltan", "Mahabaleshwar", "Patan", "Karad", "Khandala"],
    "Sangli": ["Miraj", "Tasgaon", "Jat", "Walwa", "Khanapur", "Atpadi", "Palus"],
    "Solapur": ["Pandharpur", "Mohol", "Malshiras", "Barshi", "Akkalkot", "Mangalvedhe"],
    "Ahmednagar": ["Rahuri", "Shrirampur", "Kopargaon", "Sangamner", "Newasa", "Karjat"],
    "Aurangabad": ["Paithan", "Gangapur", "Kannad", "Sillod", "Phulambri", "Khuldabad"]
}

# Soil types common in Maharashtra
SOIL_TYPES = [
    "Black Cotton Soil (Regur)",
    "Red Soil",
    "Laterite Soil",
    "Alluvial Soil",
    "Medium Black Soil",
    "Shallow Black Soil"
]

# Crops suitable for Maharashtra
CROPS = [
    "Sugarcane", "Cotton", "Soybean", "Wheat", "Rice", "Jowar", "Bajra",
    "Tur (Pigeon Pea)", "Gram", "Groundnut", "Sunflower", "Onion", "Tomato",
    "Potato", "Cabbage", "Cauliflower", "Grapes", "Pomegranate", "Banana",
    "Mango", "Orange", "Turmeric", "Ginger", "Chilli"
]

# Current crop stages
CROP_STAGES = ["Sowing", "Growing", "Flowering", "Harvesting", "Post-Harvest"]

# Irrigation methods
IRRIGATION_METHODS = ["Drip irrigation", "Sprinkler", "Flood irrigation", "Rainfed", "Canal irrigation"]

# Fertilizer types
FERTILIZER_TYPES = ["Organic", "Chemical", "Mixed", "Bio-fertilizer"]

# Indian first names
FIRST_NAMES = [
    "Rajesh", "Suresh", "Ramesh", "Mahesh", "Ganesh", "Dinesh", "Prakash", "Anil",
    "Sunil", "Vijay", "Ajay", "Sanjay", "Manoj", "Santosh", "Ashok", "Deepak",
    "Rahul", "Amit", "Rohit", "Nitin", "Sachin", "Avinash", "Prashant", "Kiran",
    "Shivaji", "Sambhaji", "Tanaji", "Bajirao", "Balaji", "Dattatray", "Govind",
    "Pandurang", "Vitthal", "Shankar", "Narayan", "Krishna", "Rama", "Laxman",
    "Bharat", "Arjun", "Karna", "Yudhishthir", "Bhima", "Nakul", "Sahadev"
]

LAST_NAMES = [
    "Patil", "Deshmukh", "Kulkarni", "Jadhav", "Pawar", "Shinde", "More", "Kamble",
    "Gaikwad", "Bhosale", "Salunkhe", "Sawant", "Mane", "Rao", "Naik", "Raut",
    "Chavan", "Kale", "Thorat", "Nikam", "Sutar", "Lokhande", "Bhagat", "Shelke",
    "Kadam", "Mohite", "Shirke", "Dange", "Ghatge", "Jedhe", "Nimbalkar", "Ghorpade"
]

def generate_phone():
    """Generate Indian mobile number"""
    return f"+91{random.randint(7000000000, 9999999999)}"

def generate_farmer(farmer_id, district, village):
    """Generate a single farmer with realistic data"""
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    
    # Assign 1-4 crops per farmer
    num_crops = random.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
    crops = random.sample(CROPS, num_crops)
    
    # Pick one crop as current crop
    current_crop = random.choice(crops)
    
    # Land size varies by district (some districts have larger farms)
    if district in ["Pune", "Nashik", "Ahmednagar"]:
        land_size = round(random.uniform(5, 100), 1)
    else:
        land_size = round(random.uniform(2, 50), 1)
    
    # Soil type
    soil_type = random.choice(SOIL_TYPES)
    
    # Experience years
    experience = random.randint(3, 35)
    
    # Success rate based on experience
    base_success = 0.65
    experience_bonus = min(experience * 0.005, 0.25)
    success_rate = round(base_success + experience_bonus + random.uniform(-0.1, 0.1), 2)
    success_rate = max(0.5, min(0.95, success_rate))
    
    # Sowing date (within last 6 months)
    days_ago = random.randint(0, 180)
    sowing_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    return {
        "id": farmer_id,
        "name": name,
        "phone": generate_phone(),
        "village_id": f"village_{hash(village) % 1000:03d}",
        "village_name": village,
        "district": district,
        "land_size_acres": land_size,
        "soil_type": soil_type,
        "crops_grown": crops,
        "current_crop": current_crop,
        "current_crop_stage": random.choice(CROP_STAGES),
        "experience_years": experience,
        "success_rate": success_rate,
        "irrigation_method": random.choice(IRRIGATION_METHODS),
        "fertilizer_usage": random.choice(FERTILIZER_TYPES),
        "sowing_date": sowing_date,
        "preferred_mandi": f"{district} APMC"
    }

def generate_dataset():
    """Generate complete dataset with 500+ farmers"""
    farmers = []
    farmer_count = 0
    
    # Distribute farmers across districts and villages
    for district, villages in DISTRICTS.items():
        # Each district gets 60-80 farmers
        district_farmers = random.randint(60, 80)
        
        for i in range(district_farmers):
            village = random.choice(villages)
            farmer_id = f"farmer_{farmer_count:04d}"
            farmer = generate_farmer(farmer_id, district, village)
            farmers.append(farmer)
            farmer_count += 1
    
    print(f"Generated {len(farmers)} farmers")
    print(f"Districts: {len(DISTRICTS)}")
    print(f"Villages: {sum(len(v) for v in DISTRICTS.values())}")
    print(f"Unique crops: {len(CROPS)}")
    
    # Load existing data structure
    try:
        with open('demo/knowledge_graph_dummy_data.json', 'r') as f:
            data = json.load(f)
    except:
        data = {"metadata": {}, "farmers": []}
    
    # Update farmers
    data['farmers'] = farmers
    
    # Update metadata
    data['metadata'].update({
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "total_farmers": len(farmers),
        "total_districts": len(DISTRICTS),
        "total_villages": sum(len(v) for v in DISTRICTS.values()),
        "total_crops": len(CROPS),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        "dataset_version": "2.0_hyperlocal"
    })
    
    # Save
    with open('demo/knowledge_graph_dummy_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Dataset saved to demo/knowledge_graph_dummy_data.json")
    
    # Print statistics
    print("\n📊 Dataset Statistics:")
    print(f"   Total Farmers: {len(farmers)}")
    
    # Farmers per district
    district_counts = {}
    for f in farmers:
        district_counts[f['district']] = district_counts.get(f['district'], 0) + 1
    
    print("\n   Farmers per District:")
    for district, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"      {district}: {count}")
    
    # Crop distribution
    crop_counts = {}
    for f in farmers:
        for crop in f['crops_grown']:
            crop_counts[crop] = crop_counts.get(crop, 0) + 1
    
    print("\n   Top 10 Crops:")
    for crop, count in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"      {crop}: {count} farmers")
    
    # Soil types
    soil_counts = {}
    for f in farmers:
        soil_counts[f['soil_type']] = soil_counts.get(f['soil_type'], 0) + 1
    
    print("\n   Soil Type Distribution:")
    for soil, count in sorted(soil_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"      {soil}: {count}")

if __name__ == "__main__":
    generate_dataset()
