"""
Enhanced Crop Disease Detection with Confidence Scores
- Multi-disease detection
- Confidence scoring
- Treatment recommendations with success rates
- Follow-up questions
"""

import json
import base64


def detect_disease_with_confidence(image_data, bedrock_client):
    """
    Enhanced disease detection with confidence scores
    Returns: {
        primary_disease, 
        confidence, 
        alternative_diseases, 
        treatments,
        follow_up_questions
    }
    """
    
    prompt = """You are an expert plant pathologist. Analyze this crop image and provide a detailed diagnosis.

**CRITICAL**: Respond with ONLY valid JSON in this EXACT format:

{
  "primary_disease": "Disease name in English",
  "primary_disease_hindi": "रोग का नाम हिंदी में",
  "confidence": 0.85,
  "severity": "mild/moderate/severe",
  "alternative_diseases": [
    {"name": "Alternative disease 1", "probability": 0.10},
    {"name": "Alternative disease 2", "probability": 0.05"}
  ],
  "symptoms_observed": ["symptom1", "symptom2"],
  "treatments": [
    {
      "method": "Treatment name",
      "method_hindi": "उपचार का नाम",
      "success_rate": 0.90,
      "application": "How to apply",
      "cost_estimate": "₹500-1000"
    }
  ],
  "preventive_measures": ["measure1", "measure2"],
  "follow_up_questions": ["Question to ask farmer for better diagnosis"],
  "urgency": "immediate/within_week/routine"
}

**RULES:**
1. confidence: 0.0-1.0 (be honest about uncertainty)
2. If confidence < 0.7, suggest follow-up questions
3. Provide 2-3 treatment options ranked by success rate
4. Include cost estimates for treatments
5. Specify urgency level

Analyze the image now:"""

    try:
        # Prepare image for Bedrock
        if isinstance(image_data, str):
            # If base64 string
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data
        
        response = bedrock_client.converse(
            modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {"bytes": image_bytes}
                        }
                    },
                    {"text": prompt}
                ]
            }],
            inferenceConfig={"maxTokens": 2000, "temperature": 0.2}
        )
        
        result_text = response["output"]["message"]["content"][0]["text"].strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        diagnosis = json.loads(result_text)
        
        print(f"[DISEASE DETECTION] Primary: {diagnosis['primary_disease']}, Confidence: {diagnosis['confidence']}")
        
        return diagnosis
        
    except Exception as e:
        print(f"[DISEASE DETECTION ERROR] {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to simple detection
        return {
            "primary_disease": "Unable to detect",
            "primary_disease_hindi": "पहचान नहीं हो सका",
            "confidence": 0.0,
            "severity": "unknown",
            "alternative_diseases": [],
            "symptoms_observed": [],
            "treatments": [],
            "preventive_measures": [],
            "follow_up_questions": ["कृपया फसल की पत्तियों की स्पष्ट तस्वीर भेजें"],
            "urgency": "routine"
        }


def format_disease_response(diagnosis):
    """Format disease diagnosis into user-friendly message"""
    
    confidence = diagnosis['confidence']
    
    # Confidence indicator
    if confidence >= 0.8:
        confidence_emoji = "🟢"
        confidence_text = "उच्च विश्वास"
    elif confidence >= 0.6:
        confidence_emoji = "🟡"
        confidence_text = "मध्यम विश्वास"
    else:
        confidence_emoji = "🔴"
        confidence_text = "कम विश्वास"
    
    # Urgency indicator
    urgency_emoji = {
        "immediate": "🚨",
        "within_week": "⚠️",
        "routine": "ℹ️"
    }.get(diagnosis.get('urgency', 'routine'), "ℹ️")
    
    message = f"{confidence_emoji} *फसल रोग निदान*\n\n"
    message += f"*रोग*: {diagnosis['primary_disease_hindi']}\n"
    message += f"*विश्वास स्तर*: {confidence_text} ({int(confidence*100)}%)\n"
    message += f"*गंभीरता*: {diagnosis.get('severity', 'unknown')}\n"
    message += f"{urgency_emoji} *तात्कालिकता*: {diagnosis.get('urgency', 'routine')}\n\n"
    
    # Symptoms
    if diagnosis.get('symptoms_observed'):
        message += "*लक्षण देखे गए*:\n"
        for symptom in diagnosis['symptoms_observed'][:3]:
            message += f"• {symptom}\n"
        message += "\n"
    
    # Treatments
    if diagnosis.get('treatments'):
        message += "*💊 उपचार (सफलता दर के अनुसार)*:\n\n"
        for i, treatment in enumerate(diagnosis['treatments'][:3], 1):
            success_rate = int(treatment.get('success_rate', 0) * 100)
            message += f"{i}. *{treatment['method_hindi']}*\n"
            message += f"   ✅ सफलता: {success_rate}%\n"
            message += f"   💰 लागत: {treatment.get('cost_estimate', 'N/A')}\n"
            message += f"   📝 {treatment.get('application', '')}\n\n"
    
    # Alternative diseases
    if diagnosis.get('alternative_diseases') and confidence < 0.8:
        message += "*🔍 अन्य संभावनाएं*:\n"
        for alt in diagnosis['alternative_diseases'][:2]:
            prob = int(alt.get('probability', 0) * 100)
            message += f"• {alt['name']} ({prob}%)\n"
        message += "\n"
    
    # Preventive measures
    if diagnosis.get('preventive_measures'):
        message += "*🛡️ रोकथाम*:\n"
        for measure in diagnosis['preventive_measures'][:3]:
            message += f"• {measure}\n"
        message += "\n"
    
    # Follow-up questions if low confidence
    if confidence < 0.7 and diagnosis.get('follow_up_questions'):
        message += "*❓ बेहतर निदान के लिए*:\n"
        for question in diagnosis['follow_up_questions'][:2]:
            message += f"• {question}\n"
        message += "\n"
    
    # Confidence warning
    if confidence < 0.6:
        message += "⚠️ *चेतावनी*: कम विश्वास स्तर। कृपया स्थानीय कृषि विशेषज्ञ से संपर्क करें।\n\n"
    
    message += "💡 *सुझाव*: उपचार से पहले छोटे क्षेत्र में परीक्षण करें।"
    
    return message


def get_disease_history(user_id, dynamodb_table):
    """Get farmer's disease detection history"""
    try:
        response = dynamodb_table.query(
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,
            Limit=5
        )
        return response.get('Items', [])
    except:
        return []


def save_disease_detection(user_id, diagnosis, dynamodb_table):
    """Save disease detection for history tracking"""
    import time
    
    try:
        item = {
            'user_id': user_id,
            'timestamp': str(int(time.time())),
            'disease': diagnosis['primary_disease'],
            'confidence': diagnosis['confidence'],
            'severity': diagnosis.get('severity', 'unknown'),
            'treatments_suggested': len(diagnosis.get('treatments', []))
        }
        dynamodb_table.put_item(Item=item)
        print(f"[DISEASE HISTORY] Saved detection for user {user_id}")
    except Exception as e:
        print(f"[DISEASE HISTORY ERROR] {e}")
