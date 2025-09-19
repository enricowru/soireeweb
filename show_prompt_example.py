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

def show_full_prompt_example():
    print("🎨 Full Enhanced Prompt Example\n")
    
    # Test with a balloon theme
    event_type = 'birthday'
    colors = ['blue', 'white']
    description = 'modern colorful balloon spiderman avengers'
    pax = 50
    
    print(f"Input:")
    print(f"  Event Type: {event_type}")
    print(f"  Colors: {colors}")
    print(f"  Description: {description}")
    print(f"  Guests: {pax}")
    print()
    
    selected_style = select_reference_style(event_type, colors, description)
    print(f"Selected Reference Style: {selected_style}")
    print()
    
    prompt = generate_event_entrance_prompt(event_type, colors, description, pax)
    print("Generated Prompt:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)

if __name__ == '__main__':
    show_full_prompt_example()