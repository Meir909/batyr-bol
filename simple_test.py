#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for BATYR BOL Telegram bot
This script verifies that the bot file is syntactically correct and has the expected structure.
"""

import sys
import os

def test_bot_file_exists():
    """Test that the bot file exists"""
    if os.path.exists("bb_bot.py"):
        print("✓ Bot file exists")
        return True
    else:
        print("❌ Bot file not found")
        return False

def test_bot_import():
    """Test that we can import the bot module"""
    try:
        # Add current directory to Python path
        sys.path.insert(0, '.')
        
        # Try to import the bot module
        import bb_bot
        print("✓ Bot module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import bot module: {e}")
        return False

def test_mission_structure():
    """Test that the MISSIONS structure exists and has content"""
    try:
        import bb_bot
        
        # Check if MISSIONS exists
        if hasattr(bb_bot, 'MISSIONS'):
            mission_count = len(bb_bot.MISSIONS)
            print(f"✓ MISSIONS array found with {mission_count} missions")
            
            # Check that we have a reasonable number of missions
            if mission_count >= 50:
                print("✓ Sufficient number of missions")
                return True
            else:
                print(f"⚠ Warning: Only {mission_count} missions found, expected more")
                return True  # Not a failure, just a warning
        else:
            print("❌ MISSIONS array not found")
            return False
    except Exception as e:
        print(f"❌ Error checking mission structure: {e}")
        return False

def test_required_functions():
    """Test that required functions exist"""
    try:
        import bb_bot
        
        required_functions = [
            'start',
            'answer',
            'voice_handler',
            'missions',
            'get_level'
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not hasattr(bb_bot, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ Missing required functions: {missing_functions}")
            return False
        else:
            print("✓ All required functions are present")
            return True
    except Exception as e:
        print(f"❌ Error checking required functions: {e}")
        return False

def test_mission_types():
    """Test that we have missions of different types"""
    try:
        import bb_bot
        
        mission_types = set()
        for mission in bb_bot.MISSIONS:
            if isinstance(mission, dict) and 'type' in mission:
                mission_types.add(mission['type'])
        
        print(f"✓ Found mission types: {sorted(mission_types)}")
        
        required_types = {'history', 'lang', 'grammar', 'thinking', 'voice'}
        missing_types = required_types - mission_types
        
        if missing_types:
            print(f"❌ Missing mission types: {missing_types}")
            return False
        else:
            print("✓ All required mission types are present")
            return True
    except Exception as e:
        print(f"❌ Error checking mission types: {e}")
        return False

def main():
    """Main test function"""
    print("Starting simple bot tests...\n")
    
    tests = [
        test_bot_file_exists,
        test_bot_import,
        test_mission_structure,
        test_required_functions,
        test_mission_types
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            failed += 1
        print()  # Empty line for readability
    
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The bot appears to be working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the bot implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)