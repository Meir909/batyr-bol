#!/usr/bin/env python3
"""
Download royalty-free photos for BATYR BOL from Unsplash
Requires: requests, urllib3
Install: pip install requests urllib3
"""

import os
import requests
from pathlib import Path
from urllib.parse import urlencode

# Configuration
UNSPLASH_API_BASE = "https://api.unsplash.com"
UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY_HERE"  # Get from https://unsplash.com/developers

# Photo requirements
PHOTOS_CONFIG = {
    "hero": {
        "path": "assets/images/hero",
        "files": [
            {
                "name": "intro-hero.jpg",
                "query": "kazakh steppe landscape mountains",
                "width": 1920,
                "height": 1080,
            }
        ]
    },
    "features": {
        "path": "assets/images/features",
        "files": [
            {"name": "game-learning.jpg", "query": "student learning game education", "width": 400, "height": 300},
            {"name": "history-heroes.jpg", "query": "historical warriors heroes ancient", "width": 400, "height": 300},
            {"name": "kazakh-language.jpg", "query": "language learning teaching books", "width": 400, "height": 300},
            {"name": "missions-ratings.jpg", "query": "competition leaderboard achievements", "width": 400, "height": 300},
            {"name": "historical-accuracy.jpg", "query": "history book research ancient", "width": 400, "height": 300},
            {"name": "learning-paths.jpg", "query": "education path learning journey", "width": 400, "height": 300},
            {"name": "language-vocabulary.jpg", "query": "dictionary words vocabulary language", "width": 400, "height": 300},
            {"name": "cultural-context.jpg", "query": "culture tradition ceremony ethnic", "width": 400, "height": 300},
        ]
    },
    "characters": {
        "path": "assets/images/characters",
        "files": [
            {"name": "abilay-khan.jpg", "query": "warrior king historical portrait strong", "width": 800, "height": 1000},
            {"name": "abilay-khan-mini.jpg", "query": "warrior king historical portrait strong", "width": 200, "height": 250},
            {"name": "abai.jpg", "query": "poet writer intellectual noble portrait", "width": 800, "height": 1000},
            {"name": "abai-mini.jpg", "query": "poet writer intellectual noble portrait", "width": 200, "height": 250},
            {"name": "aiteke-bi.jpg", "query": "elder wise man historical figure portrait", "width": 800, "height": 1000},
            {"name": "aiteke-bi-mini.jpg", "query": "elder wise man historical figure portrait", "width": 200, "height": 250},
        ]
    },
    "eras": {
        "path": "assets/images/eras",
        "files": [
            {"name": "steppe-civilizations.jpg", "query": "ancient civilization steppe nomadic settlement", "width": 400, "height": 250},
            {"name": "turkic-khaganates.jpg", "query": "ancient empire warriors khaganate medieval", "width": 400, "height": 250},
            {"name": "kazakh-khanate.jpg", "query": "khanate kingdom empire historical", "width": 400, "height": 250},
            {"name": "heroes-legends.jpg", "query": "heroes legend mythology heroic", "width": 400, "height": 250},
        ]
    },
    "backgrounds": {
        "path": "assets/images/backgrounds",
        "files": [
            {"name": "auth-background.jpg", "query": "dark background texture abstract modern", "width": 1920, "height": 1080}
        ]
    }
}

def create_directories():
    """Create all necessary directories"""
    for category, config in PHOTOS_CONFIG.items():
        path = config["path"]
        os.makedirs(path, exist_ok=True)
        print(f"✓ Created directory: {path}")

def download_from_unsplash(query, width, height, save_path):
    """Download a photo from Unsplash API"""
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY_HERE":
        print(f"⚠ Unsplash API key not set. Skipping: {save_path}")
        return False

    try:
        # Search for photos
        search_url = f"{UNSPLASH_API_BASE}/search/photos"
        params = {
            "query": query,
            "page": 1,
            "per_page": 1,
            "client_id": UNSPLASH_ACCESS_KEY,
            "orientation": "landscape" if width > height else "portrait"
        }

        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if not data.get("results"):
            print(f"✗ No photos found for: {query}")
            return False

        # Get download URL
        photo = data["results"][0]
        download_url = photo["links"]["download"]

        # Download photo
        photo_response = requests.get(download_url, timeout=10)
        photo_response.raise_for_status()

        # Save photo
        with open(save_path, "wb") as f:
            f.write(photo_response.content)

        print(f"✓ Downloaded: {os.path.basename(save_path)} ({len(photo_response.content) / 1024:.1f}KB)")
        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading {query}: {str(e)}")
        return False

def download_from_pexels(query, width, height, save_path):
    """Download a photo from Pexels (no API key needed, but limited)"""
    try:
        print(f"  Attempting Pexels fallback for: {query}")
        # Note: Pexels requires API key too, so this is a placeholder
        print(f"⚠ Pexels download not configured (requires API key)")
        return False
    except Exception as e:
        print(f"✗ Error with Pexels: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("BATYR BOL - Photo Downloader")
    print("=" * 60)

    # Check API key
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY_HERE":
        print("\n⚠ WARNING: Unsplash API key not configured!")
        print("\nTo use this script:")
        print("1. Go to: https://unsplash.com/developers")
        print("2. Register and get your Access Key")
        print("3. Replace 'YOUR_UNSPLASH_ACCESS_KEY_HERE' in this script")
        print("\nFor now, I'll show you how to download photos manually...")
        print_manual_instructions()
        return

    # Create directories
    print("\n1. Creating directories...")
    create_directories()

    # Download photos
    print("\n2. Downloading photos...")
    total = 0
    downloaded = 0

    for category, config in PHOTOS_CONFIG.items():
        print(f"\n{category.upper()}:")
        for file_info in config["files"]:
            total += 1
            path = config["path"]
            file_path = os.path.join(path, file_info["name"])

            # Skip if already exists
            if os.path.exists(file_path):
                print(f"✓ Already exists: {file_info['name']}")
                downloaded += 1
                continue

            # Try download
            if download_from_unsplash(
                file_info["query"],
                file_info["width"],
                file_info["height"],
                file_path
            ):
                downloaded += 1
            else:
                print(f"  Trying fallback source...")
                download_from_pexels(
                    file_info["query"],
                    file_info["width"],
                    file_info["height"],
                    file_path
                )

    print("\n" + "=" * 60)
    print(f"Result: {downloaded}/{total} photos downloaded")
    print("=" * 60)

def print_manual_instructions():
    """Print instructions for manual download"""
    print("\n" + "=" * 60)
    print("MANUAL DOWNLOAD INSTRUCTIONS")
    print("=" * 60)

    print("\nYou can download photos manually from these sources:")
    print("- Unsplash.com (Free, high quality, no login required)")
    print("- Pexels.com (Free, high quality)")
    print("- Pixabay.com (Free, good quality)")

    print("\nHERO SECTION (1 photo):")
    print("- intro-hero.jpg (1920x1080): Search 'kazakh steppe landscape'")

    print("\nFEATURES SECTION (8 photos, 400x300 each):")
    features = [
        ("game-learning.jpg", "student learning game education"),
        ("history-heroes.jpg", "historical warriors heroes"),
        ("kazakh-language.jpg", "language learning books"),
        ("missions-ratings.jpg", "competition leaderboard"),
        ("historical-accuracy.jpg", "history book research"),
        ("learning-paths.jpg", "education learning journey"),
        ("language-vocabulary.jpg", "dictionary words vocabulary"),
        ("cultural-context.jpg", "culture tradition ethnic"),
    ]
    for name, query in features:
        print(f"  - {name}: Search '{query}'")

    print("\nCHARACTERS SECTION (6 photos):")
    print("  - abilay-khan.jpg (800x1000): Search 'warrior king portrait'")
    print("  - abilay-khan-mini.jpg (200x250): Same as above (resize)")
    print("  - abai.jpg (800x1000): Search 'poet intellectual portrait'")
    print("  - abai-mini.jpg (200x250): Same as above (resize)")
    print("  - aiteke-bi.jpg (800x1000): Search 'elder wise man portrait'")
    print("  - aiteke-bi-mini.jpg (200x250): Same as above (resize)")

    print("\nERAS SECTION (4 photos, 400x250 each):")
    eras = [
        ("steppe-civilizations.jpg", "ancient civilization steppe"),
        ("turkic-khaganates.jpg", "ancient empire medieval"),
        ("kazakh-khanate.jpg", "khanate kingdom historical"),
        ("heroes-legends.jpg", "heroes legend mythology"),
    ]
    for name, query in eras:
        print(f"  - {name}: Search '{query}'")

    print("\nBACKGROUND SECTION (1 photo):")
    print("- auth-background.jpg (1920x1080): Search 'dark texture abstract'")

    print("\nAFTER DOWNLOADING:")
    print("1. Place files in correct folders (assets/images/[category]/)")
    print("2. Use TinyPNG to compress images (optional but recommended)")
    print("3. Refresh browser to see new photos")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Error: 'requests' module not found")
        print("Install it with: pip install requests")
        print_manual_instructions()
        exit(1)

    main()
