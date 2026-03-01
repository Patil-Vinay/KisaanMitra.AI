"""
Knowledge Graph Helper - Query village and community data
"""

import json

# Load dummy data from demo folder
def load_knowledge_graph_data():
    """Load knowledge graph dummy data"""
    try:
        # In Lambda, this file should be in the package
        with open('/var/task/demo/knowledge_graph_dummy_data.json', 'r') as f:
            return json.load(f)
    except:
        # Fallback: return empty structure
        print("[KG] Could not load knowledge graph data")
        return {"nodes": [], "edges": []}

def get_village_farmers(village_name, crop=None):
    """Get farmers from a specific village, optionally filtered by crop"""
    data = load_knowledge_graph_data()
    
    farmers = []
    for node in data.get("nodes", []):
        if node.get("type") == "farmer":
            farmer_data = node.get("data", {})
            farmer_village = farmer_data.get("village", "").lower()
            
            if village_name.lower() in farmer_village:
                # If crop filter specified, check if farmer grows that crop
                if crop:
                    farmer_crops = farmer_data.get("crops", "").lower()
                    if crop.lower() in farmer_crops:
                        farmers.append(farmer_data)
                else:
                    farmers.append(farmer_data)
    
    return farmers

def get_crop_farmers(crop_name, village=None):
    """Get farmers growing a specific crop, optionally filtered by village"""
    data = load_knowledge_graph_data()
    
    farmers = []
    for node in data.get("nodes", []):
        if node.get("type") == "farmer":
            farmer_data = node.get("data", {})
            farmer_crops = farmer_data.get("crops", "").lower()
            
            if crop_name.lower() in farmer_crops:
                # If village filter specified, check village
                if village:
                    farmer_village = farmer_data.get("village", "").lower()
                    if village.lower() in farmer_village:
                        farmers.append(farmer_data)
                else:
                    farmers.append(farmer_data)
    
    return farmers

def format_farmers_list(farmers, language='english'):
    """Format list of farmers for WhatsApp"""
    if not farmers:
        if language == 'english':
            return "I couldn't find any farmers matching your criteria in the knowledge graph."
        else:
            return "मुझे ज्ञान ग्राफ में आपके मानदंडों से मेल खाने वाले कोई किसान नहीं मिले।"
    
    if language == 'english':
        response = f"🌾 *Found {len(farmers)} Farmer(s)*\n\n"
        for i, farmer in enumerate(farmers[:10], 1):  # Limit to 10
            name = farmer.get("name", "Unknown")
            village = farmer.get("village", "Unknown")
            crops = farmer.get("crops", "Unknown")
            land = farmer.get("land_acres", "N/A")
            
            response += f"*{i}. {name}*\n"
            response += f"📍 Village: {village}\n"
            response += f"🌾 Crops: {crops}\n"
            response += f"📏 Land: {land} acres\n\n"
        
        if len(farmers) > 10:
            response += f"_...and {len(farmers) - 10} more farmers_\n\n"
        
        response += "💡 Type 'back' to go back, 'home' for main menu"
    else:
        response = f"🌾 *{len(farmers)} किसान मिले*\n\n"
        for i, farmer in enumerate(farmers[:10], 1):
            name = farmer.get("name", "Unknown")
            village = farmer.get("village", "Unknown")
            crops = farmer.get("crops", "Unknown")
            land = farmer.get("land_acres", "N/A")
            
            response += f"*{i}. {name}*\n"
            response += f"📍 गांव: {village}\n"
            response += f"🌾 फसलें: {crops}\n"
            response += f"📏 जमीन: {land} एकड़\n\n"
        
        if len(farmers) > 10:
            response += f"_...और {len(farmers) - 10} किसान_\n\n"
        
        response += "💡 'back' टाइप करें वापस जाने के लिए, 'home' मुख्य मेनू के लिए"
    
    return response

def get_village_statistics(village_name):
    """Get statistics for a village"""
    farmers = get_village_farmers(village_name)
    
    if not farmers:
        return None
    
    total_land = sum(float(f.get("land_acres", 0)) for f in farmers)
    
    # Count crops
    crop_counts = {}
    for farmer in farmers:
        crops = farmer.get("crops", "").split(",")
        for crop in crops:
            crop = crop.strip()
            if crop:
                crop_counts[crop] = crop_counts.get(crop, 0) + 1
    
    return {
        "farmer_count": len(farmers),
        "total_land": total_land,
        "crops": crop_counts,
        "farmers": farmers
    }

def format_village_stats(stats, village_name, language='english'):
    """Format village statistics for WhatsApp"""
    if not stats:
        if language == 'english':
            return f"No data found for {village_name} village."
        else:
            return f"{village_name} गांव के लिए कोई डेटा नहीं मिला।"
    
    if language == 'english':
        response = f"📊 *{village_name} Village Statistics*\n\n"
        response += f"👥 Total Farmers: {stats['farmer_count']}\n"
        response += f"📏 Total Land: {stats['total_land']:.1f} acres\n\n"
        
        response += "*🌾 Crops Grown:*\n"
        for crop, count in sorted(stats['crops'].items(), key=lambda x: x[1], reverse=True)[:5]:
            response += f"• {crop}: {count} farmer(s)\n"
        
        response += f"\n💡 Type 'back' to go back, 'home' for main menu"
    else:
        response = f"📊 *{village_name} गांव के आंकड़े*\n\n"
        response += f"👥 कुल किसान: {stats['farmer_count']}\n"
        response += f"📏 कुल जमीन: {stats['total_land']:.1f} एकड़\n\n"
        
        response += "*🌾 उगाई जाने वाली फसलें:*\n"
        for crop, count in sorted(stats['crops'].items(), key=lambda x: x[1], reverse=True)[:5]:
            response += f"• {crop}: {count} किसान\n"
        
        response += f"\n💡 'back' टाइप करें वापस जाने के लिए, 'home' मुख्य मेनू के लिए"
    
    return response
