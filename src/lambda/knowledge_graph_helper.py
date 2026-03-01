import json

def load_knowledge_graph_data():
    try:
        with open('/var/task/demo/knowledge_graph_dummy_data.json', 'r') as f:
            return json.load(f)
    except:
        return {"farmers": []}

def get_village_farmers(village_name, crop=None, exclude_user_id=None):
    data = load_knowledge_graph_data()
    farmers = []
    for farmer in data.get("farmers", []):
        # Skip the current user
        if exclude_user_id and farmer.get("phone", "").replace("+", "") == exclude_user_id.replace("+", ""):
            continue
            
        farmer_village = farmer.get("village_name", "").lower()
        if village_name.lower() in farmer_village:
            if crop:
                crops = farmer.get("crops_grown", [])
                crop_str = " ".join(crops).lower()
                if crop.lower() in crop_str:
                    farmers.append(farmer)
            else:
                farmers.append(farmer)
    return farmers

def format_farmers_list(farmers, language='english'):
    if not farmers:
        if language == 'english':
            return "I couldn't find any OTHER farmers matching your criteria in the knowledge graph."
        else:
            return "मुझे ज्ञान ग्राफ में आपके मानदंडों से मेल खाने वाले अन्य किसान नहीं मिले।"
    
    if language == 'english':
        response = f"🌾 *Found {len(farmers)} Other Farmer(s)*\n\n"
        for i, farmer in enumerate(farmers[:10], 1):
            name = farmer.get("name", "Unknown")
            village = farmer.get("village_name", "Unknown")
            crops = ", ".join(farmer.get("crops_grown", []))
            land = farmer.get("land_size_acres", "N/A")
            response += f"*{i}. {name}*\n📍 Village: {village}\n🌾 Crops: {crops}\n📏 Land: {land} acres\n\n"
        if len(farmers) > 10:
            response += f"_...and {len(farmers) - 10} more farmers_\n\n"
        response += "💡 Type 'back' to go back, 'home' for main menu"
    else:
        response = f"🌾 *{len(farmers)} अन्य किसान मिले*\n\n"
        for i, farmer in enumerate(farmers[:10], 1):
            name = farmer.get("name", "Unknown")
            village = farmer.get("village_name", "Unknown")
            crops = ", ".join(farmer.get("crops_grown", []))
            land = farmer.get("land_size_acres", "N/A")
            response += f"*{i}. {name}*\n📍 गांव: {village}\n🌾 फसलें: {crops}\n📏 जमीन: {land} एकड़\n\n"
        if len(farmers) > 10:
            response += f"_...और {len(farmers) - 10} किसान_\n\n"
        response += "💡 'back' टाइप करें वापस जाने के लिए, 'home' मुख्य मेनू के लिए"
    return response
