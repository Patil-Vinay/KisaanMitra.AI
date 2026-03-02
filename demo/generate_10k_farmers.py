"""
Generate 10,000 Farmers Dataset
Creates a massive hyperlocal dataset with realistic data
"""

import json
import random
from datetime import datetime

# Maharashtra districts with real villages
DISTRICTS = {
    "Pune": ["Uruli Kanchan", "Loni Kalbhor", "Manjari BK", "Nande", "Kesnand", "Koregaon Mul", "Wadki", "Nighoje", "Nhavare", "Khamgaon", "Yavat", "Patas", "Malthan", "Alegaon", "Dive", "Nirapur", "Panshet", "Ambavade", "Rajewadi", "Morgaon", "Supe", "Malegaon BK", "Pargaon", "Kadepur", "Nimgaon Mhalungi"],
    "Kolhapur": ["Ghunki", "Arale", "Madilage", "Nool", "Hasur", "Kowad", "Yalgud", "Talandage", "Shirati", "Nandani", "Shendur", "Tamboli", "Haripur", "Daflapur", "Yadrav", "Kabbur", "Nagaon", "Ujalaiwadi", "Balinge", "Masoli", "Bhuye", "Tambave", "Kurukali", "Dhagewadi", "Wangi"],
    "Nashik": ["Saikheda", "Mohadi", "Wadivarhe", "Chandori", "Nandur Shingote", "Vadnere", "Gaulane", "Sonaj", "Thergaon", "Vavi", "Pale", "Khedgaon", "Karanjgaon", "Vashala", "Tokawade", "Amboli", "Khambale", "Bhojan", "Dabhadi", "Khadki", "Nanashi", "Vaghad", "Taharabad", "Nanduri", "Sakore"],
    "Satara": ["Dahivadi", "Pusegaon", "Aundh", "Bhuinj", "Vathar", "Rantembhe", "Menavali", "Dhom", "Pasarni", "Bavdhan", "Gursale", "Barad", "Lonand", "Padegaon", "Nimblak", "Medha", "Tapola", "Bhilar", "Amral", "Bamnoli", "Helwak", "Tarali", "Solashi", "Kasrud", "Limb"],
    "Sangli": ["Kavalapur", "Arjunwad", "Kupwad", "Kavathemahankal", "Arag", "Digraj", "Mulikwadi", "Umarani", "Nandani", "Kharsundi", "Rampur", "Asangi BK", "Yedur", "Ashta", "Pal", "Kadegaon", "Vasumbe", "Burli", "Salgare", "Ankalhop", "Savlaj", "Borgaon", "Padmale", "Yanke", "Manjarde"],
    "Solapur": ["Velapur", "Bhose", "Agalgaon", "Padvi", "Jeur", "Bhogaon", "Narkhed", "Shendri", "Borkhal", "Dahitane", "Korti", "Bhende", "Malinagar", "Tandulwadi", "Modnimb", "Kushegaon", "Nannaj", "Shelgi", "Chincholi", "Honsal", "Angar", "Karkamb", "Banali", "Chinchpur", "Kamati"],
    "Ahmednagar": ["Sonai", "Nimgaon Jali", "Varudi", "Mahalunge", "Dahigaon", "Pimplas", "Belapur", "Harigaon", "Ghargaon", "Sawargaon", "Pimpar", "Donwad", "Kothari", "Khadkewadi", "Kanhur", "Ghogargaon", "Pimpalner", "Pangri", "Khamgaon", "Nighoj"],
    "Aurangabad": ["Georai", "Waluj", "Nandur", "Shendra", "Ladsawangi", "Pimpalgaon Gogha", "Rauza", "Daulatabad", "Pohegaon", "Pishor", "Soegaon", "Satara Parisar", "Kanchanwadi", "Padegaon", "Garkheda", "Harsul", "Chitegaon", "Gevrai", "Paithanwadi", "Naygaon"]
}

CROPS = ["Wheat", "Rice", "Cotton", "Sugarcane", "Soybean", "Tur (Pigeon Pea)", "Gram", "Groundnut", "Sunflower", "Maize", "Bajra", "Jowar", "Onion", "Potato", "Tomato", "Chilli", "Turmeric", "Ginger", "Garlic", "Grapes", "Pomegranate", "Banana", "Mango", "Orange", "Cabbage", "Cauliflower", "Brinjal", "Okra", "Cucumber", "Bitter Gourd"]

SOIL_TYPES = ["Black Cotton Soil (Regur)", "Red Soil", "Laterite Soil", "Alluvial Soil", "Medium Black Soil", "Shallow Black Soil"]

IRRIGATION_METHODS = ["Borewell", "Canal", "Well", "Drip Irrigation", "Sprinkler", "Rainfed"]

FIRST_NAMES = ["Rajesh", "Suresh", "Ramesh", "Mahesh", "Ganesh", "Dinesh", "Prakash", "Anil", "Sunil", "Vijay", "Ajay", "Sanjay", "Manoj", "Santosh", "Ashok", "Deepak", "Rahul", "Amit", "Rohit", "Nitin"]
LAST_NAMES = ["Patil", "Deshmukh", "Kulkarni", "Jadhav", "Pawar", "Shinde", "More", "Kamble", "Gaikwad", "Bhosale", "Salunkhe", "Sawant", "Rane", "Nikam", "Thorat", "Mane", "Kale", "Chavan", "Raut", "Bhoir"]

def generate_farmers(count=10000):
    farmers = []
    
    print(f"🌾 Generating {count:,} farmers...")
    
    for i in range(count):
        if (i + 1) % 1000 == 0:
            print(f"   Generated {i + 1:,} farmers...")
        
        # Random district and village
        district = random.choice(list(DISTRICTS.keys()))
        village = random.choice(DISTRICTS[district])
        
        # Random name
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        # Random phone (91 + 10 digits)
        phone = f"91{random.randint(7000000000, 9999999999)}"
        
        # Random land size (0.5 to 50 acres, weighted towards smaller farms)
        land_size = round(random.triangular(0.5, 50, 5), 2)
        
        # Random soil type
        soil_type = random.choice(SOIL_TYPES)
        
        # Random irrigation
        irrigation = random.choice(IRRIGATION_METHODS)
        
        # Random crops (1-4 crops per farmer)
        num_crops = random.randint(1, 4)
        crops = random.sample(CROPS, num_crops)
        
        # Current crop (one of the crops they grow)
        current_crop = random.choice(crops)
        
        # Experience (1-40 years)
        experience = random.randint(1, 40)
        
        # Success rate (50-95%)
        success_rate = round(random.uniform(0.5, 0.95), 2)
        
        farmer = {
            "name": name,
            "phone": phone,
            "village_name": village,
            "district": district,
            "land_size_acres": land_size,
            "soil_type": soil_type,
            "irrigation_method": irrigation,
            "crops_grown": crops,
            "current_crop": current_crop,
            "experience_years": experience,
            "success_rate": success_rate,
            "registered_at": datetime.now().isoformat()
        }
        
        farmers.append(farmer)
    
    return farmers


def main():
    print("=" * 60)
    print("🌾 GENERATING 10,000 FARMERS DATASET")
    print("=" * 60)
    
    # Generate farmers
    farmers = generate_farmers(10000)
    
    # Create data structure
    data = {
        "farmers": farmers,
        "metadata": {
            "total_farmers": len(farmers),
            "generated_at": datetime.now().isoformat(),
            "districts": list(DISTRICTS.keys()),
            "total_villages": sum(len(v) for v in DISTRICTS.values()),
            "crops": CROPS,
            "soil_types": SOIL_TYPES
        }
    }
    
    # Calculate statistics
    print("\n📊 Dataset Statistics:")
    print(f"   Total Farmers: {len(farmers):,}")
    print(f"   Districts: {len(DISTRICTS)}")
    print(f"   Villages: {sum(len(v) for v in DISTRICTS.values())}")
    print(f"   Crop Types: {len(CROPS)}")
    print(f"   Soil Types: {len(SOIL_TYPES)}")
    
    # District distribution
    district_counts = {}
    for f in farmers:
        d = f['district']
        district_counts[d] = district_counts.get(d, 0) + 1
    
    print("\n🏛️ District Distribution:")
    for district, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {district}: {count:,} farmers")
    
    # Total land
    total_land = sum(f['land_size_acres'] for f in farmers)
    avg_land = total_land / len(farmers)
    print(f"\n📏 Land Statistics:")
    print(f"   Total Land: {total_land:,.2f} acres")
    print(f"   Average per Farmer: {avg_land:.2f} acres")
    
    # Crop distribution
    crop_counts = {}
    for f in farmers:
        for crop in f['crops_grown']:
            crop_counts[crop] = crop_counts.get(crop, 0) + 1
    
    print(f"\n🌾 Top 10 Crops:")
    for crop, count in sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {crop}: {count:,} farmers")
    
    # Save to file
    print(f"\n💾 Saving to knowledge_graph_dummy_data.json...")
    with open('knowledge_graph_dummy_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    # Get file size
    import os
    file_size = os.path.getsize('knowledge_graph_dummy_data.json')
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"✅ Dataset saved successfully!")
    print(f"   File size: {file_size_mb:.2f} MB")
    
    print("\n" + "=" * 60)
    print("🎉 10,000 FARMERS DATASET COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update KG dashboard: python create_ultimate_kg_dashboard.py")
    print("2. Deploy to S3: ./deploy_to_s3.sh")
    print("3. Deploy to Lambda: cd ../src/lambda && ./deploy_whatsapp.sh")

if __name__ == "__main__":
    main()
