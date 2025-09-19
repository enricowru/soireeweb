#!/usr/bin/env python3

import os
import sys
import django
from django.conf import settings

# Add the current directory to Python path
sys.path.append('.')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import our functions
from main.api.custom_theme_api import generate_event_entrance_prompt, select_reference_style

def test_prompt_generation():
    print("🎨 Testing Reference-Enhanced Prompt Generation\n")
    
    test_cases = [
        {
            'name': 'Modern Balloon Birthday',
            'event_type': 'birthday',
            'colors': ['blue', 'white'],
            'description': 'modern colorful balloon party',
            'pax': 50
        },
        {
            'name': 'Garden Wedding',
            'event_type': 'wedding',
            'colors': ['green', 'white'],
            'description': 'nature garden butterfly fairy',
            'pax': 100
        },
        {
            'name': 'Elegant Traditional Wedding',
            'event_type': 'wedding',
            'colors': ['gold', 'yellow'],
            'description': 'elegant traditional formal',
            'pax': 80
        },
        {
            'name': 'Rustic Wedding',
            'event_type': 'wedding',
            'colors': ['white', 'green'],
            'description': 'rustic wooden country style',
            'pax': 75
        }
    ]
    
    for case in test_cases:
        print(f"📝 {case['name']}")
        print(f"   Event: {case['event_type']}, Colors: {case['colors']}, Description: {case['description']}")
        
        # Test reference style selection
        selected_style = select_reference_style(case['event_type'], case['colors'], case['description'])
        print(f"   🎯 Selected Style: {selected_style}")
        
        # Generate prompt
        prompt = generate_event_entrance_prompt(case['event_type'], case['colors'], case['description'], case['pax'])
        print(f"   📝 Prompt Preview: {prompt[:150]}...")
        print("-" * 80)

if __name__ == '__main__':
    test_prompt_generation()