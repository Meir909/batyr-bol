#!/usr/bin/env python3
"""
Test script for Gemini API integration
This script tests the functionality of the Gemini API integration
"""

import json
import os
import sys

def test_gemini_integration():
    """Test the Gemini API integration functionality"""
    print("Testing Gemini API integration...")
    
    # Test 1: Check if .env.example file exists and contains GEMINI_API_KEY
    print("\nTest 1: Checking .env.example file")
    try:
        if os.path.exists('.env.example'):
            with open('.env.example', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'GEMINI_API_KEY' in content:
                    print("✅ .env.example contains GEMINI_API_KEY placeholder")
                else:
                    print("❌ .env.example missing GEMINI_API_KEY placeholder")
        else:
            print("❌ .env.example file not found")
    except Exception as e:
        print(f"❌ Error reading .env.example: {e}")
    
    # Test 2: Check if GEMINI_API_SETUP.md documentation exists
    print("\nTest 2: Checking GEMINI_API_SETUP.md documentation")
    try:
        if os.path.exists('GEMINI_API_SETUP.md'):
            print("✅ GEMINI_API_SETUP.md documentation file exists")
        else:
            print("❌ GEMINI_API_SETUP.md documentation file not found")
    except Exception as e:
        print(f"❌ Error checking documentation: {e}")
    
    # Test 3: Check game_integration.js for API key handling
    print("\nTest 3: Checking game_integration.js for API key handling")
    try:
        if os.path.exists('game_integration.js'):
            with open('game_integration.js', 'r', encoding='utf-8') as f:
                content = f.read()
                checks = [
                    ('loadGeminiApiKey' in content, "loadGeminiApiKey method exists"),
                    ('geminiApiKey' in content, "geminiApiKey variable exists"),
                    ('YOUR_GEMINI_API_KEY' in content, "Placeholder for API key exists"),
                    ('fallback' in content.lower() or 'фолбэк' in content.lower(), "Fallback mechanism exists")
                ]
                
                for check, description in checks:
                    if check:
                        print(f"✅ {description}")
                    else:
                        print(f"❌ {description}")
        else:
            print("❌ game_integration.js file not found")
    except Exception as e:
        print(f"❌ Error checking game_integration.js: {e}")
    
    # Test 4: Check server.py for environment variable loading
    print("\nTest 4: Checking server.py for environment variable loading")
    try:
        if os.path.exists('server.py'):
            with open('server.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'load_dotenv' in content:
                    print("✅ Server loads environment variables with load_dotenv")
                else:
                    print("❌ Server does not load environment variables")
        else:
            print("❌ server.py file not found")
    except Exception as e:
        print(f"❌ Error checking server.py: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_gemini_integration()