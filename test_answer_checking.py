#!/usr/bin/env python3
"""
Test script for Groq API answer checking functionality
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_answer_checking():
    """Test the Groq API answer checking with fallback"""
    
    # Test configuration
    server_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "question": "Қазақ хандығы қашан құрылды?",
            "user_answer": "1465 жылы",
            "correct_answer": "1465 жылы",
            "context": "Қазақ хандығы - қазақ халқының мемлекеттігінің негізі қаланған тарихи оқиға. 1465 жылы Қазақ хандығы құрылды."
        },
        {
            "question": "Абылай хан қандай қасиеттерге ие болды?",
            "user_answer": "Ол дана басшы және батыр болған",
            "correct_answer": None,
            "context": "Абылай хан - қазақ халқының ұлы батыры, мемлекет қайраткері. Ол 18 ғасырда қазақ жүздерін біріктіріп, жоңғар шапқыншылығына қарсы күресті."
        },
        {
            "question": "Алдар Көсе кім болған?",
            "user_answer": "Ол ақылды адам болған",
            "correct_answer": 0,  # Multiple choice
            "context": "Алдар Көсе — қазақ ауыз әдебиетінің кейіпкері. Ол өте ақылды және қу адам болған."
        }
    ]
    
    print("🧪 Testing Groq API Answer Checking...")
    print("=" * 60)
    
    # Check if Groq API key is configured
    groq_api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
        print("⚠️  Groq API key not configured in .env file")
        print("📝 Please add your Groq API key to .env:")
        print("   GROQ_API_KEY=your_actual_api_key_here")
        print("\n🔄 Testing with fallback to simple checking...")
    else:
        print("✅ Groq API key found in .env")
        print("🚀 Testing with Groq API (will fallback if needed)...")
    
    print("\n" + "=" * 60)
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['question'][:50]}...")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{server_url}/api/answer/check",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    print(f"✅ Success!")
                    
                    # Show warning if fallback was used
                    if data.get('warning'):
                        print(f"⚠️  {data['warning']}")
                    
                    # Display results
                    print(f"📋 Is Correct: {result.get('is_correct', 'N/A')}")
                    print(f"📊 Score: {result.get('score', 'N/A')}/100")
                    print(f"💬 Feedback: {result.get('feedback', 'N/A')[:50]}...")
                    if result.get('explanation'):
                        print(f"📖 Explanation: {result['explanation'][:50]}...")
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
    
    print("\n" + "=" * 60)
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
    test_answer_checking()
