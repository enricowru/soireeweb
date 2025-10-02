"""
Simple SendGrid API test to verify key validity
"""
import requests
import json
from decouple import config

def test_sendgrid_api_key():
    """Test if SendGrid API key is valid"""
    api_key = config('SENDGRID_API_KEY', default='')
    
    if not api_key:
        print("❌ No SendGrid API key found in environment")
        return False
    
    print(f"🔑 Testing API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test API key with SendGrid's API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test with a simple API call to get user profile
    response = requests.get(
        'https://api.sendgrid.com/v3/user/profile',
        headers=headers
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SendGrid API key is valid!")
        return True
    elif response.status_code == 401:
        print("❌ SendGrid API key is invalid or expired")
        return False
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
        return False

if __name__ == "__main__":
    test_sendgrid_api_key()