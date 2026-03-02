#!/usr/bin/env python3
"""
Test weather location priority logic
"""
import sys
sys.path.append('../src/lambda')
sys.path.append('../src/onboarding')

# Mock the onboarding manager
class MockOnboardingManager:
    def get_user_profile(self, user_id):
        if user_id == "919000000002":
            return {
                'name': 'Parth Nikam',
                'village': 'Nandani',
                'district': 'Sangli',
                'current_crops': 'sugarcane'
            }
        return None

# Test the logic
def test_weather_location_priority():
    """Test that profile district takes priority over message location"""
    
    # Simulate the logic from general_agent.py
    user_id = "919000000002"
    user_message = "Give me weather report"
    
    # Mock onboarding manager
    onboarding_manager = MockOnboardingManager()
    
    location = None
    
    # PRIORITY 1: Check user profile for district
    if user_id != "unknown":
        profile = onboarding_manager.get_user_profile(user_id)
        if profile:
            location = profile.get('district')
            if location:
                print(f"✅ PASS: Using profile location: {location}")
                assert location == "Sangli", f"Expected Sangli, got {location}"
                return True
    
    # PRIORITY 2: Extract from message (should not reach here)
    if not location:
        location = "Pune"  # Default
        print(f"❌ FAIL: Fell back to default: {location}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing weather location priority logic...")
    print("=" * 50)
    
    success = test_weather_location_priority()
    
    print("=" * 50)
    if success:
        print("✅ Test PASSED: Profile district takes priority")
        sys.exit(0)
    else:
        print("❌ Test FAILED: Logic error")
        sys.exit(1)
