#!/usr/bin/env python
import requests
import json

def test_custom_theme_api():
    url = 'http://127.0.0.1:8001/api/generate-custom-theme/'
    data = {
        'description': 'TEST_MODE',
        'event_type': 'birthday',
        'colors': ['red'],
        'pax': 50
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Request data: {data}")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            json_response = response.json()
            print(f"JSON Response: {json_response}")
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    test_custom_theme_api()