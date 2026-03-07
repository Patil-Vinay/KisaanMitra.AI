"""
AI Service - Handles all AI/LLM interactions with caching and optimization
"""
import os
import time
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import json
import hashlib

# Import caching service
try:
    from services.cache_service import CacheService, RateLimiter
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("[AI_SERVICE] Cache service not available")

# Use AWS Bedrock Amazon Nova Pro for all operations
print("[AI_SERVICE] Using AWS Bedrock Amazon Nova Pro with optimization")

# Create optimized Bedrock client
try:
    bedrock = boto3.client(
        "bedrock-runtime", 
        region_name="us-east-1",
        config=boto3.session.Config(
            retries={'max_attempts': 2, 'mode': 'adaptive'},  # Reduced retries
            read_timeout=20,  # Reduced timeout
            connect_timeout=5,
            max_pool_connections=10  # Connection pooling
        )
    )
    bedrock_for_images = bedrock
    print("[AI_SERVICE] ✅ Optimized Bedrock client initialized")
except Exception as e:
    print(f"[AI_SERVICE] ❌ Failed to initialize Bedrock client: {e}")
    bedrock = None
    bedrock_for_images = None


class AIService:
    """Manages AI/LLM interactions with robust error handling"""
    
    @staticmethod
    def ask(prompt, system_prompt=None, conversation_context="", skip_context=False, max_retries=2):
        """Call Bedrock/Claude with caching and optimized retry logic"""
        if not bedrock:
            return "AI service is currently unavailable. Please try again later."

        if not prompt or not prompt.strip():
            return "Please provide a valid question or message."

        # Generate cache key for identical requests
        cache_key = None
        if CACHE_AVAILABLE and not conversation_context:  # Only cache context-free requests
            prompt_hash = hashlib.md5(f"{prompt}:{system_prompt}".encode()).hexdigest()[:16]
            cache_key = CacheService.get_ai_response_key(prompt_hash)

            cached_response = CacheService.get(cache_key)
            if cached_response:
                print(f"[AI] Using cached response")
                return cached_response

            # Rate limiting for AI calls
            ai_rate_key = RateLimiter.get_api_key("bedrock_general")
            if not RateLimiter.is_allowed(ai_rate_key, max_requests=30, window_seconds=60):
                return "AI service is temporarily busy. Please try again in a moment."

        try:
            print(f"[AI] Calling Bedrock - Model: Nova Pro")
            print(f"[AI] Prompt length: {len(prompt)} chars")

            # Optimized context handling
            if skip_context:
                full_prompt = prompt
            else:
                full_prompt = conversation_context + prompt if conversation_context else prompt

            # Optimized truncation with better limits
            max_prompt_length = 6000  # Reduced for faster processing
            if len(full_prompt) > max_prompt_length:
                full_prompt = full_prompt[-max_prompt_length:]
                print(f"[AI] Truncated prompt to {max_prompt_length} chars")

            messages = [{"role": "user", "content": [{"text": full_prompt}]}]

            # Optimized token calculation
            estimated_tokens = len(full_prompt) // 3  # Rough estimate
            max_response_tokens = min(1500, 3000 - estimated_tokens)  # Dynamic limit

            kwargs = {
                "modelId": "us.amazon.nova-pro-v1:0",
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": max_response_tokens,
                    "temperature": 0.6  # Balanced creativity/consistency
                }
            }

            if system_prompt and system_prompt.strip():
                kwargs["system"] = [{"text": system_prompt}]

            # Optimized retry logic with faster backoff
            for attempt in range(max_retries):
                try:
                    response = bedrock.converse(**kwargs)

                    if not response or "output" not in response:
                        raise Exception("Invalid response format from Bedrock")

                    content = response.get("output", {}).get("message", {}).get("content", [])
                    if not content or not content[0].get("text"):
                        raise Exception("Empty response from Bedrock")

                    result = content[0]["text"]

                    # Cache successful responses
                    if CACHE_AVAILABLE and cache_key and len(result) < 2000:  # Cache smaller responses
                        CacheService.set(cache_key, result, ttl_seconds=1800)  # 30 minutes

                    print(f"[AI] Response received, length: {len(result)} chars")
                    return result

                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    error_message = e.response.get('Error', {}).get('Message', '')

                    if error_code == 'ThrottlingException' and attempt < max_retries - 1:
                        wait_time = 0.5 * (2 ** attempt)  # Faster backoff: 0.5s, 1s
                        print(f"[AI] Throttled, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    elif error_code == 'ValidationException':
                        print(f"[AI] Validation error: {error_message}")
                        return "I couldn't process your request due to invalid input. Please try rephrasing."
                    elif error_code == 'ServiceQuotaExceededException':
                        print(f"[AI] Service quota exceeded: {error_message}")
                        return "Service is temporarily unavailable due to high demand. Please try again later."
                    else:
                        print(f"[AI] Client error: {error_code} - {error_message}")
                        if attempt < max_retries - 1:
                            time.sleep(0.5 * (attempt + 1))  # Faster retry
                            continue
                        else:
                            raise

                except BotoCoreError as e:
                    print(f"[AI] BotoCore error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    else:
                        raise

                except Exception as e:
                    print(f"[AI] Unexpected error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    else:
                        raise

        except Exception as e:
            print(f"[ERROR] AI service failed after all retries: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return "I'm having trouble helping you right now. Please try again in a moment."
    
    @staticmethod
    def get_image_client():
        """Get Bedrock client for image analysis"""
        return bedrock_for_images
    
    @staticmethod
    def extract_crop(user_message, max_retries=2):
        """Extract crop name from message using AI with validation"""
        if not user_message or not user_message.strip():
            return None
            
        print(f"[AI] Extracting crop name...")
        
        crop_prompt = f"""Extract the crop name from this farmer's message. If no crop is mentioned, return "none".

Message: "{user_message}"

Common crops: rice, wheat, onion, potato, tomato, cotton, sugarcane, soybean, maize, chilly, brinjal, cabbage, cauliflower, groundnut, turmeric, ginger, garlic, banana, mango, grapes, pomegranate, papaya, mushroom

Reply with ONLY the crop name in English (e.g., "tomato" or "wheat" or "none"). No explanation."""

        try:
            crop = AIService.ask(crop_prompt, skip_context=True, max_retries=max_retries)
            if not crop:
                return None
                
            crop = crop.strip().lower().replace("*", "").replace("_", "").replace(".", "")
            if crop == "none" or not crop or len(crop) > 20:  # Validation
                return None
                
            print(f"[AI] Extracted crop: {crop}")
            return crop
        except Exception as e:
            print(f"[ERROR] Crop extraction failed: {e}")
            return None
    
    @staticmethod
    def extract_state(user_message, max_retries=2):
        """Extract state/location from message using AI with validation"""
        if not user_message or not user_message.strip():
            return "Maharashtra"
            
        print(f"[AI] Extracting state...")
        
        state_prompt = f"""Extract the Indian state name from this message. If not mentioned, return "Maharashtra".

Message: "{user_message}"

Reply with ONLY the state name (e.g., "Maharashtra" or "Punjab"). No explanation."""

        try:
            state = AIService.ask(state_prompt, skip_context=True, max_retries=max_retries)
            if not state:
                return "Maharashtra"
                
            state = state.strip().title()
            # Validate state name length and format
            if len(state) > 30 or not state.replace(" ", "").isalpha():
                return "Maharashtra"
                
            print(f"[AI] Extracted state: {state}")
            return state
        except Exception as e:
            print(f"[ERROR] State extraction failed: {e}")
            return "Maharashtra"
    
    @staticmethod
    def route_message(user_message, max_retries=2):
        """Route message to appropriate agent using AI with validation"""
        if not user_message or not user_message.strip():
            return "general"
            
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
            agent = AIService.ask(routing_prompt, skip_context=True, max_retries=max_retries)
            if not agent:
                return "general"
                
            agent = agent.strip().lower()
            
            valid_agents = ["greeting", "crop", "market", "finance", "general"]
            if agent not in valid_agents:
                print(f"[WARNING] Invalid agent '{agent}', defaulting to general")
                agent = "general"
            
            print(f"[AI] Routing selected: {agent.upper()}")
            return agent
        except Exception as e:
            print(f"[ERROR] AI routing failed: {e}, defaulting to general")
            return "general"
