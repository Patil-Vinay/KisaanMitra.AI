#!/usr/bin/env python3
"""
Test 3 key scenarios to identify issues
"""

import json
import subprocess
import time
import re

def test_scenario(num, message, expected_crop):
    """Test a single scenario"""
    print(f"\n{'='*80}")
    print(f"TEST #{num}: {expected_crop}")
    print(f"{'='*80}")
    print(f"Message: {message}\n")
    
    # Create webhook payload
    payload = {
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
                        "from": "919000000002",
                        "id": f"test_{num}_{int(time.time())}",
                        "timestamp": str(int(time.time())),
                        "text": {"body": message},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    # Invoke Lambda
    print("⏳ Invoking Lambda...")
    result = subprocess.run([
        'aws', 'lambda', 'invoke',
        '--function-name', 'whatsapp-llama-bot',
        '--payload', json.dumps(payload),
        '--cli-binary-format', 'raw-in-base64-out',
        f'/tmp/test_{num}.json'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed: {result.stderr}")
        return False
    
    print("✅ Lambda invoked")
    
    # Wait for processing
    print("⏳ Waiting 20s for processing...")
    time.sleep(20)
    
    # Get logs
    print("📋 Fetching logs...")
    log_result = subprocess.run([
        'aws', 'logs', 'tail',
        '/aws/lambda/whatsapp-llama-bot',
        '--since', '2m',
        '--format', 'short'
    ], capture_output=True, text=True)
    
    logs = log_result.stdout
    
    # Analyze logs
    print("\n🔍 Analysis:")
    
    # Check for Anthropic API call
    if 'claude-sonnet-4-6' in logs:
        print("  ✅ Using Claude Sonnet 4.6")
    else:
        print("  ❌ Not using Claude Sonnet 4.6")
    
    # Check for successful response
    if '✅ Response received' in logs:
        print("  ✅ Anthropic API responded")
    else:
        print("  ❌ No Anthropic response")
        return False
    
    # Check validation pipeline
    validation_steps = {
        "Pre-scaling": "STEP 1: PRE-SCALING VALIDATION",
        "Missing costs": "STEP 2: ADDING MISSING COSTS",
        "Scaling": "STEP 3: SCALING TO LAND SIZE",
        "Math enforcement": "STEP 4: MATHEMATICAL ENFORCEMENT",
        "Sanity check": "STEP 5: FINAL SANITY CHECK"
    }
    
    print("\n  Validation Pipeline:")
    for name, marker in validation_steps.items():
        if marker in logs:
            print(f"    ✅ {name}")
        else:
            print(f"    ❌ {name}")
    
    # Extract final numbers
    cost_match = re.search(r'\[FINAL\] Total Cost: ₹([\d,]+)', logs)
    revenue_match = re.search(r'\[FINAL\] Total Revenue: ₹([\d,]+)', logs)
    profit_match = re.search(r'\[FINAL\] Total Profit: ₹([\d,]+)', logs)
    roi_match = re.search(r'\[FINAL\] ROI: ([\d.]+)%', logs)
    
    if all([cost_match, revenue_match, profit_match, roi_match]):
        cost = int(cost_match.group(1).replace(',', ''))
        revenue = int(revenue_match.group(1).replace(',', ''))
        profit = int(profit_match.group(1).replace(',', ''))
        roi = float(roi_match.group(1))
        
        print(f"\n  💰 Final Numbers:")
        print(f"    Cost:    ₹{cost:,}")
        print(f"    Revenue: ₹{revenue:,}")
        print(f"    Profit:  ₹{profit:,}")
        print(f"    ROI:     {roi}%")
        
        # Validate math
        calc_profit = revenue - cost
        calc_roi = (calc_profit / cost) * 100
        
        math_ok = abs(calc_profit - profit) < 100
        roi_ok = abs(calc_roi - roi) < 1
        
        print(f"\n  ✓ Mathematical Accuracy:")
        print(f"    Profit: {'✅' if math_ok else '❌'} (calculated: ₹{calc_profit:,})")
        print(f"    ROI: {'✅' if roi_ok else '❌'} (calculated: {calc_roi:.1f}%)")
        
        # Check for issues
        issues = []
        if 'UNREALISTIC ROI DETECTED' in logs:
            issues.append("Unrealistic ROI detected (corrected)")
        if 'SANITY CHECK FAILED' in logs:
            issues.append("Sanity check failed (conservative estimates applied)")
        if 'Revenue mismatch' in logs:
            issues.append("Revenue mismatch (corrected)")
        if 'Profit mismatch' in logs:
            issues.append("Profit mismatch (corrected)")
        
        if issues:
            print(f"\n  ⚠️  Issues (auto-corrected):")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"\n  ✅ No issues detected")
        
        return math_ok and roi_ok
    else:
        print("\n  ❌ Could not extract final numbers")
        return False

def main():
    """Run 3 test scenarios"""
    print("\n" + "="*80)
    print("  KisaanMitra - 3 Scenario Test")
    print("="*80)
    
    scenarios = [
        (1, "sugarcane budget for 20 acres in Jalgaon", "Sugarcane"),
        (2, "wheat cultivation 5 acres Ludhiana", "Wheat"),
        (3, "tomato farming 3 acres Bangalore", "Tomato")
    ]
    
    results = []
    for num, message, crop in scenarios:
        success = test_scenario(num, message, crop)
        results.append((num, crop, success))
        
        if num < len(scenarios):
            print(f"\n⏸️  Waiting 30s before next test...")
            time.sleep(30)
    
    # Summary
    print("\n" + "="*80)
    print("  SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} passed\n")
    
    for num, crop, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  Test #{num} ({crop}): {status}")
    
    print()
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
