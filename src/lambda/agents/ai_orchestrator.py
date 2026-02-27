"""
Smart AI Orchestration Layer
- AI thinks before responding
- Multi-agent collaboration
- Context-aware responses
- Confidence scoring
"""

import json


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
        # First check for explicit service requests (skip AI analysis)
        message_lower = user_message.lower()
        if any(phrase in message_lower for phrase in ['बजट योजना', 'budget plan', 'budget planning', 'फसल स्वास्थ्य', 'crop health', 'बाजार भाव', 'market price']):
            print(f"[AI ORCHESTRATOR] Explicit service request detected, skipping AI analysis")
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
            # Retry logic with exponential backoff
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.bedrock.converse(
                        modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Claude 3.5 Sonnet - Best reasoning
                        messages=[{"role": "user", "content": [{"text": prompt}]}],
                        inferenceConfig={"maxTokens": 800, "temperature": 0.1}  # Low temp for precision
                    )
                    break
                except Exception as e:
                    if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
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
            return analysis
        except Exception as e:
            print(f"[AI ORCHESTRATOR ERROR] {e}")
            # Fallback to keyword-based
            return self._fallback_intent_analysis(user_message)
    
    def _fallback_intent_analysis(self, message):
        """Fallback intent detection"""
        message_lower = message.lower()
        
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
        """
        # For critical decisions (budget, disease), add reasoning
        if "budget" in agent_response.lower() or "disease" in agent_response.lower():
            reasoning_prompt = f"""You provided this response to a farmer:

Response: {agent_response[:500]}

Add a brief "Why I recommend this" section (2-3 lines in Hindi) explaining your reasoning.
Keep it simple and farmer-friendly.

Format:
💡 *मेरी सिफारिश क्यों*:
[Your reasoning in 2-3 lines]

Respond with ONLY the reasoning section:"""
            
            try:
                response = self.bedrock.converse(
                    modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Claude 3.5 Sonnet - Best reasoning
                    messages=[{"role": "user", "content": [{"text": reasoning_prompt}]}],
                    inferenceConfig={"maxTokens": 300, "temperature": 0.2}
                )
                
                reasoning = response["output"]["message"]["content"][0]["text"].strip()
                return f"{agent_response}\n\n{reasoning}"
            except:
                return agent_response
        
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
