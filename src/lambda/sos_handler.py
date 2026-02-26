"""
Emergency SOS & Expert Connect
"""
import boto3
import time
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

def handle_sos(user_id, message, user_profile=None):
    """Handle emergency SOS request"""
    sos_id = f"{user_id}_{int(time.time())}"
    
    farmer_name = user_profile.get('name', 'Unknown') if user_profile else 'Unknown'
    location = user_profile.get('village', 'Unknown') if user_profile else 'Unknown'
    
    print(f"[SOS] Emergency from {farmer_name} ({user_id}): {message}")
    
    # Format SOS response
    response = f"""🆘 *आपातकालीन सहायता सक्रिय!*

हम आपकी मदद कर रहे हैं।

*तुरंत मदद के लिए कॉल करें*:
📞 किसान हेल्पलाइन: 1800-180-1551
📞 कृषि विभाग: 1800-180-1551
📞 मौसम जानकारी: 1800-180-1555

*आपकी समस्या*: {message}

*स्थिति*: उच्च प्राथमिकता
*SOS ID*: {sos_id}

💡 कृपया अपनी समस्या का विस्तार से वर्णन करें। हम जल्द से जल्द जवाब देंगे।"""
    
    return response

def get_helpline_numbers():
    """Get relevant helpline numbers"""
    return {
        'kisan_helpline': '1800-180-1551',
        'agri_dept': '1800-180-1551',
        'weather': '1800-180-1555',
        'pm_kisan': '155261',
        'soil_health': '1800-180-1551'
    }
