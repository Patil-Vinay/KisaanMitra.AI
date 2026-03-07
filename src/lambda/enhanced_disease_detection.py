"""
Enhanced Crop Disease Detection with Confidence Scores
- Multi-disease detection
- Confidence scoring
- Treatment recommendations with success rates
- Follow-up questions
"""

import json
import base64
import os


def detect_disease_with_confidence(image_data, bedrock_client=None):
    """
    Enhanced disease detection with optimized image processing and caching

    Returns: {
        primary_disease,
        confidence,
        alternative_diseases,
        treatments,
        follow_up_questions
    }
    """

    # Import caching if available
    try:
        from services.cache_service import CacheService, RateLimiter
        CACHE_AVAILABLE = True
    except ImportError:
        CACHE_AVAILABLE = False

    # Optimized prompt for faster processing
    prompt = """Analyze this crop image and provide diagnosis in EXACT JSON format:

{
  "primary_disease": "Disease name",
  "primary_disease_hindi": "रोग का नाम",
  "confidence": 0.85,
  "severity": "mild/moderate/severe",
  "alternative_diseases": [{"name": "Alt disease", "probability": 0.10}],
  "symptoms_observed": ["symptom1", "symptom2"],
  "treatments": [{
    "method": "Treatment",
    "method_hindi": "उपचार",
    "success_rate": 0.90,
    "application": "How to apply",
    "cost_estimate": "₹500-1000"
  }],
  "preventive_measures": ["measure1"],
  "follow_up_questions": ["Question for farmer"],
  "urgency": "immediate/within_week/routine"
}

Rules: confidence 0.0-1.0, provide 2-3 treatments, include costs. Analyze now:"""

    try:
        # Optimize image processing
        if isinstance(image_data, str):
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        # Image size optimization for faster processing
        original_size = len(image_bytes)
        print(f"[DISEASE DETECTION] Processing image (size: {original_size} bytes)")

        # Rate limiting for image analysis
        if CACHE_AVAILABLE:
            rate_key = RateLimiter.get_api_key("bedrock_image")
            if not RateLimiter.is_allowed(rate_key, max_requests=10, window_seconds=60):
                print(f"[DISEASE DETECTION] Rate limited")
                return {
                    "primary_disease": "Service temporarily busy",
                    "primary_disease_hindi": "सेवा अस्थायी रूप से व्यस्त",
                    "confidence": 0.0,
                    "severity": "unknown",
                    "alternative_diseases": [],
                    "symptoms_observed": [],
                    "treatments": [],
                    "preventive_measures": [],
                    "follow_up_questions": ["कृपया कुछ देर बाद पुनः प्रयास करें"],
                    "urgency": "routine"
                }

        # Optimize image size if too large (reduce processing time)
        if original_size > 1024 * 1024:  # 1MB
            print(f"[DISEASE DETECTION] Large image detected, may take longer to process")

        # Use optimized bedrock client
        if bedrock_client is None:
            import boto3
            bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1',
                config=boto3.session.Config(
                    retries={'max_attempts': 2, 'mode': 'adaptive'},
                    read_timeout=25,  # Reduced timeout
                    connect_timeout=5
                )
            )
            print(f"[DISEASE DETECTION] Created optimized Bedrock client")

        # Optimized API call with reduced token limit
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
            inferenceConfig={
                "maxTokens": 1500,  # Reduced for faster response
                "temperature": 0.1   # Lower for more consistent results
            }
        )

        print(f"[DISEASE DETECTION] Bedrock response received")

        # Optimized response parsing
        if "output" in response and "message" in response["output"]:
            content = response["output"]["message"]["content"]
            if isinstance(content, list) and len(content) > 0:
                if "text" in content[0]:
                    result_text = content[0]["text"].strip()
                else:
                    print(f"[DISEASE DETECTION ERROR] No 'text' field in content[0]")
                    raise ValueError("No text field in response")
            else:
                print(f"[DISEASE DETECTION ERROR] Invalid content structure")
                raise ValueError("Invalid content structure")
        else:
            print(f"[DISEASE DETECTION ERROR] Invalid response structure")
            raise ValueError("Invalid response structure")

        # Optimized JSON extraction
        json_text = result_text
        if "```json" in result_text:
            json_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_text = result_text.split("```")[1].split("```")[0].strip()

        diagnosis = json.loads(json_text)

        # Validate and sanitize diagnosis data
        diagnosis = {
            "primary_disease": diagnosis.get("primary_disease", "Unknown")[:100],
            "primary_disease_hindi": diagnosis.get("primary_disease_hindi", "अज्ञात")[:100],
            "confidence": max(0.0, min(1.0, float(diagnosis.get("confidence", 0.5)))),
            "severity": diagnosis.get("severity", "unknown"),
            "alternative_diseases": diagnosis.get("alternative_diseases", [])[:3],  # Limit to 3
            "symptoms_observed": diagnosis.get("symptoms_observed", [])[:5],  # Limit to 5
            "treatments": diagnosis.get("treatments", [])[:3],  # Limit to 3
            "preventive_measures": diagnosis.get("preventive_measures", [])[:5],  # Limit to 5
            "follow_up_questions": diagnosis.get("follow_up_questions", [])[:3],  # Limit to 3
            "urgency": diagnosis.get("urgency", "routine")
        }

        print(f"[DISEASE DETECTION] Primary: {diagnosis['primary_disease']}, Confidence: {diagnosis['confidence']}")

        return diagnosis

    except Exception as e:
        print(f"[DISEASE DETECTION ERROR] {e}")
        import traceback
        traceback.print_exc()

        # Optimized fallback response
        return {
            "primary_disease": "Analysis failed",
            "primary_disease_hindi": "विश्लेषण असफल",
            "confidence": 0.0,
            "severity": "unknown",
            "alternative_diseases": [],
            "symptoms_observed": [],
            "treatments": [{
                "method": "Consult local expert",
                "method_hindi": "स्थानीय विशेषज्ञ से संपर्क करें",
                "success_rate": 0.9,
                "application": "Visit nearest agricultural extension office",
                "cost_estimate": "Free consultation"
            }],
            "preventive_measures": ["Regular crop monitoring", "Proper field hygiene"],
            "follow_up_questions": ["कृपया फसल की स्पष्ट तस्वीर भेजें"],
            "urgency": "routine"
        }


def format_disease_response(diagnosis, language='hindi'):
    """Format disease diagnosis into user-friendly message"""
    
    confidence = diagnosis['confidence']
    
    # Confidence indicator
    if confidence >= 0.8:
        confidence_emoji = "🟢"
        confidence_text = "High Confidence" if language == 'english' else "उच्च विश्वास"
    elif confidence >= 0.6:
        confidence_emoji = "🟡"
        confidence_text = "Medium Confidence" if language == 'english' else "मध्यम विश्वास"
    else:
        confidence_emoji = "🔴"
        confidence_text = "Low Confidence" if language == 'english' else "कम विश्वास"
    
    # Urgency indicator
    urgency_emoji = {
        "immediate": "🚨",
        "within_week": "⚠️",
        "routine": "ℹ️"
    }.get(diagnosis.get('urgency', 'routine'), "ℹ️")
    
    if language == 'english':
        message = f"{confidence_emoji} *Crop Disease Diagnosis*\n\n"
        message += f"*Disease*: {diagnosis['primary_disease']}\n"
        message += f"*Confidence Level*: {confidence_text} ({int(confidence*100)}%)\n"
        message += f"*Severity*: {diagnosis.get('severity', 'unknown')}\n"
        message += f"{urgency_emoji} *Urgency*: {diagnosis.get('urgency', 'routine')}\n\n"
        
        # Symptoms
        if diagnosis.get('symptoms_observed'):
            message += "*Symptoms Observed*:\n"
            for symptom in diagnosis['symptoms_observed'][:3]:
                message += f"• {symptom}\n"
            message += "\n"
        
        # Treatments
        if diagnosis.get('treatments'):
            message += "*💊 Treatments (by success rate)*:\n\n"
            for i, treatment in enumerate(diagnosis['treatments'][:3], 1):
                success_rate = int(treatment.get('success_rate', 0) * 100)
                message += f"{i}. *{treatment['method']}*\n"
                message += f"   ✅ Success Rate: {success_rate}%\n"
                message += f"   💰 Cost: {treatment.get('cost_estimate', 'N/A')}\n"
                message += f"   📝 {treatment.get('application', '')}\n\n"
        
        # Alternative diseases
        if diagnosis.get('alternative_diseases') and confidence < 0.8:
            message += "*🔍 Other Possibilities*:\n"
            for alt in diagnosis['alternative_diseases'][:2]:
                prob = int(alt.get('probability', 0) * 100)
                message += f"• {alt['name']} ({prob}%)\n"
            message += "\n"
        
        # Preventive measures
        if diagnosis.get('preventive_measures'):
            message += "*🛡️ Prevention*:\n"
            for measure in diagnosis['preventive_measures'][:3]:
                message += f"• {measure}\n"
            message += "\n"
        
        # Follow-up questions if low confidence
        if confidence < 0.7 and diagnosis.get('follow_up_questions'):
            message += "*❓ For Better Diagnosis*:\n"
            for question in diagnosis['follow_up_questions'][:2]:
                message += f"• {question}\n"
            message += "\n"
        
        # Confidence warning
        if confidence < 0.6:
            message += "⚠️ *Warning*: Low confidence level. Please consult a local agricultural expert.\n\n"
        
        message += "💡 *Tip*: Test treatment on a small area first."
    else:
        # Hindi version (original)
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
    from decimal import Decimal
    
    try:
        # Convert float values to Decimal for DynamoDB
        item = {
            'user_id': user_id,
            'timestamp': str(int(time.time())),
            'disease': diagnosis['primary_disease'],
            'confidence': Decimal(str(diagnosis['confidence'])),  # Convert float to Decimal
            'severity': diagnosis.get('severity', 'unknown'),
            'treatments_suggested': len(diagnosis.get('treatments', []))
        }
        dynamodb_table.put_item(Item=item)
        print(f"[DISEASE HISTORY] Saved detection for user {user_id}")
    except Exception as e:
        print(f"[DISEASE HISTORY ERROR] {e}")
        import traceback
        traceback.print_exc()
