# 🎯 Quick Implementation Guide - Remaining 7 Features

## Priority 1: Feature 8 - Smart Reminders (4 hours)

### Step 1: Create DynamoDB Table
```bash
aws dynamodb create-table \
    --table-name kisaanmitra-reminders \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=reminder_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=reminder_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1
```

### Step 2: Create reminder_manager.py
```python
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
reminders_table = dynamodb.Table('kisaanmitra-reminders')
events = boto3.client('events', region_name='ap-south-1')

def set_reminder(user_id, task, days_from_now, crop_name):
    """Set farming task reminder"""
    reminder_date = datetime.now() + timedelta(days=days_from_now)
    reminder_id = f"{crop_name}_{task}_{reminder_date.strftime('%Y%m%d')}"
    
    reminders_table.put_item(Item={
        'user_id': user_id,
        'reminder_id': reminder_id,
        'task': task,
        'crop': crop_name,
        'date': reminder_date.isoformat(),
        'status': 'pending'
    })
    
    # Create EventBridge rule
    rule_name = f"reminder-{user_id}-{reminder_id}"
    events.put_rule(
        Name=rule_name,
        ScheduleExpression=f"cron(0 8 {reminder_date.day} {reminder_date.month} ? {reminder_date.year})",
        State='ENABLED'
    )
    
    # Add Lambda target
    events.put_targets(
        Rule=rule_name,
        Targets=[{
            'Id': '1',
            'Arn': 'arn:aws:lambda:ap-south-1:YOUR_ACCOUNT:function:whatsapp-llama-bot',
            'Input': json.dumps({
                'type': 'reminder',
                'user_id': user_id,
                'task': task,
                'crop': crop_name
            })
        }]
    )
    
    return f"✅ Reminder set for {task} on {reminder_date.strftime('%d %B %Y')}"

def get_crop_calendar(crop_name):
    """Get standard crop calendar"""
    calendars = {
        'tomato': [
            {'task': 'पहली खाद डालें', 'days': 15},
            {'task': 'पहला स्प्रे करें', 'days': 20},
            {'task': 'दूसरी खाद डालें', 'days': 30},
            {'task': 'दूसरा स्प्रे करें', 'days': 40},
            {'task': 'कटाई शुरू करें', 'days': 75}
        ],
        'rice': [
            {'task': 'पहली खाद डालें', 'days': 20},
            {'task': 'पहला स्प्रे करें', 'days': 30},
            {'task': 'दूसरी खाद डालें', 'days': 45},
            {'task': 'कटाई की तैयारी', 'days': 110}
        ]
    }
    return calendars.get(crop_name.lower(), [])
```

### Step 3: Integrate in Lambda
```python
# In handle_finance_query after budget generation
if budget:
    # Set automatic reminders
    calendar = get_crop_calendar(crop_name)
    for task in calendar:
        set_reminder(from_number, task['task'], task['days'], crop_name)
    
    message += "\n\n⏰ *Automatic Reminders Set*:\n"
    for task in calendar[:3]:
        message += f"• {task['task']} - {task['days']} days\n"
```

---

## Priority 2: Feature 10 - Emergency SOS (3 hours)

### Step 1: Create SNS Topic
```bash
aws sns create-topic --name AgriExperts --region ap-south-1
aws sns subscribe --topic-arn arn:aws:sns:ap-south-1:XXX:AgriExperts \
    --protocol email --notification-endpoint expert@example.com
```

### Step 2: Create sos_handler.py
```python
import boto3

sns = boto3.client('sns', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
sos_table = dynamodb.Table('kisaanmitra-sos')

def handle_sos(user_id, message, user_profile):
    """Handle emergency SOS"""
    sos_id = f"{user_id}_{int(time.time())}"
    
    # Save to database
    sos_table.put_item(Item={
        'sos_id': sos_id,
        'user_id': user_id,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'priority': 'HIGH',
        'status': 'pending',
        'farmer_name': user_profile.get('name', 'Unknown'),
        'location': user_profile.get('village', 'Unknown')
    })
    
    # Notify experts
    sns.publish(
        TopicArn='arn:aws:sns:ap-south-1:XXX:AgriExperts',
        Subject=f'🆘 Farmer SOS - {user_profile.get("name")}',
        Message=f"""
Emergency SOS from farmer:

Name: {user_profile.get('name')}
Location: {user_profile.get('village')}
Phone: {user_id}
Crops: {user_profile.get('crops')}

Issue: {message}

Respond within 15 minutes.
        """
    )
    
    return f"""🆘 *आपातकालीन सहायता सक्रिय!*

हमारे विशेषज्ञ 15 मिनट में जवाब देंगे।

तुरंत मदद के लिए:
📞 किसान हेल्पलाइन: 1800-180-1551
📞 कृषि विभाग: 1800-180-1551

आपकी समस्या: {message}
स्थिति: प्राथमिकता में

SOS ID: {sos_id}"""
```

### Step 3: Integrate in Lambda
```python
# In interactive button handler
elif button_id == "sos":
    # Ask for issue description
    send_whatsapp_message(from_number, "🆘 कृपया अपनी समस्या का वर्णन करें:")
    # Set flag to handle next message as SOS
    conversation_table.put_item(Item={
        'user_id': from_number,
        'timestamp': datetime.now().isoformat(),
        'expecting': 'sos_description'
    })

# In text message handler
# Check if expecting SOS
last_interaction = conversation_table.get_item(Key={'user_id': from_number})
if last_interaction.get('expecting') == 'sos_description':
    reply = handle_sos(from_number, user_message, user_profile)
    send_whatsapp_message(from_number, reply)
    return
```

---

## Priority 3: Feature 3 - Voice Support (5 hours)

### Step 1: Add IAM Permissions
```json
{
    "Effect": "Allow",
    "Action": [
        "transcribe:StartTranscriptionJob",
        "transcribe:GetTranscriptionJob",
        "polly:SynthesizeSpeech"
    ],
    "Resource": "*"
}
```

### Step 2: Create voice_handler.py
```python
import boto3
import base64

transcribe = boto3.client('transcribe', region_name='ap-south-1')
polly = boto3.client('polly', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')

def transcribe_audio(audio_bytes, language='hi-IN'):
    """Convert speech to text"""
    # Upload to S3
    bucket = 'kisaanmitra-audio'
    key = f"audio/{int(time.time())}.ogg"
    s3.put_object(Bucket=bucket, Key=key, Body=audio_bytes)
    
    # Start transcription
    job_name = f"transcribe-{int(time.time())}"
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f's3://{bucket}/{key}'},
        MediaFormat='ogg',
        LanguageCode=language
    )
    
    # Wait for completion
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(2)
    
    # Get transcript
    transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    response = http.request('GET', transcript_uri)
    transcript = json.loads(response.data)
    
    return transcript['results']['transcripts'][0]['transcript']

def text_to_speech(text, language='hi-IN'):
    """Convert text to speech"""
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='ogg_vorbis',
        VoiceId='Aditi',  # Hindi voice
        LanguageCode=language
    )
    
    return response['AudioStream'].read()

def send_whatsapp_audio(to, audio_bytes):
    """Send audio message via WhatsApp"""
    # Upload to S3
    bucket = 'kisaanmitra-audio'
    key = f"responses/{int(time.time())}.ogg"
    s3.put_object(Bucket=bucket, Key=key, Body=audio_bytes, ContentType='audio/ogg')
    
    # Get presigned URL
    audio_url = s3.generate_presigned_url('get_object', 
        Params={'Bucket': bucket, 'Key': key}, 
        ExpiresIn=3600)
    
    # Send via WhatsApp
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {"link": audio_url}
    }
    http.request("POST", url, body=json.dumps(data), headers=headers)
```

### Step 3: Integrate in Lambda
```python
# In lambda_handler
elif msg_type == "audio":
    print(f"[VOICE] Audio message received")
    audio_id = msg["audio"]["id"]
    
    # Download audio
    audio_bytes = download_whatsapp_audio(audio_id)
    
    # Transcribe
    text = transcribe_audio(audio_bytes, language='hi-IN')
    print(f"[VOICE] Transcribed: {text}")
    
    # Process as text
    reply = handle_message(text, from_number)
    
    # Convert to speech
    audio_response = text_to_speech(reply, language='hi-IN')
    
    # Send audio back
    send_whatsapp_audio(from_number, audio_response)
```

---

## Priority 4: Feature 5 - Weather Integration (4 hours)

### Step 1: Get OpenWeatherMap API Key
```bash
# Sign up at https://openweathermap.org/api
# Add to Lambda environment variables
aws lambda update-function-configuration \
    --function-name whatsapp-llama-bot \
    --environment Variables={OPENWEATHER_API_KEY=your_key_here} \
    --region ap-south-1
```

### Step 2: Create weather_service.py
```python
import urllib3

http = urllib3.PoolManager()

def get_weather_forecast(location):
    """Get 7-day weather forecast"""
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={location},IN&appid={api_key}&units=metric"
    
    response = http.request('GET', url)
    data = json.loads(response.data)
    
    return data

def analyze_weather_for_farming(forecast):
    """Analyze weather for farming decisions"""
    forecasts = forecast['list'][:24]  # Next 3 days (8 forecasts per day)
    
    rain_coming = False
    days_until_rain = 0
    max_temp = 0
    min_temp = 100
    
    for i, f in enumerate(forecasts):
        temp = f['main']['temp']
        max_temp = max(max_temp, temp)
        min_temp = min(min_temp, temp)
        
        if 'rain' in f and not rain_coming:
            rain_coming = True
            days_until_rain = i // 8  # Convert to days
    
    recommendations = []
    
    if rain_coming and days_until_rain <= 1:
        recommendations.append("⚠️ 24 घंटे में बारिश - अभी कीटनाशक स्प्रे करें!")
    
    if max_temp > 40:
        recommendations.append("🌡️ अत्यधिक गर्मी - सिंचाई बढ़ाएं")
    
    if min_temp < 10:
        recommendations.append("❄️ ठंड - फसल को ढकें")
    
    return {
        'rain_expected': rain_coming,
        'days_until_rain': days_until_rain,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'recommendations': recommendations
    }

def format_weather_response(location, forecast, analysis):
    """Format weather response"""
    message = f"🌤️ *मौसम पूर्वानुमान - {location}*\n\n"
    message += f"🌡️ तापमान: {analysis['min_temp']:.0f}°C - {analysis['max_temp']:.0f}°C\n"
    
    if analysis['rain_expected']:
        message += f"🌧️ बारिश: {analysis['days_until_rain']} दिन में\n"
    else:
        message += "☀️ बारिश: नहीं\n"
    
    message += "\n*🌾 कृषि सलाह*:\n"
    for rec in analysis['recommendations']:
        message += f"• {rec}\n"
    
    return message
```

### Step 3: Integrate in Budget Generation
```python
# In generate_crop_budget_with_ai_combined
# Add weather analysis
weather = get_weather_forecast(location)
weather_analysis = analyze_weather_for_farming(weather)

# Add to AI prompt
prompt += f"""

**WEATHER FORECAST (Next 3 days)**:
- Temperature: {weather_analysis['min_temp']:.0f}°C - {weather_analysis['max_temp']:.0f}°C
- Rain Expected: {weather_analysis['rain_expected']}
- Days Until Rain: {weather_analysis['days_until_rain']}

Consider weather in your feasibility analysis.
"""

# Add weather info to response
message += "\n\n" + format_weather_response(location, weather, weather_analysis)
```

---

## Quick Implementation Checklist

### Feature 8: Reminders
- [ ] Create DynamoDB table
- [ ] Create reminder_manager.py
- [ ] Integrate in budget generation
- [ ] Test reminder creation
- [ ] Test EventBridge trigger

### Feature 10: SOS
- [ ] Create SNS topic
- [ ] Create sos_handler.py
- [ ] Integrate in button handler
- [ ] Test SOS flow
- [ ] Test expert notification

### Feature 3: Voice
- [ ] Add IAM permissions
- [ ] Create S3 bucket for audio
- [ ] Create voice_handler.py
- [ ] Integrate in Lambda
- [ ] Test voice messages

### Feature 5: Weather
- [ ] Get API key
- [ ] Create weather_service.py
- [ ] Integrate in budget
- [ ] Test weather forecast
- [ ] Test recommendations

---

## Estimated Timeline

- **Day 1**: Features 8 & 10 (7 hours)
- **Day 2**: Features 3 & 5 (9 hours)
- **Day 3**: Features 9, 6, 7 (15 hours)
- **Day 4**: Testing & polish (8 hours)

**Total**: 4 days

---

## Testing Strategy

1. Unit test each feature individually
2. Integration test with WhatsApp
3. End-to-end user flow testing
4. Load testing (multiple users)
5. Error handling verification

---

**Ready to implement?** Start with Feature 8 (Reminders) - highest impact, medium complexity!
