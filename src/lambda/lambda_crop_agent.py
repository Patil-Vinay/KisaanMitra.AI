"""
AWS Lambda Handler for KisaanMitra.AI Crop Agent
Integrates Crop Health API for disease detection
"""

import json
import base64
import os
import boto3
from typing import Dict, Any
import requests

# Initialize AWS clients
s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

# Configuration from environment variables
S3_BUCKET = os.environ.get('S3_BUCKET', 'kisaanmitra-images')
SECRET_NAME = os.environ.get('SECRET_NAME', 'kisaanmitra/crop-health-api')
REGION = os.environ.get('AWS_REGION', 'ap-south-1')


def get_api_key() -> str:
    """Retrieve API key from AWS Secrets Manager"""
    try:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        secret = json.loads(response['SecretString'])
        return secret['CROP_HEALTH_API_KEY']
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        # Fallback to environment variable (for testing)
        return os.environ.get('CROP_HEALTH_API_KEY', '')


def download_image_from_s3(bucket: str, key: str) -> bytes:
    """Download image from S3"""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as e:
        print(f"Error downloading from S3: {e}")
        raise


def detect_disease(image_data: bytes, latitude: float = None, longitude: float = None) -> Dict:
    """Call Crop Health API for disease detection"""
    
    api_key = get_api_key()
    if not api_key:
        raise ValueError("API key not found")
    
    # Encode image to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Prepare request
    url = "https://crop.kindwise.com/api/v1/identification"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "images": [image_base64],
        "similar_images": True
    }
    
    if latitude and longitude:
        payload["latitude"] = latitude
        payload["longitude"] = longitude
    
    # Make API call
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    
    return response.json()


def format_response_for_farmer(api_response: Dict, language: str = 'hi') -> Dict:
    """Format API response into farmer-friendly message"""
    
    result = api_response.get('result', {})
    disease_data = result.get('disease', {}).get('suggestions', [])
    crop_data = result.get('crop', {}).get('suggestions', [])
    
    # Extract top disease
    disease = None
    if disease_data:
        top_disease = disease_data[0]
        disease = {
            'name': top_disease.get('name', 'Unknown'),
            'scientific_name': top_disease.get('scientific_name', ''),
            'confidence': round(top_disease.get('probability', 0) * 100, 1),
            'id': top_disease.get('id', '')
        }
    
    # Extract crop
    crop = None
    if crop_data:
        top_crop = crop_data[0]
        crop = {
            'name': top_crop.get('name', 'Unknown'),
            'scientific_name': top_crop.get('scientific_name', ''),
            'confidence': round(top_crop.get('probability', 0) * 100, 1)
        }
    
    # Build farmer message (Hindi)
    if language == 'hi':
        if disease:
            message = f"🌾 फसल रोग पहचान\n\n"
            message += f"रोग: {disease['name']}\n"
            message += f"विश्वास स्तर: {disease['confidence']}%\n\n"
            
            if crop:
                message += f"फसल: {crop['name']}\n\n"
            
            message += "💊 उपचार:\n"
            message += "• तुरंत प्रभावित पत्तियों को हटा दें\n"
            message += "• उपयुक्त कवकनाशी का छिड़काव करें\n"
            message += "• खेत में जल निकासी सुनिश्चित करें\n\n"
            message += "अधिक जानकारी के लिए 'उपचार' टाइप करें"
        else:
            message = "कोई रोग नहीं पाया गया। फसल स्वस्थ दिखती है। ✅"
    else:
        # English fallback
        if disease:
            message = f"🌾 Crop Disease Detected\n\n"
            message += f"Disease: {disease['name']}\n"
            message += f"Confidence: {disease['confidence']}%\n\n"
            
            if crop:
                message += f"Crop: {crop['name']}\n\n"
            
            message += "💊 Treatment:\n"
            message += "• Remove affected leaves immediately\n"
            message += "• Apply appropriate fungicide\n"
            message += "• Ensure proper drainage\n\n"
            message += "Type 'treatment' for more details"
        else:
            message = "No disease detected. Crop looks healthy. ✅"
    
    return {
        'message': message,
        'disease': disease,
        'crop': crop,
        'raw_response': api_response
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function
    
    Expected event format:
    {
        "image_source": "s3" | "base64",
        "s3_bucket": "bucket-name",  # if image_source = "s3"
        "s3_key": "path/to/image.jpg",  # if image_source = "s3"
        "image_base64": "base64_string",  # if image_source = "base64"
        "latitude": 18.5204,  # optional
        "longitude": 73.8567,  # optional
        "language": "hi"  # optional, default: "hi"
    }
    """
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract parameters
        image_source = event.get('image_source', 's3')
        latitude = event.get('latitude')
        longitude = event.get('longitude')
        language = event.get('language', 'hi')
        
        # Get image data
        if image_source == 's3':
            bucket = event.get('s3_bucket', S3_BUCKET)
            key = event.get('s3_key')
            
            if not key:
                raise ValueError("s3_key is required when image_source is 's3'")
            
            print(f"Downloading image from S3: s3://{bucket}/{key}")
            image_data = download_image_from_s3(bucket, key)
            
        elif image_source == 'base64':
            image_base64 = event.get('image_base64')
            
            if not image_base64:
                raise ValueError("image_base64 is required when image_source is 'base64'")
            
            print("Decoding base64 image")
            image_data = base64.b64decode(image_base64)
            
        else:
            raise ValueError(f"Invalid image_source: {image_source}")
        
        # Detect disease
        print("Calling Crop Health API...")
        api_response = detect_disease(image_data, latitude, longitude)
        
        # Format response
        print("Formatting response for farmer...")
        formatted_response = format_response_for_farmer(api_response, language)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(formatted_response, ensure_ascii=False)
        }
        
    except ValueError as e:
        print(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Bad Request',
                'message': str(e)
            })
        }
        
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
        return {
            'statusCode': 502,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'API Error',
                'message': 'Failed to call Crop Health API'
            })
        }
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "image_source": "base64",
        "image_base64": "",  # Add base64 image here for testing
        "latitude": 18.5204,
        "longitude": 73.8567,
        "language": "hi"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
