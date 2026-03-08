"""
Lambda function to update Knowledge Graph data periodically
Triggered by EventBridge (CloudWatch Events) every 5 minutes
"""

import boto3
import json
from collections import defaultdict
from datetime import datetime
import os

AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')
S3_BUCKET = 'kisaanmitra-knowledge-graph'
S3_KEY = 'knowledge_graph_dummy_data.json'

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)

def fetch_farmers():
    """Fetch all farmers from DynamoDB"""
    table = dynamodb.Table('kisaanmitra-farmer-profiles')
    
    response = table.scan()
    farmers = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        farmers.extend(response.get('Items', []))
    
    return farmers

def generate_kg_data(farmers):
    """Generate knowledge graph structure"""
    nodes = []
    links = []
    
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
        
        districts[district]['count'] += 1
        districts[district]['land'] += land
        
        village_key = f"{village}|{district}"
        villages[village_key]['count'] += 1
        villages[village_key]['land'] += land
        villages[village_key]['district'] = district
        villages[village_key]['soil_types'].add(soil_type)
        
        if crops_str:
            farmer_crops = [c.strip() for c in crops_str.split(',')]
            land_per_crop = land / len(farmer_crops) if farmer_crops else 0
            
            for crop in farmer_crops:
                if crop:
                    crops[crop]['count'] += 1
                    crops[crop]['land'] += land_per_crop
                    villages[village_key]['crops'].add(crop)
    
    # Create nodes
    for district, stats in districts.items():
        nodes.append({
            'id': f'd_{district}',
            'name': district,
            'type': 'district',
            'count': stats['count'],
            'land': round(stats['land'], 2),
            'group': 1
        })
    
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
        
        links.append({
            'source': f'd_{district}',
            'target': f'v_{village_key}',
            'value': stats['count']
        })
    
    for crop, stats in crops.items():
        nodes.append({
            'id': f'c_{crop}',
            'name': crop,
            'type': 'crop',
            'count': stats['count'],
            'land': round(stats['land'], 2),
            'group': 3
        })
        
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

def lambda_handler(event, context):
    """Lambda handler function"""
    try:
        print("Fetching farmers from DynamoDB...")
        farmers = fetch_farmers()
        print(f"Found {len(farmers)} farmers")
        
        print("Generating knowledge graph data...")
        kg_data = generate_kg_data(farmers)
        
        print(f"Generated KG with {len(kg_data['nodes'])} nodes and {len(kg_data['links'])} links")
        
        # Upload to S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=S3_KEY,
            Body=json.dumps(kg_data),
            ContentType='application/json',
            CacheControl='max-age=60'
        )
        
        print(f"Successfully uploaded to S3: s3://{S3_BUCKET}/{S3_KEY}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Knowledge graph updated successfully',
                'metadata': kg_data['metadata']
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
