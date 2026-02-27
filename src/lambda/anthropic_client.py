"""
Direct Anthropic Claude API Client
Uses the official Anthropic API instead of AWS Bedrock
"""

import os
import json
import urllib.request
import urllib.error

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


def call_claude(prompt, max_tokens=3000, temperature=0.1, model="claude-sonnet-4-6"):
    """
    Call Anthropic Claude API directly
    
    Args:
        prompt: The user prompt/question
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0-1)
        model: Claude model to use (default: Claude Sonnet 4.6 - latest)
    
    Returns:
        str: The response text from Claude
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    print(f"[ANTHROPIC] Calling Claude API: {model}")
    print(f"[ANTHROPIC] Prompt length: {len(prompt)} chars")
    
    # Prepare request
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json"
    }
    
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        # Make HTTP request
        req = urllib.request.Request(
            ANTHROPIC_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        # Extract text from response
        if 'content' in result and len(result['content']) > 0:
            response_text = result['content'][0]['text']
            print(f"[ANTHROPIC] ✅ Response received: {len(response_text)} chars")
            return response_text
        else:
            print(f"[ANTHROPIC] ❌ Unexpected response format: {result}")
            raise ValueError("Unexpected response format from Claude API")
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"[ANTHROPIC] ❌ HTTP Error {e.code}: {error_body}")
        raise Exception(f"Anthropic API error: {e.code} - {error_body}")
    except urllib.error.URLError as e:
        print(f"[ANTHROPIC] ❌ URL Error: {e.reason}")
        raise Exception(f"Network error calling Anthropic API: {e.reason}")
    except Exception as e:
        print(f"[ANTHROPIC] ❌ Unexpected error: {e}")
        raise


def call_claude_with_retry(prompt, max_tokens=3000, temperature=0.1, model="claude-sonnet-4-6", max_retries=3):
    """
    Call Claude API with exponential backoff retry logic
    
    Args:
        prompt: The user prompt/question
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0-1)
        model: Claude model to use (default: Claude Sonnet 4.6 - latest)
        max_retries: Maximum number of retry attempts
    
    Returns:
        str: The response text from Claude
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return call_claude(prompt, max_tokens, temperature, model)
        except Exception as e:
            if "rate" in str(e).lower() and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                print(f"[ANTHROPIC] Rate limited, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                time.sleep(wait_time)
            elif attempt < max_retries - 1:
                wait_time = 2
                print(f"[ANTHROPIC] Error, retrying in {wait_time}s (attempt {attempt + 2}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise


# Bedrock-compatible wrapper for easy migration
class AnthropicBedrockWrapper:
    """
    Wrapper to make Anthropic API compatible with existing Bedrock code
    """
    
    def converse(self, modelId, messages, inferenceConfig, system=None, **kwargs):
        """
        Bedrock-compatible converse method
        Accepts system parameter but ignores it (Anthropic API handles system prompts differently)
        """
        # Extract prompt from messages
        prompt = messages[0]["content"][0]["text"]
        
        # If system prompt is provided, prepend it to the user message
        if system:
            prompt = f"{system}\n\n{prompt}"
        
        # Extract config
        max_tokens = inferenceConfig.get("maxTokens", 3000)
        temperature = inferenceConfig.get("temperature", 0.1)
        
        # Map Bedrock model ID to Anthropic model
        # Anthropic API model name: claude-sonnet-4-6 (Claude Sonnet 4.6 - latest)
        if "claude" in modelId.lower():
            model = "claude-sonnet-4-6"
        else:
            model = "claude-sonnet-4-6"  # Default
        
        # Call Claude
        response_text = call_claude_with_retry(prompt, max_tokens, temperature, model)
        
        # Return in Bedrock format
        return {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": response_text
                        }
                    ]
                }
            }
        }


def get_anthropic_client():
    """
    Get Anthropic client (Bedrock-compatible wrapper)
    """
    return AnthropicBedrockWrapper()
