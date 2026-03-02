"""
AI Service - Handles all AI/LLM interactions
"""
import os
import time
import boto3

USE_ANTHROPIC_DIRECT = os.environ.get('USE_ANTHROPIC_DIRECT', 'true').lower() == 'true'

if USE_ANTHROPIC_DIRECT:
    from anthropic_client import get_anthropic_client
    bedrock = get_anthropic_client()
    bedrock_for_images = boto3.client("bedrock-runtime", region_name="us-east-1")
else:
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    bedrock_for_images = bedrock


class AIService:
    """Manages AI/LLM interactions with retry logic"""
    
    @staticmethod
    def ask(prompt, system_prompt=None, conversation_context="", skip_context=False):
        """Call Bedrock/Claude with retry logic"""
        try:
            print(f"[AI] Calling Bedrock - Model: Nova Pro")
            print(f"[AI] Prompt length: {len(prompt)} chars")
            
            # Skip context for simple queries
            if skip_context:
                full_prompt = prompt
            else:
                full_prompt = conversation_context + prompt if conversation_context else prompt
            
            messages = [{"role": "user", "content": [{"text": full_prompt}]}]
            
            kwargs = {
                "modelId": "us.amazon.nova-pro-v1:0",
                "messages": messages,
                "inferenceConfig": {"maxTokens": 2000, "temperature": 0.6}
            }
            
            if system_prompt:
                kwargs["system"] = [{"text": system_prompt}]
            
            # Retry logic
            max_retries = 3
            base_wait = 2
            
            for attempt in range(max_retries):
                try:
                    response = bedrock.converse(**kwargs)
                    result = response["output"]["message"]["content"][0]["text"]
                    print(f"[AI] Response received, length: {len(result)} chars")
                    return result
                except Exception as e:
                    if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                        wait_time = base_wait * (attempt + 1)
                        print(f"[AI] Throttled, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        raise
            
        except Exception as e:
            print(f"[ERROR] AI error: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return "I'm having trouble helping you right now. Please try again."
    
    @staticmethod
    def get_image_client():
        """Get Bedrock client for image analysis"""
        return bedrock_for_images
    
    @staticmethod
    def extract_crop(user_message):
        """Extract crop name from message using AI"""
        print(f"[AI] Extracting crop name...")
        
        crop_prompt = f"""Extract the crop name from this farmer's message. If no crop is mentioned, return "none".

Message: "{user_message}"

Common crops: rice, wheat, onion, potato, tomato, cotton, sugarcane, soybean, maize, chilly, brinjal, cabbage, cauliflower, groundnut, turmeric, ginger, garlic, banana, mango, grapes, pomegranate, papaya, mushroom

Reply with ONLY the crop name in English (e.g., "tomato" or "wheat" or "none"). No explanation."""

        try:
            crop = AIService.ask(crop_prompt, skip_context=True).strip().lower().replace("*", "").replace("_", "")
            if crop == "none" or not crop:
                return None
            print(f"[AI] Extracted crop: {crop}")
            return crop
        except Exception as e:
            print(f"[ERROR] Crop extraction failed: {e}")
            return None
    
    @staticmethod
    def extract_state(user_message):
        """Extract state/location from message using AI"""
        print(f"[AI] Extracting state...")
        
        state_prompt = f"""Extract the Indian state name from this message. If not mentioned, return "Maharashtra".

Message: "{user_message}"

Reply with ONLY the state name (e.g., "Maharashtra" or "Punjab"). No explanation."""

        try:
            state = AIService.ask(state_prompt, skip_context=True).strip().title()
            print(f"[AI] Extracted state: {state}")
            return state
        except Exception as e:
            print(f"[ERROR] State extraction failed: {e}")
            return "Maharashtra"
    
    @staticmethod
    def route_message(user_message):
        """Route message to appropriate agent using AI"""
        print(f"[AI] Routing message...")
        
        routing_prompt = f"""Analyze this farmer's message and determine which agent should handle it.

Message: "{user_message}"

Available agents:
- greeting: Simple greetings (hi, hello, namaste)
- crop: Crop health issues (disease, pests, leaf problems, plant issues, crop care)
- market: Market prices, mandi rates, selling prices
- finance: Budget planning, cost calculation, profit analysis, expenses, loans, schemes, financial planning, cultivation costs
- general: General farming advice, crop recommendations, weather, other queries

IMPORTANT ROUTING RULES:
1. If message mentions costs, budget, expenses, profit, or financial planning → FINANCE
2. If message mentions a crop + land size (e.g., "wheat in 10 acres", "sugarcane 50% of my land") → FINANCE (implies budget planning)
3. If message asks about cultivation/growing a crop with land details → FINANCE
4. If message is about crop health/disease → CROP
5. If message asks for market prices → MARKET

Reply with ONLY ONE WORD - the agent name (greeting/crop/market/finance/general).
No explanation, just the agent name."""

        try:
            agent = AIService.ask(routing_prompt, skip_context=True).strip().lower()
            
            valid_agents = ["greeting", "crop", "market", "finance", "general"]
            if agent not in valid_agents:
                print(f"[WARNING] Invalid agent '{agent}', defaulting to general")
                agent = "general"
            
            print(f"[AI] Routing selected: {agent.upper()}")
            return agent
        except Exception as e:
            print(f"[ERROR] AI routing failed: {e}, defaulting to general")
            return "general"
