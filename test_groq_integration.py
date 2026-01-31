#!/usr/bin/env python3
"""
Test script for Groq API integration with fallback
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_integration():
    """Test the Groq API integration with fallback"""
    
    # Test configuration
    server_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {"topic": "Қазақ хандығы", "level": 1},
        {"topic": "Абылай хан", "level": 2},
        {"topic": "Ертөстік", "level": 1},
        {"topic": "Алдар Көсе", "level": 1}
    ]
    
    print("🧪 Testing Groq API Integration...")
    print("=" * 50)
    
    # Check if Groq API key is configured
    groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
        print("⚠️  Groq API key not configured in .env file")
        print("📝 Please add your Groq API key to .env:")
        print("   GROQ_API_KEY=your_actual_api_key_here")
        print("\n🔄 Testing with fallback to local model...")
    else:
        print("✅ Groq API key found in .env")
        print("🚀 Testing with Groq API (will fallback if needed)...")
    
    print("\n" + "=" * 50)
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['topic']} (Level {test_case['level']})")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{server_url}/api/content/generate",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    content = data.get('content', {})
                    print(f"✅ Success!")
                    
                    # Check if warning is present (fallback used)
                    if data.get('warning'):
                        print(f"⚠️  {data['warning']}")
                    
                    # Display content structure
                    print(f"📋 Topic: {content.get('topic', 'N/A')}")
                    print(f"📖 Text KZ: {content.get('text_kz', 'N/A')[:50]}...")
                    print(f"❓ Questions: {len(content.get('questions_kz', []))}")
                    print(f"🔢 Options: {len(content.get('options_kz', []))}")
                    
                    # Check if Russian content is present
                    if content.get('text_ru'):
                        print(f"🇷🇺 Russian translation available")
                else:
                    print(f"❌ API Error: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Server not running")
            print("💡 Please start the server with: python server.py")
            break
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")
    
    # Instructions for setting up Groq API
    if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
        print("\n📋 How to set up Groq API:")
        print("1. Go to https://console.groq.com/keys")
        print("2. Create a new API key")
        print("3. Add it to your .env file:")
        print("   GROQ_API_KEY=gsk_your_actual_key_here")
        print("4. Restart the server")

if __name__ == "__main__":
    test_groq_integration()
