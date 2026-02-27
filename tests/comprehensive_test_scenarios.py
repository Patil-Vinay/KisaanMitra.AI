#!/usr/bin/env python3
"""
Comprehensive Test Scenarios for KisaanMitra Finance Agent
Tests 10 diverse scenarios covering different crops, regions, and edge cases
"""

import json
import time
from datetime import datetime

# Test scenarios covering various crops, regions, and conditions
TEST_SCENARIOS = [
    {
        "id": 1,
        "name": "Sugarcane - Large Farm - Maharashtra",
        "phone": "919000000002",
        "message": "I need sugarcane budget for 20 acres in Jalgaon",
        "expected_crop": "sugarcane",
        "expected_location": "Jalgaon",
        "expected_land": 20,
        "validation_checks": {
            "yield_per_acre_min": 60,
            "yield_per_acre_max": 110,
            "cost_per_acre_min": 50000,
            "cost_per_acre_max": 100000,
            "roi_max": 200
        }
    },
    {
        "id": 2,
        "name": "Wheat - Small Farm - Punjab",
        "phone": "919000000002",
        "message": "wheat cultivation cost for 5 acres in Ludhiana",
        "expected_crop": "wheat",
        "expected_location": "Ludhiana",
        "expected_land": 5,
        "validation_checks": {
            "yield_per_acre_min": 25,
            "yield_per_acre_max": 50,
            "cost_per_acre_min": 18000,
            "cost_per_acre_max": 35000,
            "roi_max": 100
        }
    },
    {
        "id": 3,
        "name": "Cotton - Medium Farm - Gujarat",
        "phone": "919000000002",
        "message": "cotton farming budget 10 acres Ahmedabad",
        "expected_crop": "cotton",
        "expected_location": "Ahmedabad",
        "expected_land": 10,
        "validation_checks": {
            "yield_per_acre_min": 8,
            "yield_per_acre_max": 20,
            "cost_per_acre_min": 25000,
            "cost_per_acre_max": 50000,
            "roi_max": 120
        }
    },
    {
        "id": 4,
        "name": "Rice - Paddy - West Bengal",
        "phone": "919000000002",
        "message": "paddy rice budget for 15 acres in Kolkata region",
        "expected_crop": "rice",
        "expected_location": "Kolkata",
        "expected_land": 15,
        "validation_checks": {
            "yield_per_acre_min": 20,
            "yield_per_acre_max": 50,
            "cost_per_acre_min": 20000,
            "cost_per_acre_max": 40000,
            "roi_max": 100
        }
    },
    {
        "id": 5,
        "name": "Tomato - Vegetable - Karnataka",
        "phone": "919000000002",
        "message": "tomato cultivation 3 acres Bangalore",
        "expected_crop": "tomato",
        "expected_location": "Bangalore",
        "expected_land": 3,
        "validation_checks": {
            "yield_per_acre_min": 100,
            "yield_per_acre_max": 300,
            "cost_per_acre_min": 40000,
            "cost_per_acre_max": 80000,
            "roi_max": 180
        }
    },
    {
        "id": 6,
        "name": "Onion - High Value - Maharashtra",
        "phone": "919000000002",
        "message": "onion farming cost 8 acres Nashik",
        "expected_crop": "onion",
        "expected_location": "Nashik",
        "expected_land": 8,
        "validation_checks": {
            "yield_per_acre_min": 80,
            "yield_per_acre_max": 200,
            "cost_per_acre_min": 40000,
            "cost_per_acre_max": 70000,
            "roi_max": 180
        }
    },
    {
        "id": 7,
        "name": "Soybean - Pulse - Madhya Pradesh",
        "phone": "919000000002",
        "message": "soybean budget 12 acres Indore",
        "expected_crop": "soybean",
        "expected_location": "Indore",
        "expected_land": 12,
        "validation_checks": {
            "yield_per_acre_min": 8,
            "yield_per_acre_max": 20,
            "cost_per_acre_min": 15000,
            "cost_per_acre_max": 30000,
            "roi_max": 120
        }
    },
    {
        "id": 8,
        "name": "Groundnut - Oilseed - Andhra Pradesh",
        "phone": "919000000002",
        "message": "groundnut peanut cultivation 6 acres Guntur",
        "expected_crop": "groundnut",
        "expected_location": "Guntur",
        "expected_land": 6,
        "validation_checks": {
            "yield_per_acre_min": 10,
            "yield_per_acre_max": 25,
            "cost_per_acre_min": 20000,
            "cost_per_acre_max": 40000,
            "roi_max": 120
        }
    },
    {
        "id": 9,
        "name": "Maize - Corn - Rajasthan",
        "phone": "919000000002",
        "message": "maize corn farming 7 acres Jaipur",
        "expected_crop": "maize",
        "expected_location": "Jaipur",
        "expected_land": 7,
        "validation_checks": {
            "yield_per_acre_min": 20,
            "yield_per_acre_max": 50,
            "cost_per_acre_min": 15000,
            "cost_per_acre_max": 30000,
            "roi_max": 100
        }
    },
    {
        "id": 10,
        "name": "Chilli - Spice - Telangana",
        "phone": "919000000002",
        "message": "chilli pepper cultivation 4 acres Hyderabad",
        "expected_crop": "chilli",
        "expected_location": "Hyderabad",
        "expected_land": 4,
        "validation_checks": {
            "yield_per_acre_min": 15,
            "yield_per_acre_max": 40,
            "cost_per_acre_min": 35000,
            "cost_per_acre_max": 70000,
            "roi_max": 180
        }
    }
]

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_section(text):
    """Print formatted section"""
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80)

def validate_response(scenario, response_text):
    """Validate response against expected criteria"""
    issues = []
    warnings = []
    
    # Check if response contains error indicators
    if "error" in response_text.lower() or "failed" in response_text.lower():
        issues.append("Response contains error message")
    
    # Check for required components in response
    required_keywords = ["cost", "revenue", "profit", "roi"]
    missing_keywords = [kw for kw in required_keywords if kw not in response_text.lower()]
    if missing_keywords:
        issues.append(f"Missing keywords: {', '.join(missing_keywords)}")
    
    # Extract numbers from response for validation
    import re
    
    # Try to extract yield per acre
    yield_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ton|quintal|kg)/acre', response_text, re.IGNORECASE)
    if yield_match:
        yield_value = float(yield_match.group(1))
        checks = scenario['validation_checks']
        
        if 'yield_per_acre_min' in checks and yield_value < checks['yield_per_acre_min']:
            warnings.append(f"Yield per acre ({yield_value}) below minimum ({checks['yield_per_acre_min']})")
        if 'yield_per_acre_max' in checks and yield_value > checks['yield_per_acre_max']:
            issues.append(f"Yield per acre ({yield_value}) exceeds maximum ({checks['yield_per_acre_max']})")
    
    # Try to extract ROI
    roi_match = re.search(r'ROI[:\s]*(\d+(?:\.\d+)?)\s*%', response_text, re.IGNORECASE)
    if roi_match:
        roi_value = float(roi_match.group(1))
        if 'roi_max' in checks and roi_value > checks['roi_max']:
            warnings.append(f"ROI ({roi_value}%) exceeds realistic maximum ({checks['roi_max']}%)")
    
    # Check for validation pipeline indicators
    validation_indicators = [
        "VALIDATION",
        "MATH_ENFORCEMENT",
        "SANITY_CHECK"
    ]
    
    return {
        "issues": issues,
        "warnings": warnings,
        "has_validation": any(ind in response_text for ind in validation_indicators)
    }

def run_test_scenario(scenario):
    """Run a single test scenario"""
    print_section(f"Test #{scenario['id']}: {scenario['name']}")
    
    print(f"\n📱 Phone: {scenario['phone']}")
    print(f"💬 Message: {scenario['message']}")
    print(f"🎯 Expected: {scenario['expected_crop']} | {scenario['expected_location']} | {scenario['expected_land']} acres")
    
    # Simulate WhatsApp message
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "1460763002175471",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15551411052",
                        "phone_number_id": "1049535664900621"
                    },
                    "messages": [{
                        "from": scenario['phone'],
                        "id": f"test_msg_{scenario['id']}_{int(time.time())}",
                        "timestamp": str(int(time.time())),
                        "text": {
                            "body": scenario['message']
                        },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    # Save test payload
    payload_file = f"/tmp/test_scenario_{scenario['id']}.json"
    with open(payload_file, 'w') as f:
        json.dump(webhook_payload, f, indent=2)
    
    print(f"\n⏳ Invoking Lambda function...")
    start_time = time.time()
    
    # Invoke Lambda
    import subprocess
    result = subprocess.run([
        'aws', 'lambda', 'invoke',
        '--function-name', 'whatsapp-llama-bot',
        '--payload', json.dumps(json.dumps(webhook_payload)),
        '--cli-binary-format', 'raw-in-base64-out',
        f'/tmp/test_response_{scenario["id"]}.json'
    ], capture_output=True, text=True)
    
    elapsed_time = time.time() - start_time
    
    if result.returncode != 0:
        print(f"\n❌ Lambda invocation failed!")
        print(f"Error: {result.stderr}")
        return {
            "scenario_id": scenario['id'],
            "status": "FAILED",
            "error": result.stderr,
            "elapsed_time": elapsed_time
        }
    
    print(f"✅ Lambda invoked successfully ({elapsed_time:.2f}s)")
    
    # Wait for processing
    print("⏳ Waiting for processing (20s)...")
    time.sleep(20)
    
    # Check logs for this specific request
    print("\n📋 Fetching logs...")
    log_result = subprocess.run([
        'aws', 'logs', 'tail',
        '/aws/lambda/whatsapp-llama-bot',
        '--since', '2m',
        '--format', 'short'
    ], capture_output=True, text=True)
    
    logs = log_result.stdout
    
    # Extract relevant log sections
    if f"test_msg_{scenario['id']}" in logs or scenario['message'] in logs:
        print("✅ Found request in logs")
        
        # Look for validation steps
        validation_found = "VALIDATION" in logs
        math_enforcement_found = "MATH_ENFORCEMENT" in logs
        sanity_check_found = "SANITY_CHECK" in logs
        anthropic_success = "✅ Response received" in logs
        
        print(f"\n🔍 Validation Pipeline:")
        print(f"  - Pre-scaling validation: {'✅' if validation_found else '❌'}")
        print(f"  - Math enforcement: {'✅' if math_enforcement_found else '❌'}")
        print(f"  - Sanity check: {'✅' if sanity_check_found else '❌'}")
        print(f"  - Anthropic API: {'✅' if anthropic_success else '❌'}")
        
        # Extract final numbers from logs
        import re
        final_cost_match = re.search(r'\[FINAL\] Total Cost: ₹([\d,]+)', logs)
        final_revenue_match = re.search(r'\[FINAL\] Total Revenue: ₹([\d,]+)', logs)
        final_profit_match = re.search(r'\[FINAL\] Total Profit: ₹([\d,]+)', logs)
        final_roi_match = re.search(r'\[FINAL\] ROI: ([\d.]+)%', logs)
        
        if all([final_cost_match, final_revenue_match, final_profit_match, final_roi_match]):
            print(f"\n💰 Final Numbers:")
            print(f"  - Total Cost: ₹{final_cost_match.group(1)}")
            print(f"  - Total Revenue: ₹{final_revenue_match.group(1)}")
            print(f"  - Total Profit: ₹{final_profit_match.group(1)}")
            print(f"  - ROI: {final_roi_match.group(1)}%")
            
            # Validate numbers
            total_cost = int(final_cost_match.group(1).replace(',', ''))
            total_revenue = int(final_revenue_match.group(1).replace(',', ''))
            total_profit = int(final_profit_match.group(1).replace(',', ''))
            roi = float(final_roi_match.group(1))
            
            # Check mathematical accuracy
            calculated_profit = total_revenue - total_cost
            calculated_roi = (calculated_profit / total_cost) * 100
            
            math_accurate = abs(calculated_profit - total_profit) < 100  # Allow ₹100 rounding
            roi_accurate = abs(calculated_roi - roi) < 1  # Allow 1% rounding
            
            print(f"\n✓ Mathematical Accuracy:")
            print(f"  - Profit calculation: {'✅' if math_accurate else '❌'}")
            print(f"  - ROI calculation: {'✅' if roi_accurate else '❌'}")
            
            # Check cost per acre
            cost_per_acre = total_cost / scenario['expected_land']
            checks = scenario['validation_checks']
            
            cost_realistic = (checks['cost_per_acre_min'] <= cost_per_acre <= checks['cost_per_acre_max'])
            roi_realistic = roi <= checks['roi_max']
            
            print(f"\n✓ Realism Checks:")
            print(f"  - Cost per acre (₹{cost_per_acre:,.0f}): {'✅' if cost_realistic else '⚠️'}")
            print(f"  - ROI ({roi}%): {'✅' if roi_realistic else '⚠️'}")
            
            return {
                "scenario_id": scenario['id'],
                "status": "SUCCESS",
                "elapsed_time": elapsed_time,
                "validation_pipeline": {
                    "pre_scaling": validation_found,
                    "math_enforcement": math_enforcement_found,
                    "sanity_check": sanity_check_found,
                    "anthropic_api": anthropic_success
                },
                "numbers": {
                    "total_cost": total_cost,
                    "total_revenue": total_revenue,
                    "total_profit": total_profit,
                    "roi": roi,
                    "cost_per_acre": cost_per_acre
                },
                "accuracy": {
                    "math_accurate": math_accurate,
                    "roi_accurate": roi_accurate,
                    "cost_realistic": cost_realistic,
                    "roi_realistic": roi_realistic
                }
            }
        else:
            print("\n⚠️ Could not extract final numbers from logs")
    else:
        print("⚠️ Request not found in logs")
    
    return {
        "scenario_id": scenario['id'],
        "status": "PARTIAL",
        "elapsed_time": elapsed_time,
        "logs_found": False
    }

def main():
    """Run all test scenarios"""
    print_header("KisaanMitra Comprehensive Test Suite")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 Total Scenarios: {len(TEST_SCENARIOS)}")
    
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        result = run_test_scenario(scenario)
        results.append(result)
        
        # Wait between tests to avoid rate limiting
        if i < len(TEST_SCENARIOS):
            print(f"\n⏸️  Waiting 30s before next test...")
            time.sleep(30)
    
    # Summary
    print_header("TEST SUMMARY")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    partial_count = sum(1 for r in results if r['status'] == 'PARTIAL')
    
    print(f"\n📊 Results:")
    print(f"  ✅ Success: {success_count}/{len(TEST_SCENARIOS)}")
    print(f"  ❌ Failed: {failed_count}/{len(TEST_SCENARIOS)}")
    print(f"  ⚠️  Partial: {partial_count}/{len(TEST_SCENARIOS)}")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'FAILED' else "⚠️"
        print(f"\n{status_icon} Scenario #{result['scenario_id']}: {result['status']}")
        
        if 'accuracy' in result:
            acc = result['accuracy']
            print(f"  - Math Accurate: {'✅' if acc['math_accurate'] else '❌'}")
            print(f"  - ROI Accurate: {'✅' if acc['roi_accurate'] else '❌'}")
            print(f"  - Cost Realistic: {'✅' if acc['cost_realistic'] else '⚠️'}")
            print(f"  - ROI Realistic: {'✅' if acc['roi_realistic'] else '⚠️'}")
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(TEST_SCENARIOS),
                "success": success_count,
                "failed": failed_count,
                "partial": partial_count
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to test_results.json")
    
    return success_count == len(TEST_SCENARIOS)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
