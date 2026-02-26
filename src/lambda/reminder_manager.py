"""
Smart Reminders & Task Management
"""
import boto3
import json
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
events = boto3.client('events', region_name='ap-south-1')
lambda_client = boto3.client('lambda', region_name='ap-south-1')

def get_crop_calendar(crop_name):
    """Get standard crop calendar with tasks"""
    calendars = {
        'tomato': [
            {'task': 'पहली खाद डालें (First fertilizer)', 'days': 15},
            {'task': 'पहला स्प्रे करें (First spray)', 'days': 20},
            {'task': 'दूसरी खाद डालें (Second fertilizer)', 'days': 30},
            {'task': 'दूसरा स्प्रे करें (Second spray)', 'days': 40},
            {'task': 'तीसरी खाद डालें (Third fertilizer)', 'days': 50},
            {'task': 'कटाई शुरू करें (Start harvesting)', 'days': 75}
        ],
        'rice': [
            {'task': 'पहली खाद डालें', 'days': 20},
            {'task': 'पहला स्प्रे करें', 'days': 30},
            {'task': 'दूसरी खाद डालें', 'days': 45},
            {'task': 'दूसरा स्प्रे करें', 'days': 60},
            {'task': 'कटाई की तैयारी', 'days': 110}
        ],
        'wheat': [
            {'task': 'पहली खाद डालें', 'days': 20},
            {'task': 'पहली सिंचाई करें', 'days': 25},
            {'task': 'दूसरी खाद डालें', 'days': 40},
            {'task': 'कटाई की तैयारी', 'days': 120}
        ],
        'onion': [
            {'task': 'पहली खाद डालें', 'days': 15},
            {'task': 'निराई-गुड़ाई करें', 'days': 25},
            {'task': 'दूसरी खाद डालें', 'days': 35},
            {'task': 'कटाई शुरू करें', 'days': 90}
        ],
        'potato': [
            {'task': 'पहली खाद डालें', 'days': 20},
            {'task': 'मिट्टी चढ़ाएं', 'days': 30},
            {'task': 'दूसरी खाद डालें', 'days': 40},
            {'task': 'कटाई शुरू करें', 'days': 80}
        ],
        'sugarcane': [
            {'task': 'पहली खाद डालें', 'days': 30},
            {'task': 'पहली सिंचाई करें', 'days': 45},
            {'task': 'दूसरी खाद डालें', 'days': 90},
            {'task': 'तीसरी खाद डालें', 'days': 180},
            {'task': 'कटाई की तैयारी', 'days': 330}
        ],
        'cotton': [
            {'task': 'पहली खाद डालें', 'days': 20},
            {'task': 'पहला स्प्रे करें', 'days': 30},
            {'task': 'दूसरी खाद डालें', 'days': 50},
            {'task': 'कटाई शुरू करें', 'days': 150}
        ]
    }
    
    # Default calendar for unknown crops
    default = [
        {'task': 'पहली खाद डालें', 'days': 20},
        {'task': 'पहला स्प्रे करें', 'days': 30},
        {'task': 'दूसरी खाद डालें', 'days': 45}
    ]
    
    return calendars.get(crop_name.lower(), default)

def format_reminders_message(crop_name, calendar):
    """Format reminders message"""
    message = f"\n\n⏰ *स्वचालित रिमाइंडर सेट*:\n"
    message += f"आपको {crop_name} के लिए निम्न कार्यों की याद दिलाई जाएगी:\n\n"
    
    for i, task in enumerate(calendar[:5], 1):  # Show first 5
        message += f"{i}. {task['task']} - {task['days']} दिन में\n"
    
    if len(calendar) > 5:
        message += f"\n...और {len(calendar) - 5} अन्य कार्य\n"
    
    message += "\n💡 आपको WhatsApp पर समय पर याद दिलाया जाएगा!"
    
    return message
