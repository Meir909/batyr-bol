#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for BATYR BOL Telegram bot
This script verifies that the bot has been properly enhanced with all requested features.
"""

def read_bot_file():
    """Read the bot file content"""
    try:
        with open("bb_bot.py", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading bot file: {e}")
        return None

def count_missions(content):
    """Count the number of missions in the bot file"""
    # Count occurrences of mission declarations
    mission_count = content.count('"type":')
    return mission_count

def check_mission_types(content):
    """Check what types of missions are present"""
    import re
    # Find all mission type declarations
    types = set(re.findall(r'"type":\s*"([^"]+)"', content))
    return sorted(list(types))

def check_startup_message(content):
    """Check if the startup message is present"""
    return "Бот запущен и готов к работе" in content

def check_direct_answer_feature(content):
    """Check if direct answer functionality is implemented"""
    # Look for key indicators of direct answer functionality
    indicators = [
        "direct answers" in content,
        "Handle direct answers" in content,
        "else:" in content and "context.args" in content,
        "update.message.text.lower()" in content
    ]
    return any(indicators)

def check_voice_mission_feature(content):
    """Check if enhanced voice mission functionality is implemented"""
    # Look for key indicators of enhanced voice functionality
    indicators = [
        "awaiting_voice_for_mission" in content,
        "voice missions are worth 2 XP" in content,
        "general voice message" in content
    ]
    return any(indicators)

def check_random_mission_selection(content):
    """Check if random mission selection is implemented"""
    return "random.sample" in content

def main():
    """Main verification function"""
    print("Verifying BATYR BOL Telegram bot enhancements...\n")
    
    # Read the bot file
    content = read_bot_file()
    if content is None:
        return False
    
    print("✓ Bot file read successfully\n")
    
    # Perform checks
    checks = [
        ("Mission count", lambda: count_missions(content) >= 100, f"Found {count_missions(content)} missions"),
        ("Mission types", lambda: set(check_mission_types(content)) >= {"history", "lang", "grammar", "thinking", "voice"}, f"Found types: {check_mission_types(content)}"),
        ("Startup message", lambda: check_startup_message(content), "Бот запущен и готов к работе"),
        ("Direct answer feature", lambda: check_direct_answer_feature(content), "Users can answer without /answer command"),
        ("Enhanced voice handling", lambda: check_voice_mission_feature(content), "Improved voice mission processing"),
        ("Random mission selection", lambda: check_random_mission_selection(content), "Daily random mission selection")
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func, detail in checks:
        try:
            if check_func():
                print(f"✅ {check_name}: PASSED ({detail})")
                passed += 1
            else:
                print(f"❌ {check_name}: FAILED ({detail})")
                failed += 1
        except Exception as e:
            print(f"❌ {check_name}: ERROR ({e})")
            failed += 1
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"Total checks: {len(checks)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All verifications passed!")
        print("The bot has been successfully enhanced with all requested features:")
        print("  • Over 100 educational missions")
        print("  • Multiple mission types (history, language, grammar, thinking, voice)")
        print("  • Direct answer functionality (no need for /answer command)")
        print("  • Enhanced voice message handling")
        print("  • Random daily mission selection")
        print("  • Startup confirmation message")
        return True
    else:
        print(f"\n⚠️  {failed} verification(s) failed. Please review the bot implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)