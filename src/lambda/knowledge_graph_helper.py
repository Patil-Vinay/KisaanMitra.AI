import json

def load_knowledge_graph_data():
    """Load knowledge graph data from JSON file"""
    # Try Lambda path first, then local path
    paths = [
        '/var/task/demo/knowledge_graph_dummy_data.json',  # Lambda
        'demo/knowledge_graph_dummy_data.json',  # Local
        '../demo/knowledge_graph_dummy_data.json',  # From src/lambda
        '../../demo/knowledge_graph_dummy_data.json'  # From tests
    ]
    
    for path in paths:
        try:
            print(f"[KG] Trying to load from: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[KG] ✅ Successfully loaded from: {path}")
                print(f"[KG] Data contains {len(data.get('farmers', []))} farmers")
                return data
        except FileNotFoundError:
            print(f"[KG] File not found: {path}")
            continue
        except Exception as e:
            print(f"[KG] Error loading from {path}: {e}")
            continue
    
    print("[KG] ❌ WARNING: Could not load knowledge graph data from any path")
    return {"farmers": []}

def get_village_farmers(village_name, crop=None, exclude_user_id=None, include_self=False):
    """
    Get farmers from a village
    
    Args:
        village_name: Name of the village
        crop: Optional crop filter
        exclude_user_id: User ID to exclude (for "other farmers" queries)
        include_self: If True, include the current user in results
    """
    data = load_knowledge_graph_data()
    print(f"[KG] Loaded {len(data.get('farmers', []))} farmers from knowledge graph")
    print(f"[KG] Searching for village: '{village_name}', user_id: '{exclude_user_id}'")
    
    farmers = []
    current_user = None
    
    for farmer in data.get("farmers", []):
        farmer_village = farmer.get("village_name", "").lower()
        farmer_phone = farmer.get("phone", "").replace("+", "")
        
        # Check if this is the current user
        is_current_user = (exclude_user_id and farmer_phone == exclude_user_id.replace("+", ""))
        
        if is_current_user:
            print(f"[KG] Found current user: {farmer.get('name')} from {farmer.get('village_name')}")
        
        # Store current user for later
        if is_current_user:
            current_user = farmer
            if not include_self:
                continue
        
        # Check village match
        if village_name.lower() in farmer_village:
            if crop:
                crops = farmer.get("crops_grown", [])
                crop_str = " ".join(crops).lower()
                if crop.lower() in crop_str:
                    farmers.append(farmer)
            else:
                farmers.append(farmer)
    
    print(f"[KG] Found {len(farmers)} farmers in village '{village_name}'")
    print(f"[KG] Current user found: {current_user is not None}")
    
    return farmers, current_user

def format_farmers_list(farmers, language='english', current_user=None, query_type='other'):
    """
    Format farmers list for display
    
    Args:
        farmers: List of farmer objects
        language: 'english' or 'hindi'
        current_user: Current user object (if available)
        query_type: 'all' (total count) or 'other' (excluding user)
    """
    if not farmers and not current_user:
        if language == 'english':
            return "I couldn't find any farmers matching your criteria in the knowledge graph."
        else:
            return "मुझे ज्ञान ग्राफ में आपके मानदंडों से मेल खाने वाले किसान नहीं मिले।"
    
    # Calculate total count
    total_count = len(farmers)
    if query_type == 'all' and current_user:
        total_count += 1  # Include the user in the count
    
    if language == 'english':
        if query_type == 'all':
            response = f"🌾 *Total Farmers in Village: {total_count}*\n\n"
            if current_user:
                response += f"*You ({current_user.get('name', 'Unknown')})*\n"
                response += f"📏 Land: {current_user.get('land_size_acres', 'N/A')} acres\n"
                crops = ", ".join(current_user.get("crops_grown", []))
                response += f"🌾 Crops: {crops}\n\n"
                response += f"*Other Farmers ({len(farmers)}):*\n\n"
        else:
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
        if query_type == 'all':
            response = f"🌾 *गांव में कुल किसान: {total_count}*\n\n"
            if current_user:
                response += f"*आप ({current_user.get('name', 'Unknown')})*\n"
                response += f"📏 जमीन: {current_user.get('land_size_acres', 'N/A')} एकड़\n"
                crops = ", ".join(current_user.get("crops_grown", []))
                response += f"🌾 फसलें: {crops}\n\n"
                response += f"*अन्य किसान ({len(farmers)}):*\n\n"
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
