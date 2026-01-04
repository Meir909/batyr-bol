#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for BATYR BOL Telegram bot
This script verifies that the bot is working correctly and all features are functional.
"""

import asyncio
import logging
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes
from unittest.mock import AsyncMock, Mock

# Import the bot module
import bb_bot

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mission_count():
    """Test that we have a sufficient number of missions"""
    mission_count = len(bb_bot.MISSIONS)
    print(f"✓ Mission count test: {mission_count} missions found")
    assert mission_count >= 100, f"Expected at least 100 missions, got {mission_count}"
    print("✓ Mission count is sufficient (≥100)")

def test_mission_types():
    """Test that we have all required mission types"""
    mission_types = set()
    for mission in bb_bot.MISSIONS:
        mission_types.add(mission["type"])
    
    required_types = {"history", "lang", "grammar", "thinking", "voice"}
    missing_types = required_types - mission_types
    
    print(f"✓ Mission types test: Found types {mission_types}")
    assert not missing_types, f"Missing mission types: {missing_types}"
    print("✓ All required mission types are present")

async def test_direct_answer_functionality():
    """Test the direct answer functionality"""
    print("Testing direct answer functionality...")
    
    # Create a mock update and context
    update = Mock(spec=Update)
    update.effective_user = Mock()
    update.effective_user.id = 12345
    update.message = Mock(spec=Message)
    update.message.text = "хан"
    update.message.reply_text = AsyncMock()
    
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = None  # No command arguments for direct answer
    
    # Initialize user data
    bb_bot.users[12345] = {
        "xp": 0,
        "level": 1,
        "lang": "kz",
        "done": set(),
        "last_day": bb_bot.today(),
        "streak": 1,
        "current_mission": None,
        "daily_missions": [bb_bot.MISSIONS[0]]  # First mission for testing
    }
    
    # Test direct answer
    await bb_bot.answer(update, context)
    
    # Check if reply was called
    update.message.reply_text.assert_called()
    print("✓ Direct answer functionality test passed")

async def test_command_answer_functionality():
    """Test the command-based answer functionality"""
    print("Testing command-based answer functionality...")
    
    # Create a mock update and context
    update = Mock(spec=Update)
    update.effective_user = Mock()
    update.effective_user.id = 12346
    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()
    
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = ["1", "хан"]  # Command arguments for /answer 1 хан
    
    # Initialize user data
    bb_bot.users[12346] = {
        "xp": 0,
        "level": 1,
        "lang": "kz",
        "done": set(),
        "last_day": bb_bot.today(),
        "streak": 1,
        "current_mission": None,
        "daily_missions": [bb_bot.MISSIONS[0]]  # First mission for testing
    }
    
    # Test command-based answer
    await bb_bot.answer(update, context)
    
    # Check if reply was called
    update.message.reply_text.assert_called()
    print("✓ Command-based answer functionality test passed")

async def test_voice_mission_handling():
    """Test voice mission handling"""
    print("Testing voice mission handling...")
    
    # Create a mock update and context
    update = Mock(spec=Update)
    update.effective_user = Mock()
    update.effective_user.id = 12347
    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()
    
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    
    # Initialize user data with a voice mission
    voice_mission = None
    for mission in bb_bot.MISSIONS:
        if mission["type"] == "voice":
            voice_mission = mission
            break
    
    assert voice_mission is not None, "No voice mission found for testing"
    
    bb_bot.users[12347] = {
        "xp": 0,
        "level": 1,
        "lang": "kz",
        "done": set(),
        "last_day": bb_bot.today(),
        "streak": 1,
        "current_mission": None,
        "daily_missions": [voice_mission],
        "awaiting_voice_for_mission": 0  # Waiting for voice response for mission 0
    }
    
    # Test voice handler
    await bb_bot.voice_handler(update, context)
    
    # Check if reply was called
    update.message.reply_text.assert_called()
    print("✓ Voice mission handling test passed")

async def test_get_level_function():
    """Test the get_level helper function"""
    print("Testing get_level function...")
    
    # Test various XP values
    test_cases = [
        (0, 1),
        (5, 1),
        (10, 2),
        (20, 3),
        (30, 3),
        (50, 4),
        (100, 4)
    ]
    
    for xp, expected_level in test_cases:
        level = bb_bot.get_level(xp)
        assert level == expected_level, f"Expected level {expected_level} for {xp} XP, got {level}"
    
    print("✓ get_level function test passed")

async def run_all_tests():
    """Run all tests"""
    print("Starting bot functionality tests...\n")
    
    try:
        # Test mission count
        await test_mission_count()
        
        # Test mission types
        test_mission_types()
        
        # Test direct answer functionality
        await test_direct_answer_functionality()
        
        # Test command-based answer functionality
        await test_command_answer_functionality()
        
        # Test voice mission handling
        await test_voice_mission_handling()
        
        # Test helper functions
        await test_get_level_function()
        
        print("\n🎉 All tests passed! The bot is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run the tests
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)