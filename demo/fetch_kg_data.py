#!/usr/bin/env python3
"""
Fetch real-time data from DynamoDB and generate knowledge graph JSON
This script should be run periodically (e.g., via cron or Lambda) to update the KG dashboard
"""

import boto3
import json
from collections import defaultdict
from datetime import datetime

AWS_REGION = "ap-south-1"

def fetch_farmers_from_dynamodb():
    """Fetch all farmers from DynamoDB"""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table('kisaanmitra-farmer-profiles')
    
    response = table.scan()
    farmers = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        farmers.extend(response.get('Items', []))
    
    return farmers

def generate_knowledge_graph_data(farmers):
    """Generate knowledge graph structure from farmer data"""
    nodes = []
    links = []
    
    # Track unique entities
    districts = defaultdict(lambda: {'count': 0, 'land': 0})
    villages = defaultdict(lambda: {'count': 0, 'land': 0, 'district': '', 'crops': set(), 'soil_types': set()})
    crops = defaultdict(lambda: {'count': 0, 'land': 0})
    
    # Process farmers
    for farmer in farmers:
        district = farmer.get('district', 'Unknown')
        village = farmer.get('village', 'Unknown')
        land = float(farmer.get('land_acres', 0))
        crops_str = farmer.get('current_crops', '')
        soil_type = farmer.get('soil_type', 'Unknown')
        
        # Update district stats
        districts[district]['count'] += 1
        districts[district]['land'] += land
        
        # Update village stats
        village_key = f"{village}|{district}"
        villages[village_key]['count'] += 1
        villages[village_key]['land'] += land
        villages[village_key]['district'] = district
        villages[village_key]['soil_types'].add(soil_type)
        
        # Process crops
        if crops_str:
            farmer_crops = [c.strip() for c in crops_str.split(',')]
            land_per_crop = land / len(farmer_crops) if farmer_crops else 0
            
            for crop in farmer_crops:
                if crop:
                    crops[crop]['count'] += 1
                    crops[crop]['land'] += land_per_crop
                    villages[village_key]['crops'].add(crop)
    
    # Create district nodes
    for district, stats in districts.items():
        nodes.append({
            'id': f'd_{district}',
            'name': district,
            'type': 'district',
            'count': stats['count'],
            'land': round(stats['land'], 2),
            'group': 1
        })
    
    # Create village nodes
    for village_key, stats in villages.items():
        village_name, district = village_key.split('|')
        nodes.append({
            'id': f'v_{village_key}',
            'name': village_name,
            'type': 'village',
            'count': stats['count'],
            'land': round(stats['land'], 2),
            'soil_types': list(stats['soil_types']),
            'crops': list(stats['crops']),
            'group': 2
        })
        
        # Link village to district
        links.append({
            'source': f'd_{district}',
            'target': f'v_{village_key}',
            'value': stats['count']
        })
    
    # Create crop nodes
    for crop, stats in crops.items():
        nodes.append({
            'id': f'c_{crop}',
            'name': crop,
            'type': 'crop',
            'count': stats['count'],
            'land': round(stats['land'], 2),
            'group': 3
        })
        
        # Link crops to villages
        for village_key, village_stats in villages.items():
            if crop in village_stats['crops']:
                links.append({
                    'source': f'v_{village_key}',
                    'target': f'c_{crop}',
                    'value': 1
                })
    
    return {
        'nodes': nodes,
        'links': links,
        'metadata': {
            'total_farmers': len(farmers),
            'total_districts': len(districts),
            'total_villages': len(villages),
            'total_crops': len(crops),
            'total_land': round(sum(d['land'] for d in districts.values()), 2),
            'last_updated': datetime.utcnow().isoformat()
        }
    }

def main():
    """Main function to fetch data and generate JSON"""
    print("Fetching farmers from DynamoDB...")
    farmers = fetch_farmers_from_dynamodb()
    print(f"Found {len(farmers)} farmers")
    
    print("Generating knowledge graph data...")
    kg_data = generate_knowledge_graph_data(farmers)
    
    # Save to file
    output_file = 'demo/kg_data_live.json'
    with open(output_file, 'w') as f:
        json.dump(kg_data, f, indent=2)
    
    print(f"Knowledge graph data saved to {output_file}")
    print(f"Metadata: {kg_data['metadata']}")
    
    # Upload to S3
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        s3.put_object(
            Bucket='kisaanmitra-web-demo-1772974554',
            Key='kg_data_live.json',
            Body=json.dumps(kg_data),
            ContentType='application/json',
            CacheControl='max-age=60'  # Cache for 1 minute
        )
        print("Uploaded to S3: s3://kisaanmitra-web-demo-1772974554/kg_data_live.json")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

if __name__ == '__main__':
    main()
