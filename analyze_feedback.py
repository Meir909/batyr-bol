#!/usr/bin/env python3
"""
Feedback Analysis Script for BATYR BOL
Analyzes user feedback to improve the platform
"""

import json
import re
from collections import Counter
import os

def load_feedback():
    """Load feedback from feedback.json file"""
    feedback_data = []
    if os.path.exists("feedback.json"):
        try:
            with open("feedback.json", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        feedback_data.append(json.loads(line))
        except Exception as e:
            print(f"Error loading feedback: {e}")
    return feedback_data

def analyze_feedback(feedback_data):
    """Analyze feedback for common themes and sentiments"""
    if not feedback_data:
        print("No feedback data available.")
        return
    
    print("=== FEEDBACK ANALYSIS REPORT ===\n")
    
    # Basic statistics
    print(f"Total feedback entries: {len(feedback_data)}")
    
    # Extract keywords
    positive_keywords = ['хорошо', 'отлично', 'нравится', 'good', 'great', 'love', 'awesome']
    negative_keywords = ['плохо', 'ужасно', 'ненавижу', 'bad', 'terrible', 'hate', 'awful']
    suggestion_keywords = ['хотелось бы', 'нужно', 'should', 'need', 'want', 'would like']
    
    positive_count = 0
    negative_count = 0
    suggestion_count = 0
    
    all_words = []
    
    for entry in feedback_data:
        feedback_text = entry.get('feedback', '').lower()
        all_words.extend(re.findall(r'\b\w+\b', feedback_text))
        
        # Count sentiment keywords
        if any(word in feedback_text for word in positive_keywords):
            positive_count += 1
        if any(word in feedback_text for word in negative_keywords):
            negative_count += 1
        if any(word in feedback_text for word in suggestion_keywords):
            suggestion_count += 1
    
    print(f"\nSentiment Analysis:")
    print(f"  Positive feedback: {positive_count}")
    print(f"  Negative feedback: {negative_count}")
    print(f"  Suggestions: {suggestion_count}")
    
    # Most common words (excluding common stop words)
    stop_words = {'и', 'в', 'не', 'на', 'с', 'о', 'как', 'то', 'это', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'}
    filtered_words = [word for word in all_words if len(word) > 3 and word not in stop_words]
    word_freq = Counter(filtered_words)
    
    print(f"\nMost common words in feedback:")
    for word, count in word_freq.most_common(10):
        print(f"  {word}: {count}")
    
    # Suggestions analysis
    print(f"\n=== SUGGESTIONS FOR IMPROVEMENT ===")
    for entry in feedback_data:
        feedback_text = entry.get('feedback', '')
        username = entry.get('username', 'Anonymous')
        if any(word in feedback_text.lower() for word in suggestion_keywords):
            print(f"\nFrom {username}:")
            print(f"  \"{feedback_text}\"")

def suggest_improvements(feedback_data):
    """Generate improvement suggestions based on feedback"""
    print(f"\n=== RECOMMENDED IMPROVEMENTS ===")
    
    # Common improvement areas based on keywords
    improvements = {
        'more_content': ['больше', 'more', 'еще'],
        'better_ui': ['интерфейс', 'interface', 'design', 'ui'],
        'more_missions': ['миссии', 'missions', 'задания', 'tasks'],
        'voice_features': ['голос', 'voice', 'audio'],
        'language_support': ['язык', 'language', 'перевод', 'translation'],
        'performance': ['медленно', 'slow', 'быстро', 'fast', 'lag']
    }
    
    found_areas = set()
    
    for entry in feedback_data:
        feedback_text = entry.get('feedback', '').lower()
        for area, keywords in improvements.items():
            if any(keyword in feedback_text for keyword in keywords):
                found_areas.add(area)
    
    if 'more_content' in found_areas:
        print("➕ Add more educational content and missions")
    if 'better_ui' in found_areas:
        print("🎨 Improve user interface and design")
    if 'more_missions' in found_areas:
        print("🎯 Create additional missions for different topics")
    if 'voice_features' in found_areas:
        print("🎤 Enhance voice mission features and recognition")
    if 'language_support' in found_areas:
        print("🌐 Improve multilingual support")
    if 'performance' in found_areas:
        print("⚡ Optimize performance and responsiveness")
    
    if not found_areas:
        print("No specific improvement areas identified from feedback.")

if __name__ == "__main__":
    feedback_data = load_feedback()
    analyze_feedback(feedback_data)
    suggest_improvements(feedback_data)
    print(f"\n=== END OF REPORT ===")