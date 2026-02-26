#!/usr/bin/env python3
"""
Test script to verify onboarding flow
Tests the new user detection logic
"""

import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from onboarding.farmer_onboarding import onboarding_manager

def test_new_user_detection():
    """Test new user detection"""
    print("=" * 60)
    print("TEST 1: New User Detection")
    print("=" * 60)
    
    test_user_id = "test_919876543210"
    
    # Check if user is new
    is_new = onboarding_manager.is_new_user(test_user_id)
    print(f"✓ User {test_user_id} is new: {is_new}")
    
    assert is_new == True, "User should be new"
    print("✅ Test passed: New user detected correctly\n")


def test_onboarding_flow():
    """Test complete onboarding flow"""
    print("=" * 60)
    print("TEST 2: Complete Onboarding Flow")
    print("=" * 60)
    
    test_user_id = "test_919876543211"
    
    # Step 1: First message (should trigger welcome)
    print("\n📱 Step 1: User sends 'Hi'")
    response, completed = onboarding_manager.process_onboarding_message(test_user_id, "Hi")
    print(f"Bot: {response[:100]}...")
    print(f"Completed: {completed}")
    assert not completed, "Should not be completed yet"
    assert "नाम" in response, "Should ask for name"
    
    # Step 2: Provide name
    print("\n📱 Step 2: User provides name")
    response, completed = onboarding_manager.process_onboarding_message(test_user_id, "मेरा नाम राजेश है")
    print(f"Bot: {response[:100]}...")
    print(f"Completed: {completed}")
    assert not completed, "Should not be completed yet"
    assert "फसल" in response, "Should ask for crops"
    
    # Step 3: Provide crops
    print("\n📱 Step 3: User provides crops")
    response, completed = onboarding_manager.process_onboarding_message(test_user_id, "गेहूं और धान")
    print(f"Bot: {response[:100]}...")
    print(f"Completed: {completed}")
    assert not completed, "Should not be completed yet"
    assert "जमीन" in response, "Should ask for land"
    
    # Step 4: Provide land
    print("\n📱 Step 4: User provides land size")
    response, completed = onboarding_manager.process_onboarding_message(test_user_id, "5 एकड़")
    print(f"Bot: {response[:100]}...")
    print(f"Completed: {completed}")
    assert not completed, "Should not be completed yet"
    assert "गांव" in response, "Should ask for village"
    
    # Step 5: Provide village
    print("\n📱 Step 5: User provides village")
    response, completed = onboarding_manager.process_onboarding_message(test_user_id, "पुणे")
    print(f"Bot: {response[:100]}...")
    print(f"Completed: {completed}")
    assert completed, "Should be completed now"
    assert "रजिस्ट्रेशन पूरा" in response, "Should show completion message"
    
    # Step 6: Verify profile saved
    print("\n📱 Step 6: Verify profile saved")
    profile = onboarding_manager.get_user_profile(test_user_id)
    print(f"Profile: {json.dumps(profile, indent=2, ensure_ascii=False)}")
    assert profile is not None, "Profile should exist"
    assert profile.get("name"), "Profile should have name"
    assert profile.get("crops"), "Profile should have crops"
    assert profile.get("land_acres"), "Profile should have land"
    assert profile.get("village"), "Profile should have village"
    
    # Step 7: Verify user is no longer new
    print("\n📱 Step 7: Verify user is no longer new")
    is_new = onboarding_manager.is_new_user(test_user_id)
    print(f"User is new: {is_new}")
    assert not is_new, "User should not be new anymore"
    
    print("\n✅ Test passed: Complete onboarding flow works correctly\n")


def test_existing_user():
    """Test existing user detection"""
    print("=" * 60)
    print("TEST 3: Existing User Detection")
    print("=" * 60)
    
    # Use user from previous test
    test_user_id = "test_919876543211"
    
    # Check if user is new
    is_new = onboarding_manager.is_new_user(test_user_id)
    print(f"✓ User {test_user_id} is new: {is_new}")
    
    assert is_new == False, "User should not be new"
    
    # Get profile
    profile = onboarding_manager.get_user_profile(test_user_id)
    print(f"✓ Profile exists: {profile is not None}")
    print(f"✓ Name: {profile.get('name')}")
    print(f"✓ Village: {profile.get('village')}")
    
    print("✅ Test passed: Existing user detected correctly\n")


def test_user_status_check():
    """Test the check_user_status helper function logic"""
    print("=" * 60)
    print("TEST 4: User Status Check Logic")
    print("=" * 60)
    
    # Test new user
    new_user_id = "test_new_user"
    is_new = onboarding_manager.is_new_user(new_user_id)
    state, data = onboarding_manager.get_onboarding_state(new_user_id)
    profile = None if is_new else onboarding_manager.get_user_profile(new_user_id)
    
    print(f"New User:")
    print(f"  is_new: {is_new}")
    print(f"  state: {state}")
    print(f"  has_profile: {profile is not None}")
    
    assert is_new == True, "Should be new user"
    assert profile is None, "Should not have profile"
    
    # Test existing user
    existing_user_id = "test_919876543211"
    is_new = onboarding_manager.is_new_user(existing_user_id)
    state, data = onboarding_manager.get_onboarding_state(existing_user_id)
    profile = None if is_new else onboarding_manager.get_user_profile(existing_user_id)
    
    print(f"\nExisting User:")
    print(f"  is_new: {is_new}")
    print(f"  state: {state}")
    print(f"  has_profile: {profile is not None}")
    
    assert is_new == False, "Should not be new user"
    assert profile is not None, "Should have profile"
    
    print("\n✅ Test passed: User status check works correctly\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("KISAANMITRA ONBOARDING TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_new_user_detection()
        test_onboarding_flow()
        test_existing_user()
        test_user_status_check()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nOnboarding system is working correctly.")
        print("Ready to deploy to AWS Lambda.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
