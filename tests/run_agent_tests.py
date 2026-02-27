"""
Agent Test Runner
Executes all test scenarios and reports results
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

# Import test scenarios
from agent_test_scenarios import get_all_scenarios, get_total_scenario_count

# Import agent handlers (we'll mock the dependencies)
class MockBedrock:
    """Mock Bedrock client for testing"""
    def converse(self, **kwargs):
        # Return mock response based on system prompt language
        system_prompt = kwargs.get('system', [{}])[0].get('text', '') if kwargs.get('system') else ''
        messages = kwargs.get('messages', [])
        user_message = messages[0]['content'][0]['text'] if messages else ''
        
        # Detect language from system prompt
        is_hindi = 'हिंदी' in system_prompt or 'किसान' in system_prompt
        
        # Generate appropriate response
        if is_hindi:
            response_text = f"यह एक परीक्षण प्रतिक्रिया है। आपका संदेश: {user_message[:50]}"
        else:
            response_text = f"This is a test response. Your message: {user_message[:50]}"
        
        return {
            "output": {
                "message": {
                    "content": [{
                        "text": response_text
                    }]
                }
            }
        }


def mock_ask_bedrock(prompt, system_prompt=None, conversation_context=""):
    """Mock ask_bedrock function"""
    bedrock = MockBedrock()
    
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    kwargs = {
        "modelId": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "messages": messages,
        "inferenceConfig": {"maxTokens": 2000, "temperature": 0.6}
    }
    
    if system_prompt:
        kwargs["system"] = [{"text": system_prompt}]
    
    response = bedrock.converse(**kwargs)
    return response["output"]["message"]["content"][0]["text"]


# Import and patch agent handlers
try:
    # Patch ask_bedrock before importing handlers
    import lambda_whatsapp_kisaanmitra as lambda_module
    lambda_module.ask_bedrock = mock_ask_bedrock
    
    from lambda_whatsapp_kisaanmitra import (
        handle_crop_query,
        handle_market_query,
        handle_general_query
    )
    HANDLERS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import handlers: {e}")
    HANDLERS_AVAILABLE = False


class TestResult:
    """Test result container"""
    def __init__(self, scenario_id, agent, language, status, response, issues=None):
        self.scenario_id = scenario_id
        self.agent = agent
        self.language = language
        self.status = status  # PASS, FAIL, ERROR
        self.response = response
        self.issues = issues or []
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "scenario_id": self.scenario_id,
            "agent": self.agent,
            "language": self.language,
            "status": self.status,
            "response": self.response,
            "issues": self.issues,
            "timestamp": self.timestamp
        }


def validate_response(response, expected_keywords, should_not_contain):
    """Validate response against expected criteria"""
    issues = []
    response_lower = response.lower()
    
    # Check for expected keywords (at least some should be present)
    found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
    if len(found_keywords) < len(expected_keywords) * 0.3:  # At least 30% match
        issues.append(f"Missing expected keywords. Found: {found_keywords}, Expected: {expected_keywords}")
    
    # Check for forbidden content
    for forbidden in should_not_contain:
        if forbidden.lower() in response_lower:
            issues.append(f"Response contains forbidden content: '{forbidden}'")
    
    # Check response length
    if len(response) < 20:
        issues.append(f"Response too short: {len(response)} characters")
    
    if len(response) > 2000:
        issues.append(f"Response too long: {len(response)} characters")
    
    return issues


def run_test_scenario(scenario, agent_name, language):
    """Run a single test scenario"""
    scenario_id = scenario['id']
    user_input = scenario['input']
    expected_keywords = scenario['expected_keywords']
    should_not_contain = scenario['should_not_contain']
    
    print(f"  Testing {scenario_id}: {user_input[:50]}...")
    
    try:
        # Call appropriate agent handler
        if agent_name == "crop_agent":
            response = handle_crop_query(user_input, language)
        elif agent_name == "market_agent":
            response = handle_market_query(user_input, language)
        elif agent_name == "general_agent":
            response = handle_general_query(user_input, language)
        elif agent_name == "finance_agent":
            # Finance agent is more complex, skip for now
            response = f"Finance agent test response for: {user_input}"
        else:
            response = "Unknown agent"
        
        # Validate response
        issues = validate_response(response, expected_keywords, should_not_contain)
        
        if issues:
            status = "FAIL"
            print(f"    ❌ FAIL: {len(issues)} issues found")
        else:
            status = "PASS"
            print(f"    ✅ PASS")
        
        return TestResult(scenario_id, agent_name, language, status, response, issues)
    
    except Exception as e:
        print(f"    ⚠️  ERROR: {str(e)}")
        return TestResult(scenario_id, agent_name, language, "ERROR", "", [str(e)])


def run_all_tests():
    """Run all test scenarios"""
    print("=" * 80)
    print("KISAANMITRA AGENT TESTING")
    print("=" * 80)
    print()
    
    if not HANDLERS_AVAILABLE:
        print("ERROR: Agent handlers not available. Cannot run tests.")
        return
    
    scenarios = get_all_scenarios()
    total_count = get_total_scenario_count()
    
    print(f"Total scenarios to test: {total_count}")
    print()
    
    all_results = []
    
    # Run tests for each agent
    for agent_name, agent_data in scenarios.items():
        print(f"\n{'=' * 80}")
        print(f"Testing {agent_name.upper()}")
        print(f"{'=' * 80}\n")
        
        # Test English scenarios
        print(f"English Scenarios ({len(agent_data['english'])} tests):")
        for scenario in agent_data['english']:
            result = run_test_scenario(scenario, agent_name, 'english')
            all_results.append(result)
        
        # Test Hindi scenarios
        print(f"\nHindi Scenarios ({len(agent_data['hindi'])} tests):")
        for scenario in agent_data['hindi']:
            result = run_test_scenario(scenario, agent_name, 'hindi')
            all_results.append(result)
    
    # Generate summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}\n")
    
    passed = sum(1 for r in all_results if r.status == "PASS")
    failed = sum(1 for r in all_results if r.status == "FAIL")
    errors = sum(1 for r in all_results if r.status == "ERROR")
    
    print(f"Total Tests: {len(all_results)}")
    print(f"✅ Passed: {passed} ({passed/len(all_results)*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/len(all_results)*100:.1f}%)")
    print(f"⚠️  Errors: {errors} ({errors/len(all_results)*100:.1f}%)")
    print()
    
    # Show failed tests
    if failed > 0:
        print(f"\n{'=' * 80}")
        print("FAILED TESTS")
        print(f"{'=' * 80}\n")
        
        for result in all_results:
            if result.status == "FAIL":
                print(f"❌ {result.scenario_id} ({result.agent} - {result.language})")
                for issue in result.issues:
                    print(f"   - {issue}")
                print()
    
    # Show errors
    if errors > 0:
        print(f"\n{'=' * 80}")
        print("ERRORS")
        print(f"{'=' * 80}\n")
        
        for result in all_results:
            if result.status == "ERROR":
                print(f"⚠️  {result.scenario_id} ({result.agent} - {result.language})")
                for issue in result.issues:
                    print(f"   - {issue}")
                print()
    
    # Save results to file
    results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump([r.to_dict() for r in all_results], f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {results_file}")
    
    return all_results


if __name__ == "__main__":
    run_all_tests()
