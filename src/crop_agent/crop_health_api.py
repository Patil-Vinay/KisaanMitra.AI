import requests
import base64
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CropHealthAPI:
    """Crop.health API Client (Kindwise platform)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://crop.kindwise.com/api/v1"
        self.headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def detect_disease(self, image_path: str, 
                       latitude: Optional[float] = None,
                       longitude: Optional[float] = None) -> Dict:
        """Detect crop disease from image"""
        
        # Validate image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        print(f"Reading image: {image_path}")
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Build payload
        payload = {
            "images": [image_data],
            "similar_images": True
        }
        
        if latitude and longitude:
            payload["latitude"] = latitude
            payload["longitude"] = longitude
        
        print("Sending request to API...")
        
        # Make request
        response = requests.post(
            f"{self.base_url}/identification",
            json=payload,
            headers=self.headers,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code not in [200, 201]:
            print(f"Error: {response.text}")
            response.raise_for_status()
        
        return response.json()


if __name__ == "__main__":
    # Load API key from environment variable
    API_KEY = os.getenv("CROP_HEALTH_API_KEY")
    
    if not API_KEY:
        print("ERROR: CROP_HEALTH_API_KEY not found in environment variables")
        print("Please create a .env file with: CROP_HEALTH_API_KEY=your_api_key")
        exit(1)
    
    # Initialize API
    api = CropHealthAPI(API_KEY)
    
    # Your image file - UPDATE THIS PATH
    image_path = "2.jpg"  # Change to your actual image filename
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Available files: {[f for f in os.listdir('.') if f.endswith(('.jpg', '.jpeg', '.png'))]}")
        exit(1)
    
    try:
        # Detect disease
        print("\n=== Starting Disease Detection ===\n")
        result = api.detect_disease(
            image_path=image_path,
            latitude=18.5204,  # Pune
            longitude=73.8567
        )
        
        # Display results
        print("\n=== RESULTS ===\n")
        
        if 'suggestions' in result and result['suggestions']:
            for i, suggestion in enumerate(result['suggestions'][:3], 1):
                print(f"{i}. {suggestion.get('name', 'Unknown')}")
                print(f"   Confidence: {suggestion.get('probability', 0):.1%}")
                print()
        
        # Full response
        print("\nFull API response:")
        import json
        print(json.dumps(result, indent=2))
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
    except requests.exceptions.RequestException as e:
        print(f"API ERROR: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")