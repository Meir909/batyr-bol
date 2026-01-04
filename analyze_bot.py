#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis script for BATYR BOL Telegram bot
This script analyzes the bot code without executing it to verify its structure and functionality.
"""

import ast
import json
import re

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
    # Count occurrences of mission type declarations
    mission_count = content.count('"type":')
    return mission_count

def check_mission_types(content):
    """Check what types of missions are present"""
    # Look for mission type patterns
    types = set()
    
    # Find all mission type declarations
    type_matches = re.findall(r'"type":\s*"([^"]+)"', content)
    types.update(type_matches)
    
    return sorted(list(types))

def check_for_key_features(content):
    """Check for key features in the bot implementation"""
    features = {
        "direct_answer": "Direct answer functionality" in content or "direct answers" in content,
        "voice_handling": "voice_handler" in content,
        "mission_selection": "random.sample" in content,
        "startup_message": "Бот запущен и готов к работе" in content,
        "multiple_mission_types": len(check_mission_types(content)) > 1
    }
    return features

def analyze_functions(content):
    """Analyze what functions are defined in the bot"""
    # Parse the Python code
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Syntax error in bot file: {e}")
        return []
    
    # Find all function definitions
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    
    return functions

def check_imports(content):
    """Check what modules are imported"""
    # Parse the Python code
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Syntax error in bot file: {e}")
        return []
    
    # Find all import statements
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    
    return imports

def main():
    """Main analysis function"""
    print("Analyzing BATYR BOL Telegram bot...\n")
    
    # Read the bot file
    content = read_bot_file()
    if content is None:
        return False
    
    print("✓ Bot file read successfully\n")
    
    # Count missions
    mission_count = count_missions(content)
    print(f"📊 Mission count: {mission_count}")
    
    # Check mission types
    mission_types = check_mission_types(content)
    print(f"📋 Mission types found: {mission_types}")
    
    # Analyze functions
    functions = analyze_functions(content)
    print(f"⚙️  Functions defined: {len(functions)}")
    print(f"   Function names: {functions}")
    
    # Check imports
    imports = check_imports(content)
    print(f"📦 Imports: {imports}")
    
    # Check for key features
    features = check_for_key_features(content)
    print("\n🔍 Key features implemented:")
    for feature, description in features.items():
        status = "✅" if features[feature] else "❌"
        print(f"   {status} {description}")
    
    # Summary
    print("\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)
    
    # Check if we have sufficient missions
    if mission_count >= 100:
        print("✅ Sufficient mission count (≥100)")
    elif mission_count >= 50:
        print("⚠️  Moderate mission count (≥50 but <100)")
    else:
        print("❌ Insufficient mission count (<50)")
    
    # Check for required mission types
    required_types = {"history", "lang", "grammar", "thinking", "voice"}
    missing_types = required_types - set(mission_types)
    if not missing_types:
        print("✅ All required mission types present")
    else:
        print(f"❌ Missing mission types: {missing_types}")
    
    # Check for required functions
    required_functions = {"start", "answer", "voice_handler", "missions", "get_level"}
    missing_functions = required_functions - set(functions)
    if not missing_functions:
        print("✅ All required functions present")
    else:
        print(f"❌ Missing functions: {missing_functions}")
    
    # Check for key features
    key_features_count = sum(features.values())
    if key_features_count >= 4:
        print("✅ Most key features implemented")
    elif key_features_count >= 2:
        print("⚠️  Some key features implemented")
    else:
        print("❌ Few key features implemented")
    
    print("\n🎉 Analysis complete!")
    return True

if __name__ == "__main__":
    main()