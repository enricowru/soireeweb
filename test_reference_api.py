#!/usr/bin/env python3

import requests
import json

def test_reference_enhanced_api():
    """Test the reference-enhanced custom theme API with different scenarios"""
    
    base_url = 'http://127.0.0.1:8001/api/generate-custom-theme/'
    
    test_scenarios = [
        {
            'name': 'Modern Balloon Birthday',
            'data': {
                'description': 'modern colorful balloon birthday party',
                'event_type': 'birthday',
                'colors': ['blue', 'white'],
                'pax': 50
            }
        },
        {
            'name': 'Garden Wedding',
            'data': {
                'description': 'nature garden butterfly fairy wedding',
                'event_type': 'wedding', 
                'colors': ['green', 'white'],
                'pax': 100
            }
        },
        {
            'name': 'Elegant Traditional',
            'data': {
                'description': 'elegant traditional formal celebration',
                'event_type': 'wedding',
                'colors': ['gold', 'yellow'],
                'pax': 80
            }
        },
        {
            'name': 'Rustic Wedding',
            'data': {
                'description': 'rustic wooden country wedding', 
                'event_type': 'wedding',
                'colors': ['white', 'green'],
                'pax': 75
            }
        }
    ]
    
    print("🎨 Testing Reference-Enhanced Custom Theme Generation\n")
    
    for scenario in test_scenarios:
        print(f"📝 Testing: {scenario['name']}")
        print(f"   Description: {scenario['data']['description']}")
        print(f"   Event Type: {scenario['data']['event_type']}")
        print(f"   Colors: {scenario['data']['colors']}")
        print(f"   Guests: {scenario['data']['pax']}")
        
        try:
            response = requests.post(base_url, json=scenario['data'])
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ SUCCESS: Generated theme '{data['theme_name']}'")
                    print(f"   🖼️  Image URL: {data['theme_image']}")
                else:
                    print(f"   ❌ FAILED: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP ERROR: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ REQUEST ERROR: {e}")
        
        print("-" * 60)

if __name__ == '__main__':
    test_reference_enhanced_api()