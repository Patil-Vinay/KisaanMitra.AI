"""
Real Accuracy Testing for KisaanMitra.AI
Tests actual deployed system with real queries
"""

import boto3
import json
import time
from datetime import datetime
from collections import defaultdict

# Initialize AWS clients
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Test datasets
TEST_QUERIES = {
    "crop_queries": [
        "मेरे टमाटर में पीले धब्बे हैं",
        "गेहूं में रोग लग गया है",
        "धान की पत्तियां सूख रही हैं",
        "कपास में कीड़े लग गए हैं",
        "गन्ने में लाल सड़न है",
        "my tomato has yellow spots",
        "wheat disease problem",
        "rice leaves turning brown",
        "cotton pest attack",
        "sugarcane red rot disease"
    ],
    "market_queries": [
        "गेहूं का भाव क्या है",
        "प्याज की कीमत बताओ",
        "टमाटर का मंडी रेट",
        "धान का आज का भाव",
        "गन्ने की कीमत",
        "wheat price today",
        "onion market rate",
        "tomato mandi price",
        "rice price in market",
        "sugarcane rate today"
    ],
    "finance_queries": [
        "2 एकड़ गेहूं का बजट",
        "गन्ने की खेती में खर्च",
        "किसान क्रेडिट कार्ड कैसे मिलेगा",
        "PM-KISAN योजना क्या है",
        "खेती के लिए लोन चाहिए",
        "budget for 2 acre wheat",
        "sugarcane farming cost",
        "how to get kisan credit card",
        "what is PM-KISAN scheme",
        "need loan for farming"
    ],
    "general_queries": [
        "नमस्ते",
        "मदद चाहिए",
        "मौसम कैसा रहेगा",
        "कौन सी फसल उगाऊं",
        "खेती की सलाह दो",
        "hello",
        "need help",
        "weather forecast",
        "which crop to grow",
        "farming advice"
    ]
}

# Expected routing for each query
EXPECTED_ROUTING = {
    # Crop queries
    "मेरे टमाटर में पीले धब्बे हैं": "crop",
    "गेहूं में रोग लग गया है": "crop",
    "धान की पत्तियां सूख रही हैं": "crop",
    "कपास में कीड़े लग गए हैं": "crop",
    "गन्ने में लाल सड़न है": "crop",
    "my tomato has yellow spots": "crop",
    "wheat disease problem": "crop",
    "rice leaves turning brown": "crop",
    "cotton pest attack": "crop",
    "sugarcane red rot disease": "crop",
    
    # Market queries
    "गेहूं का भाव क्या है": "market",
    "प्याज की कीमत बताओ": "market",
    "टमाटर का मंडी रेट": "market",
    "धान का आज का भाव": "market",
    "गन्ने की कीमत": "market",
    "wheat price today": "market",
    "onion market rate": "market",
    "tomato mandi price": "market",
    "rice price in market": "market",
    "sugarcane rate today": "market",
    
    # Finance queries
    "2 एकड़ गेहूं का बजट": "finance",
    "गन्ने की खेती में खर्च": "finance",
    "किसान क्रेडिट कार्ड कैसे मिलेगा": "finance",
    "PM-KISAN योजना क्या है": "finance",
    "खेती के लिए लोन चाहिए": "finance",
    "budget for 2 acre wheat": "finance",
    "sugarcane farming cost": "finance",
    "how to get kisan credit card": "finance",
    "what is PM-KISAN scheme": "finance",
    "need loan for farming": "finance",
    
    # General queries
    "नमस्ते": "greeting",
    "मदद चाहिए": "general",
    "मौसम कैसा रहेगा": "general",
    "कौन सी फसल उगाऊं": "general",
    "खेती की सलाह दो": "general",
    "hello": "greeting",
    "need help": "general",
    "weather forecast": "general",
    "which crop to grow": "general",
    "farming advice": "general"
}

def test_ai_routing(query):
    """Test AI routing accuracy"""
    routing_prompt = f"""Analyze this farmer's message and determine which agent should handle it.

Message: "{query}"

Available agents:
- greeting: Simple greetings (hi, hello, namaste)
- crop: Crop health issues (disease, pests, leaf problems, plant issues)
- market: Market prices and mandi rates
- finance: Budget planning, loans, government schemes, costs, expenses
- general: General farming advice, crop recommendations, weather, other queries

Reply with ONLY ONE WORD - the agent name (greeting/crop/market/finance/general).
No explanation, just the agent name."""

    try:
        response = bedrock.converse(
            modelId="us.amazon.nova-pro-v1:0",
            messages=[{"role": "user", "content": [{"text": routing_prompt}]}],
            inferenceConfig={"maxTokens": 50, "temperature": 0.3}
        )
        
        agent = response["output"]["message"]["content"][0]["text"].strip().lower()
        
        # Validate response
        valid_agents = ["greeting", "crop", "market", "finance", "general"]
        if agent not in valid_agents:
            return "invalid"
        
        return agent
    except Exception as e:
        print(f"Error testing routing: {e}")
        return "error"

def test_crop_extraction(query):
    """Test crop name extraction accuracy"""
    crop_prompt = f"""Extract the crop name from this farmer's message. If no crop is mentioned, return "none".

Message: "{query}"

Common crops: rice, wheat, onion, potato, tomato, cotton, sugarcane, soybean, maize, chilly, brinjal, cabbage, cauliflower, groundnut, turmeric, ginger, garlic, banana, mango, grapes, pomegranate

Reply with ONLY the crop name in English (lowercase). If no crop mentioned, reply "none"."""

    try:
        response = bedrock.converse(
            modelId="us.amazon.nova-pro-v1:0",
            messages=[{"role": "user", "content": [{"text": crop_prompt}]}],
            inferenceConfig={"maxTokens": 20, "temperature": 0.1}
        )
        
        crop = response["output"]["message"]["content"][0]["text"].strip().lower()
        return crop
    except Exception as e:
        print(f"Error extracting crop: {e}")
        return "error"

def test_state_extraction(query):
    """Test state/location extraction accuracy"""
    state_prompt = f"""Extract the Indian state or location from this message. If no location mentioned, return "none".

Message: "{query}"

Indian states: Maharashtra, Karnataka, Uttar Pradesh, Madhya Pradesh, Gujarat, Rajasthan, Punjab, Haryana, Tamil Nadu, Andhra Pradesh, Telangana, Kerala, West Bengal, Bihar, Odisha

Reply with ONLY the state name. If no location mentioned, reply "none"."""

    try:
        response = bedrock.converse(
            modelId="us.amazon.nova-pro-v1:0",
            messages=[{"role": "user", "content": [{"text": state_prompt}]}],
            inferenceConfig={"maxTokens": 20, "temperature": 0.1}
        )
        
        state = response["output"]["message"]["content"][0]["text"].strip()
        return state
    except Exception as e:
        print(f"Error extracting state: {e}")
        return "error"

def run_routing_accuracy_test():
    """Test AI routing accuracy"""
    print("\n" + "="*80)
    print("TESTING: AI ROUTING ACCURACY (Amazon Nova Pro)")
    print("="*80)
    
    results = {
        "total": 0,
        "correct": 0,
        "incorrect": 0,
        "errors": 0,
        "by_category": defaultdict(lambda: {"total": 0, "correct": 0})
    }
    
    all_queries = []
    for category, queries in TEST_QUERIES.items():
        all_queries.extend(queries)
    
    print(f"\nTesting {len(all_queries)} queries...")
    print("-" * 80)
    
    for i, query in enumerate(all_queries, 1):
        expected = EXPECTED_ROUTING.get(query, "unknown")
        
        print(f"\n[{i}/{len(all_queries)}] Query: {query}")
        print(f"Expected: {expected}")
        
        # Test routing
        predicted = test_ai_routing(query)
        print(f"Predicted: {predicted}")
        
        results["total"] += 1
        
        if predicted == "error":
            results["errors"] += 1
            print("❌ ERROR")
        elif predicted == expected:
            results["correct"] += 1
            results["by_category"][expected]["correct"] += 1
            print("✅ CORRECT")
        else:
            results["incorrect"] += 1
            print(f"❌ INCORRECT (expected {expected}, got {predicted})")
        
        results["by_category"][expected]["total"] += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    # Calculate accuracy
    accuracy = (results["correct"] / results["total"] * 100) if results["total"] > 0 else 0
    
    print("\n" + "="*80)
    print("ROUTING ACCURACY RESULTS")
    print("="*80)
    print(f"\nTotal Queries: {results['total']}")
    print(f"Correct: {results['correct']}")
    print(f"Incorrect: {results['incorrect']}")
    print(f"Errors: {results['errors']}")
    print(f"\n🎯 OVERALL ACCURACY: {accuracy:.2f}%")
    
    print("\n" + "-"*80)
    print("ACCURACY BY CATEGORY")
    print("-"*80)
    
    for category, stats in sorted(results["by_category"].items()):
        cat_accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"{category.upper():12} : {stats['correct']}/{stats['total']} = {cat_accuracy:.1f}%")
    
    return results

def run_crop_extraction_test():
    """Test crop name extraction accuracy"""
    print("\n" + "="*80)
    print("TESTING: CROP NAME EXTRACTION (Amazon Nova Pro)")
    print("="*80)
    
    test_cases = {
        "मेरे टमाटर में पीले धब्बे हैं": "tomato",
        "गेहूं में रोग लग गया है": "wheat",
        "धान की पत्तियां सूख रही हैं": "rice",
        "कपास में कीड़े लग गए हैं": "cotton",
        "गन्ने में लाल सड़न है": "sugarcane",
        "my tomato has yellow spots": "tomato",
        "wheat disease problem": "wheat",
        "rice leaves turning brown": "rice",
        "cotton pest attack": "cotton",
        "sugarcane red rot disease": "sugarcane",
        "प्याज की कीमत बताओ": "onion",
        "आलू का भाव": "potato",
        "मौसम कैसा रहेगा": "none",
        "नमस्ते": "none"
    }
    
    results = {"total": 0, "correct": 0, "incorrect": 0, "errors": 0}
    
    print(f"\nTesting {len(test_cases)} queries...")
    print("-" * 80)
    
    for i, (query, expected) in enumerate(test_cases.items(), 1):
        print(f"\n[{i}/{len(test_cases)}] Query: {query}")
        print(f"Expected: {expected}")
        
        predicted = test_crop_extraction(query)
        print(f"Predicted: {predicted}")
        
        results["total"] += 1
        
        if predicted == "error":
            results["errors"] += 1
            print("❌ ERROR")
        elif predicted == expected:
            results["correct"] += 1
            print("✅ CORRECT")
        else:
            results["incorrect"] += 1
            print(f"❌ INCORRECT")
        
        time.sleep(0.5)
    
    accuracy = (results["correct"] / results["total"] * 100) if results["total"] > 0 else 0
    
    print("\n" + "="*80)
    print("CROP EXTRACTION RESULTS")
    print("="*80)
    print(f"\nTotal Queries: {results['total']}")
    print(f"Correct: {results['correct']}")
    print(f"Incorrect: {results['incorrect']}")
    print(f"Errors: {results['errors']}")
    print(f"\n🎯 EXTRACTION ACCURACY: {accuracy:.2f}%")
    
    return results

def run_response_time_test():
    """Test response time for different query types"""
    print("\n" + "="*80)
    print("TESTING: RESPONSE TIME (Amazon Nova Pro)")
    print("="*80)
    
    test_queries = [
        "गेहूं में रोग लग गया है",
        "wheat price today",
        "2 एकड़ गेहूं का बजट",
        "नमस्ते"
    ]
    
    results = []
    
    print(f"\nTesting {len(test_queries)} queries...")
    print("-" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: {query}")
        
        start_time = time.time()
        
        try:
            response = bedrock.converse(
                modelId="us.amazon.nova-pro-v1:0",
                messages=[{"role": "user", "content": [{"text": query}]}],
                inferenceConfig={"maxTokens": 500, "temperature": 0.6}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"Response Time: {response_time:.2f}s")
            results.append(response_time)
            print("✅ SUCCESS")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        time.sleep(0.5)
    
    if results:
        avg_time = sum(results) / len(results)
        min_time = min(results)
        max_time = max(results)
        
        print("\n" + "="*80)
        print("RESPONSE TIME RESULTS")
        print("="*80)
        print(f"\nAverage: {avg_time:.2f}s")
        print(f"Minimum: {min_time:.2f}s")
        print(f"Maximum: {max_time:.2f}s")
        print(f"Total Tests: {len(results)}")
    
    return results

def main():
    """Run all accuracy tests"""
    print("\n" + "="*80)
    print("KISAANMITRA.AI - REAL ACCURACY TESTING")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: Amazon Nova Pro (us.amazon.nova-pro-v1:0)")
    print(f"Region: us-east-1")
    print("="*80)
    
    # Test 1: Routing Accuracy
    routing_results = run_routing_accuracy_test()
    
    # Test 2: Crop Extraction
    crop_results = run_crop_extraction_test()
    
    # Test 3: Response Time
    time_results = run_response_time_test()
    
    # Final Summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    routing_accuracy = (routing_results["correct"] / routing_results["total"] * 100) if routing_results["total"] > 0 else 0
    crop_accuracy = (crop_results["correct"] / crop_results["total"] * 100) if crop_results["total"] > 0 else 0
    avg_response_time = sum(time_results) / len(time_results) if time_results else 0
    
    print(f"\n1. AI Routing Accuracy: {routing_accuracy:.2f}%")
    print(f"   - Tested: {routing_results['total']} queries")
    print(f"   - Correct: {routing_results['correct']}")
    print(f"   - Incorrect: {routing_results['incorrect']}")
    
    print(f"\n2. Crop Extraction Accuracy: {crop_accuracy:.2f}%")
    print(f"   - Tested: {crop_results['total']} queries")
    print(f"   - Correct: {crop_results['correct']}")
    print(f"   - Incorrect: {crop_results['incorrect']}")
    
    print(f"\n3. Average Response Time: {avg_response_time:.2f}s")
    print(f"   - Tested: {len(time_results)} queries")
    
    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)
    
    # Save results to file
    results_file = f"accuracy_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "model": "Amazon Nova Pro",
            "routing_accuracy": routing_accuracy,
            "crop_extraction_accuracy": crop_accuracy,
            "average_response_time": avg_response_time,
            "routing_results": routing_results,
            "crop_results": crop_results,
            "response_times": time_results
        }, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {results_file}")

if __name__ == "__main__":
    main()
