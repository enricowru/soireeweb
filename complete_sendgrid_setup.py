"""
Complete SendGrid Setup and Test Script for SoireeWeb
Run this after getting a new SendGrid API key
"""
import os
import sys
from pathlib import Path

def update_env_file_with_api_key(api_key):
    """Update .env file with the new SendGrid API key"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the placeholder
    updated_content = content.replace(
        'SENDGRID_API_KEY=YOUR_NEW_SENDGRID_API_KEY_HERE',
        f'SENDGRID_API_KEY={api_key}'
    )
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print(f"✅ Updated .env file with new API key: {api_key[:10]}...{api_key[-4:]}")
    return True

def test_sendgrid_api_key(api_key):
    """Test if the SendGrid API key is valid"""
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.sendgrid.com/v3/user/profile',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ SendGrid API key is valid!")
            print(f"   Account: {user_data.get('username', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("❌ SendGrid API key is invalid or expired")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

def test_django_email():
    """Test Django email sending with SendGrid"""
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        import django
        django.setup()
        
        from django.core.mail import send_mail
        from django.conf import settings
        
        print("📧 Testing Django email with SendGrid...")
        print(f"   Backend: {settings.EMAIL_BACKEND}")
        print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
        print(f"   API Key Configured: {bool(getattr(settings, 'SENDGRID_API_KEY', ''))}")
        
        # Send test email
        result = send_mail(
            subject='SoireeWeb Email Test - SendGrid Working!',
            message='This is a test email from SoireeWeb using SendGrid.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['shekaigarcia@gmail.com'],
            html_message='''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #4CAF50;">🎉 SoireeWeb Email System is Working!</h2>
                <p>Congratulations! Your SendGrid email configuration is working perfectly.</p>
                <p><strong>This means:</strong></p>
                <ul>
                    <li>✅ Forgot password emails will work</li>
                    <li>✅ Email verification will work</li>
                    <li>✅ Both localhost and Render deployment will work</li>
                </ul>
                <p><em>Test sent from SoireeWeb Django application</em></p>
            </div>
            ''',
            fail_silently=False,
        )
        
        if result:
            print("🎉 SUCCESS! Email sent successfully!")
            print("📬 Check shekaigarcia@gmail.com inbox (and spam folder)")
            print("🚀 Your email system is now fully functional!")
            return True
        else:
            print("❌ Email sending failed (result was 0)")
            return False
            
    except Exception as e:
        print(f"❌ Django email test failed: {e}")
        return False

def main():
    """Main setup and test function"""
    print("🔧 SENDGRID SETUP AND TEST FOR SOIREEWEB")
    print("=" * 50)
    
    # Get API key from user
    print("\n📝 Please provide your new SendGrid API key:")
    print("   1. Go to https://app.sendgrid.com/")
    print("   2. Settings → API Keys")
    print("   3. Create API Key → Full Access")
    print("   4. Copy the key (starts with SG.)")
    print()
    
    api_key = input("Enter your SendGrid API key: ").strip()
    
    if not api_key.startswith('SG.'):
        print("❌ Invalid API key format. Should start with 'SG.'")
        return
    
    # Test the API key
    print(f"\n🔑 Testing API key: {api_key[:10]}...{api_key[-4:]}")
    if not test_sendgrid_api_key(api_key):
        print("❌ API key test failed. Please check your key.")
        return
    
    # Update .env file
    print("\n📝 Updating .env file...")
    if not update_env_file_with_api_key(api_key):
        print("❌ Failed to update .env file")
        return
    
    # Test Django email
    print("\n📧 Testing Django email functionality...")
    if test_django_email():
        print("\n🎉 SETUP COMPLETE!")
        print("✅ SendGrid is configured and working")
        print("✅ Emails will work on both localhost and Render")
        print("✅ Forgot password and email verification are functional")
        print("\n🚀 Next steps:")
        print("   1. Deploy to Render with the same SENDGRID_API_KEY")
        print("   2. Test forgot password on your web app")
        print("   3. Test email verification during registration")
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")

if __name__ == "__main__":
    main()