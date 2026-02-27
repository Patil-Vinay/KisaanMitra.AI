"""
Smart AI Orchestration Layer
- AI thinks before responding
- Multi-agent collaboration
- Context-aware responses
- Confidence scoring
- Response caching for performance
"""

import json
import hashlib
import time  # Import at module level


# Simple in-memory cache (Lambda container reuse)
_intent_cache = {}
_cache_ttl = 1800  # 30 minutes (increased from 5 for better performance)


class AIOrchestrator:
    """Orchestrates AI responses with reasoning and confidence"""
    
    def __init__(self, bedrock_client):
        self.bedrock = bedrock_client
        self.confidence_threshold = 0.7
    
    def analyze_intent(self, user_message, conversation_history=""):
        """
        Deep intent analysis before routing
        Returns: {intent, confidence, entities, reasoning}
        """
        # OPTIMIZATION: Check cache first
        cache_key = hashlib.md5(f"{user_message[:100]}".encode()).hexdigest()
        if cache_key in _intent_cache:
            cached_data, timestamp = _intent_cache[cache_key]
            if time.time() - timestamp < _cache_ttl:
                print(f"[AI ORCHESTRATOR] Using cached intent analysis")
                return cached_data
        
        # OPTIMIZATION: Use keyword-based detection first (90% of cases)
        # Only use AI for ambiguous queries
        message_lower = user_message.lower()
        
        # Check for crop recommendation queries (which crop, what to plant, suggest crop)
        crop_rec_keywords = ['which crop', 'what crop', 'suggest crop', 'recommend crop', 
                             'should i plant', 'what to plant', 'which to grow', 'what to grow',
                             'कौन सी फसल', 'क्या लगाएं', 'क्या उगाएं', 'फसल सुझाव']
        if any(kw in message_lower for kw in crop_rec_keywords):
            print(f"[AI ORCHESTRATOR] Crop recommendation query detected, routing to general agent")
            return {
                "primary_intent": "general",
                "confidence": 0.95,
                "entities": {},
                "reasoning": "User asking for crop recommendation advice",
                "clarification_needed": False
            }
        
        # OPTIMIZATION: Expand keyword detection to avoid AI calls
        if any(phrase in message_lower for phrase in ['बजट योजना', 'budget plan', 'budget planning', 'फसल स्वास्थ्य', 'crop health', 'बाजार भाव', 'market price', 'disease', 'sick', 'yellow', 'spots', 'रोग', 'बीमारी', 'price', 'rate', 'bhav', 'भाव', 'दाम', 'cost', 'finance', 'loan', 'खर्च', 'योजना', 'लागत']):
            print(f"[AI ORCHESTRATOR] Clear keyword detected, using fast routing (no AI call)")
            return self._fallback_intent_analysis(user_message)
        
        # Check if recent context indicates budget planning (MUST check BEFORE AI analysis)
        if conversation_history:
            history_lower = conversation_history.lower()
            
            # Check if user just clicked Budget Planning menu or asked about budget
            if ('budget planning' in history_lower or 'बजट योजना' in history_lower or 
                'which crop?' in history_lower or 'कौन सी फसल?' in history_lower):
                # If user now provides crop/land/location details, it's DEFINITELY budget
                has_crop = any(crop in message_lower for crop in ['tomato', 'onion', 'wheat', 'rice', 'cotton', 'sugarcane', 'potato', 'टमाटर', 'प्याज', 'गेहूं'])
                has_land = any(word in message_lower for word in ['acre', 'hectare', 'एकड़', 'हेक्टेयर'])
                has_location = any(word in message_lower for word in ['kolhapur', 'pune', 'mumbai', 'nashik', 'पुणे', 'मुंबई', 'delhi', 'jaipur'])
                
                if has_crop or has_land or has_location:
                    print(f"[AI ORCHESTRATOR] Context indicates budget query with details (crop={has_crop}, land={has_land}, location={has_location})")
                    return {
                        "primary_intent": "budget",
                        "confidence": 0.98,
                        "entities": {},
                        "reasoning": "User providing crop/land/location details after Budget Planning menu selection",
                        "clarification_needed": False
                    }
        
        prompt = f"""Analyze this farmer's message deeply:

Message: "{user_message}"

Recent conversation:
{conversation_history}

Provide a JSON response with:
1. primary_intent: Main goal (crop_health, market_price, budget, general, emergency)
2. confidence: 0.0-1.0 (how sure are you?)
3. entities: {{crop, location, disease, quantity, etc}}
4. reasoning: Why you chose this intent
5. clarification_needed: true/false (ONLY true if message is very vague like "help" or "what")
6. suggested_question: If clarification needed

IMPORTANT CONTEXT RULES:
- If recent conversation mentions "budget" or "बजट" and user provides crop/land/location, it's BUDGET intent
- If user mentions land size (acre, hectare) with crop name, it's likely BUDGET not crop_health
- If user mentions budget, बजट, योजना, cost, खर्च - set confidence HIGH (0.9+) and clarification_needed: false

Example:
{{
  "primary_intent": "budget",
  "confidence": 0.9,
  "entities": {{"crop": "tomato", "land_size": "1 acre", "location": "Kolhapur"}},
  "reasoning": "User explicitly asks for finance structure with clear details",
  "clarification_needed": false,
  "suggested_question": null
}}

Respond ONLY with valid JSON:"""
        
        try:
            # OPTIMIZED: Better retry logic with longer waits
            max_retries = 3
            base_wait = 2  # Reduced from 5 for faster retries
            
            for attempt in range(max_retries):
                try:
                    response = self.bedrock.converse(
                        modelId="us.amazon.nova-micro-v1:0",  # Nova Micro - Ultra fast, 100 req/min
                        messages=[{"role": "user", "content": [{"text": prompt}]}],
                        inferenceConfig={"maxTokens": 800, "temperature": 0.1}  # Low temp for precision
                    )
                    break
                except Exception as e:
                    if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                        wait_time = base_wait * (attempt + 1)  # 2, 4, 6 seconds (linear)
                        print(f"[AI ORCHESTRATOR] Throttled, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        raise
            
            result_text = response["output"]["message"]["content"][0]["text"].strip()
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(result_text)
            print(f"[AI ORCHESTRATOR] Intent: {analysis['primary_intent']}, Confidence: {analysis['confidence']}")
            
            # Cache the result
            _intent_cache[cache_key] = (analysis, time.time())
            
            return analysis
        except Exception as e:
            print(f"[AI ORCHESTRATOR ERROR] {e}")
            # Fallback to keyword-based
            return self._fallback_intent_analysis(user_message)
    
    def _fallback_intent_analysis(self, message):
        """Fallback intent detection"""
        message_lower = message.lower()
        
        # Check for crop recommendation queries FIRST (highest priority for general queries)
        crop_rec_keywords = ['which crop', 'what crop', 'suggest crop', 'recommend crop', 
                             'should i plant', 'what to plant', 'which to grow', 'what to grow',
                             'कौन सी फसल', 'क्या लगाएं', 'क्या उगाएं', 'फसल सुझाव']
        if any(kw in message_lower for kw in crop_rec_keywords):
            return {
                "primary_intent": "general",
                "confidence": 0.95,
                "entities": {},
                "reasoning": "User asking for crop recommendation advice",
                "clarification_needed": False
            }
        
        # Check for explicit service requests (high confidence)
        if any(word in message_lower for word in ['बजट योजना', 'budget plan', 'budget planning']):
            return {
                "primary_intent": "budget",
                "confidence": 0.95,
                "entities": {},
                "reasoning": "User explicitly requested budget planning service",
                "clarification_needed": False
            }
        
        if any(word in message_lower for word in ['disease', 'sick', 'problem', 'yellow', 'spots', 'रोग', 'बीमारी', 'फसल स्वास्थ्य', 'crop health']):
            return {
                "primary_intent": "crop_health",
                "confidence": 0.85,
                "entities": {},
                "reasoning": "Keywords indicate crop health issue",
                "clarification_needed": False
            }
        elif any(word in message_lower for word in ['price', 'rate', 'market', 'bhav', 'भाव', 'दाम', 'बाजार भाव', 'market price']):
            return {
                "primary_intent": "market_price",
                "confidence": 0.85,
                "entities": {},
                "reasoning": "Keywords indicate market price query",
                "clarification_needed": False
            }
        elif any(word in message_lower for word in ['budget', 'cost', 'finance', 'loan', 'बजट', 'खर्च', 'योजना', 'लागत']):
            return {
                "primary_intent": "budget",
                "confidence": 0.85,
                "entities": {},
                "reasoning": "Keywords indicate budget/finance query",
                "clarification_needed": False
            }
        else:
            return {
                "primary_intent": "general",
                "confidence": 0.5,
                "entities": {},
                "reasoning": "No clear intent detected",
                "clarification_needed": True,
                "suggested_question": "क्या आप फसल की जांच, बाजार भाव, या बजट योजना के बारे में पूछना चाहते हैं?"
            }
    
    def should_ask_clarification(self, analysis):
        """Check if we should ask for clarification"""
        # NEVER ask for clarification if confidence >= threshold
        # ONLY ask if explicitly marked as needing clarification
        return analysis.get('clarification_needed', False)
    
    def consult_agents(self, intent, user_message, context):
        """
        Multi-agent consultation for complex queries
        Returns: {agent_responses, consensus, confidence}
        """
        # For complex queries, get input from multiple agents
        if intent in ['budget', 'crop_health']:
            print(f"[AI ORCHESTRATOR] Consulting multiple agents for {intent}")
            # This would call multiple agents and synthesize responses
            # For now, return single agent response
            return {
                "primary_agent": intent,
                "consultation_needed": False,
                "confidence": 0.9
            }
        
        return {
            "primary_agent": intent,
            "consultation_needed": False,
            "confidence": 1.0
        }
    
    def generate_reasoning_response(self, user_message, agent_response, context):
        """
        Add reasoning layer to agent response
        Makes AI explain its thinking
        
        OPTIMIZATION: DISABLED for performance (adds 14+ seconds)
        """
        # DISABLED: This adds 14+ seconds per message
        # For critical decisions (budget, disease), add reasoning
        # Keeping code for future use if needed
        return agent_response
    
    def calculate_response_confidence(self, response_text):
        """Calculate confidence in the response"""
        # Simple heuristic - can be improved
        confidence_indicators = {
            'high': ['definitely', 'clearly', 'certainly', 'निश्चित', 'पक्का'],
            'medium': ['probably', 'likely', 'शायद', 'संभव'],
            'low': ['maybe', 'unsure', 'not sure', 'पता नहीं']
        }
        
        response_lower = response_text.lower()
        
        if any(word in response_lower for word in confidence_indicators['high']):
            return 0.9
        elif any(word in response_lower for word in confidence_indicators['low']):
            return 0.5
        else:
            return 0.7


# Global orchestrator instance
orchestrator = None

def get_orchestrator(bedrock_client):
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = AIOrchestrator(bedrock_client)
    return orchestrator
