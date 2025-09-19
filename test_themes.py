#!/usr/bin/env python
"""
Test script to validate theme functionality fixes
"""

import sys
import os

# Add the Django project to the path
sys.path.append('d:/SYSTEMS/webpython/soireeweb')
os.chdir('d:/SYSTEMS/webpython/soireeweb')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from main.themes import get_themes_for_event_type

def test_theme_mapping():
    """Test that event type mapping works correctly"""
    
    print("Testing theme mapping fixes...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "Birthday Party",
        "BIRTHDAY", 
        "birthday",
        "Kiddie Party",
        "KIDDIE PARTY",
        "Christening", 
        "CHRISTENING",
        "Corporate"
    ]
    
    for event_type in test_cases:
        try:
            themes = get_themes_for_event_type(event_type)
            print(f"✅ {event_type}: Found {len(themes)} themes")
            if themes:
                print(f"   Theme names: {[theme['name'] for theme in themes]}")
            else:
                print(f"   No themes found for event type: {event_type}")
        except Exception as e:
            print(f"❌ {event_type}: Error - {e}")
        print()

if __name__ == "__main__":
    test_theme_mapping()