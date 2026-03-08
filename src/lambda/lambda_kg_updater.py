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
DUMMY_DATA_KEY = 'dummy_farmers_10k.json'  # Original 10k farmers

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)

def fetch_dummy_data():
    """Fetch existing dummy data from S3"""
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=DUMMY_DATA_KEY)
        data = json.loads(response['Body'].read().decode('utf-8'))
        # The dummy file has a "farmers" array
        return data.get('farmers', [])
    except Exception as e:
        print(f"Could not fetch dummy data: {e}")
        return []

def fetch_real_farmers():
    """Fetch all real farmers from DynamoDB"""
    table = dynamodb.Table('kisaanmitra-farmer-profiles')
    
    response = table.scan()
    farmers = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        farmers.extend(response.get('Items', []))
    
    return farmers

def convert_dynamodb_to_farmer_format(db_farmers):
    """Convert DynamoDB format to dummy data format"""
    converted = []
    for farmer in db_farmers:
        # Parse crops
        crops_str = farmer.get('current_crops', '')
        crops_list = [c.strip() for c in crops_str.split(',')] if crops_str else []
        
        converted.append({
            'name': farmer.get('name', 'Unknown'),
            'phone': farmer.get('phone_number', ''),
            'village_name': farmer.get('village', 'Unknown'),
            'district': farmer.get('district', 'Unknown'),
            'land_size_acres': float(farmer.get('land_acres', 0)),
            'soil_type': farmer.get('soil_type', 'Unknown'),
            'irrigation_method': farmer.get('irrigation_method', 'Unknown'),
            'crops_grown': crops_list,
            'current_crop': crops_list[0] if crops_list else 'Unknown',
            'experience_years': int(farmer.get('experience_years', 0)),
            'success_rate': 0.75,  # Default for real users
            'registered_at': farmer.get('created_at', datetime.utcnow().isoformat())
        })
    
    return converted

def generate_kg_data(all_farmers):
    """Generate knowledge graph structure from farmer data"""
    nodes = []
    links = []
    
    districts = defaultdict(lambda: {'count': 0, 'land': 0})
    villages = defaultdict(lambda: {'count': 0, 'land': 0, 'district': '', 'crops': set(), 'soil_types': set()})
    crops = defaultdict(lambda: {'count': 0, 'land': 0})
    
    # Process farmers
    for farmer in all_farmers:
        district = farmer.get('district', 'Unknown')
        village = farmer.get('village_name', 'Unknown')
        land = float(farmer.get('land_size_acres', 0))
        crops_list = farmer.get('crops_grown', [])
        soil_type = farmer.get('soil_type', 'Unknown')
        
        districts[district]['count'] += 1
        districts[district]['land'] += land
        
        village_key = f"{village}|{district}"
        villages[village_key]['count'] += 1
        villages[village_key]['land'] += land
        villages[village_key]['district'] = district
        villages[village_key]['soil_types'].add(soil_type)
        
        if crops_list:
            land_per_crop = land / len(crops_list) if crops_list else 0
            
            for crop in crops_list:
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
            'total_farmers': len(all_farmers),
            'total_districts': len(districts),
            'total_villages': len(villages),
            'total_crops': len(crops),
            'total_land': round(sum(d['land'] for d in districts.values()), 2),
            'last_updated': datetime.utcnow().isoformat()
        },
        'farmers': all_farmers  # Include full farmer list for dashboard
    }

def lambda_handler(event, context):
    """Lambda handler function"""
    try:
        print("Fetching dummy data from S3...")
        dummy_farmers = fetch_dummy_data()
        print(f"Found {len(dummy_farmers)} dummy farmers")
        
        print("Fetching real farmers from DynamoDB...")
        real_farmers_db = fetch_real_farmers()
        print(f"Found {len(real_farmers_db)} real farmers in DynamoDB")
        
        # Convert DynamoDB format to farmer format
        real_farmers = convert_dynamodb_to_farmer_format(real_farmers_db)
        
        # Merge dummy and real farmers
        all_farmers = dummy_farmers + real_farmers
        print(f"Total farmers after merge: {len(all_farmers)}")
        
        print("Generating knowledge graph data...")
        kg_data = generate_kg_data(all_farmers)
        
        print(f"Generated KG with {len(kg_data['nodes'])} nodes and {len(kg_data['links'])} links")
        
        # Upload to S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=S3_KEY,
            Body=json.dumps(kg_data),
            ContentType='application/json',
            CacheControl='no-cache, no-store, must-revalidate'
        )
        
        print(f"Successfully uploaded to S3: s3://{S3_BUCKET}/{S3_KEY}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Knowledge graph updated successfully',
                'metadata': kg_data['metadata'],
                'dummy_farmers': len(dummy_farmers),
                'real_farmers': len(real_farmers),
                'total_farmers': len(all_farmers)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
