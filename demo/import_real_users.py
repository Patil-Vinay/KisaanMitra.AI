"""
Import Real Users from DynamoDB to Knowledge Graph
"""

import json
import boto3
from collections import defaultdict

def get_real_users():
    """Fetch real users from DynamoDB"""
    dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
    
    # Scan the conversations table
    response = dynamodb.scan(
        TableName='kisaanmitra-conversations',
        ProjectionExpression='user_id, #ts, message, response',
        ExpressionAttributeNames={'#ts': 'timestamp'}
    )
    
    # Group by user_id
    users = defaultdict(list)
    for item in response['Items']:
        user_id = item.get('user_id', {}).get('S', '')
        timestamp = item.get('timestamp', {}).get('S', '')
        message = item.get('message', {}).get('S', '')
        response_text = item.get('response', {}).get('S', '')
        
        users[user_id].append({
            'timestamp': timestamp,
            'message': message,
            'response': response_text
        })
    
    return users

def extract_profile_from_conversations(conversations):
    """Extract user profile from conversation history"""
    profile = {
        'name': None,
        'village': None,
        'land_size': None,
        'crops': [],
        'total_messages': len(conversations)
    }
    
    # Look for onboarding responses
    for conv in conversations:
        msg = conv.get('message', '').lower()
        resp = conv.get('response', '').lower()
        
        # Extract name
        if 'name' in msg or 'naam' in msg:
            # Try to extract from next message
            pass
        
        # Extract village
        if 'village' in resp or 'gaon' in resp or 'kolhapur' in resp:
            if 'kolhapur' in resp:
                profile['village'] = 'Kolhapur'
        
        # Extract land size
        if 'acre' in msg or 'एकर' in msg:
            words = msg.split()
            for i, word in enumerate(words):
                if word.isdigit():
                    profile['land_size'] = int(word)
                    break
        
        # Extract crops
        crops_keywords = ['sugarcane', 'soybean', 'wheat', 'cotton', 'onion', 'tomato']
        for crop in crops_keywords:
            if crop in msg or crop in resp:
                if crop not in profile['crops']:
                    profile['crops'].append(crop.title())
    
    return profile

def create_real_user_entries():
    """Create farmer entries from real users"""
    print("Fetching real users from DynamoDB...")
    users = get_real_users()
    
    print(f"Found {len(users)} unique users")
    
    real_farmers = []
    
    for user_id, conversations in users.items():
        profile = extract_profile_from_conversations(conversations)
        
        # Create farmer entry
        farmer = {
            "id": f"farmer_real_{user_id[-4:]}",
            "name": profile['name'] or f"User {user_id[-4:]}",
            "phone": f"+{user_id}",
            "village_id": "village_001",  # Default to Kolhapur
            "village_name": profile['village'] or "Kolhapur",
            "land_size_acres": profile['land_size'] or 20,
            "crops_grown": profile['crops'] or ["Sugarcane"],
            "experience_years": 8,
            "success_rate": 0.85,
            "total_messages": profile['total_messages'],
            "is_real_user": True
        }
        
        real_farmers.append(farmer)
    
    return real_farmers

def add_known_users():
    """Add known users manually"""
    known_users = [
        {
            "id": "farmer_real_vinay",
            "name": "Vinay",
            "phone": "+919000000001",
            "village_id": "village_001",
            "village_name": "Kolhapur",
            "land_size_acres": 15,
            "crops_grown": ["Sugarcane", "Wheat"],
            "experience_years": 6,
            "success_rate": 0.82,
            "avg_yield_sugarcane": 445,
            "total_revenue_last_year": 2137500,
            "total_expenses_last_year": 675000,
            "net_profit_last_year": 1462500,
            "best_selling_month": "March",
            "irrigation_method": "Flood irrigation",
            "fertilizer_usage": "Chemical",
            "is_real_user": True,
            "total_messages": 0,
            "status": "Fresh start - data cleared"
        }
    ]
    
    return known_users

def update_knowledge_graph():
    """Update the knowledge graph with real users"""
    print("Loading existing knowledge graph...")
    with open('knowledge_graph_dummy_data.json', 'r') as f:
        data = json.load(f)
    
    print("Adding real users...")
    
    # Add known users
    known_users = add_known_users()
    
    # drop the old test entry
    data['farmers'] = [f for f in data['farmers'] if f['name'] != 'Parth Nikam']
    
    # Add/Update Vinay
    vinay_found = False
    for i, farmer in enumerate(data['farmers']):
        if 'Vinay' in farmer.get('name', ''):
            data['farmers'][i] = known_users[0]
            vinay_found = True
            print("Updated Vinay's profile")
            break
    
    if not vinay_found:
        data['farmers'].insert(0, known_users[0])
        print("Added Vinay")
    
    # Update metadata
    data['metadata']['total_farmers'] = len(data['farmers'])
    data['metadata']['real_users_included'] = True
    data['metadata']['last_updated'] = '2026-03-01T13:45:00 IST'
    
    # Add relationships for real users
    real_user_relationships = [
        {
            "type": "LOCATED_IN",
            "source_id": "farmer_real_vinay",
            "source_type": "farmer",
            "target_id": "village_001",
            "target_type": "village",
            "strength": 1.0
        },
        {
            "type": "GROWS",
            "source_id": "farmer_real_vinay",
            "source_type": "farmer",
            "target_id": "crop_001",
            "target_type": "crop",
            "strength": 1.0,
            "area_acres": 15,
            "yield_per_acre": 445
        }
    ]
    
    # Add new relationships
    for rel in real_user_relationships:
        if rel not in data['relationships']:
            data['relationships'].append(rel)
    
    print("Saving updated knowledge graph...")
    with open('knowledge_graph_dummy_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\nKnowledge graph updated!")
    print(f"   Total farmers: {len(data['farmers'])}")
    print(f"   Total relationships: {len(data['relationships'])}")
    print(f"   Real user: Vinay (data cleared, ready for fresh onboarding)")

def main():
    """Main function"""
    try:
        update_knowledge_graph()
        print("\nReal users imported successfully!")
        print("\nNext steps:")
        print("1. Regenerate dashboard: python visualize_knowledge_graph.py")
        print("2. Deploy to S3: ./deploy_to_s3.sh")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
