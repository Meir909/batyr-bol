#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runtime test script for BATYR BOL Telegram bot
This script provides a way to verify the bot is working correctly when it's running.
To use this script:
1. Make sure the bot is running (python bb_bot.py)
2. Run this script (python test_runtime.py)
"""

import requests
import time
import sys

def check_bot_running():
    """
    Check if the bot is running by looking for the process.
    Note: This is a simplified check and may not work on all systems.
    """
    import subprocess
    try:
        # This will work on Windows
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        if "python.exe" in result.stdout:
            return True
        return False
    except:
        # Fallback: try to import the bot and check if it has the expected structure
        try:
            import bb_bot
            return hasattr(bb_bot, 'MISSIONS') and hasattr(bb_bot, 'answer')
        except:
            return False

def print_test_instructions():
    """Print instructions for testing the bot manually"""
    print("🔧 MANUAL TESTING INSTRUCTIONS")
    print("="*50)
    print("To test the bot functionality, you can:")
    print()
    print("1. Start the bot:")
    print("   python bb_bot.py")
    print()
    print("2. Test the following features:")
    print("   ✅ Send /start to initialize")
    print("   ✅ Send /missions to get daily missions")
    print("   ✅ Try answering with /answer command:")
    print("      /answer 1 хан")
    print("   ✅ Try answering directly without command:")
    print("      хан")
    print("   ✅ Try voice missions by sending voice messages")
    print("   ✅ Check /profile and /leaderboard commands")
    print()
    print("3. Expected behaviors:")
    print("   ✅ Bot should display 'Бот запущен и готов к работе' on startup")
    print("   ✅ Users should get 5 random missions daily")
    print("   ✅ Users can answer with or without /answer command")
    print("   ✅ Voice missions should be processed correctly")
    print("   ✅ XP should be awarded for correct answers")

def main():
    """Main function"""
    print("🚀 BATYR BOL Bot Runtime Test")
    print("="*40)
    print()
    
    # Check if bot appears to be running or available
    print("🔍 Checking bot availability...")
    bot_available = check_bot_running()
    
    if bot_available:
        print("✅ Bot appears to be available")
    else:
        print("⚠️  Bot may not be running")
    
    print()
    print_test_instructions()
    
    print("\n" + "="*50)
    print("💡 TIP: For automated testing, you would need to")
    print("   use a Telegram bot testing framework or mock")
    print("   the Telegram API, which is beyond the scope")
    print("   of this simple verification script.")

if __name__ == "__main__":
    main()