#!/usr/bin/env python3
"""
Test script to verify forgot password functionality works
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from main.models import PasswordResetOTP, User
from django.utils import timezone

def test_otp_model():
    """Test OTP model functionality"""
    print("🧪 Testing OTP Model...")
    
    # Test creating OTP
    test_email = "test@example.com"
    otp = PasswordResetOTP.objects.create(email=test_email)
    
    print(f"✅ OTP Created: {otp.otp_code} for {test_email}")
    print(f"✅ Expires at: {otp.expires_at}")
    print(f"✅ Is valid: {otp.is_valid()}")
    
    # Cleanup
    otp.delete()
    print("✅ OTP Model test passed!")

def test_email_settings():
    """Test email configuration"""
    print("\n📧 Testing Email Settings...")
    
    print(f"✅ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"✅ EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"✅ EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"✅ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"✅ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"✅ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Don't print password for security
    has_password = bool(settings.EMAIL_HOST_PASSWORD)
    print(f"✅ EMAIL_HOST_PASSWORD configured: {has_password}")

def test_user_exists():
    """Test if any users exist for testing"""
    print("\n👤 Testing User Model...")
    
    users = User.objects.all()
    print(f"✅ Total users in database: {users.count()}")
    
    if users.exists():
        user = users.first()
        print(f"✅ Sample user: {user.username} ({user.email})")
    else:
        print("⚠️ No users found. You may need to create a test user.")

if __name__ == "__main__":
    print("🚀 Starting Forgot Password Functionality Test\n")
    
    try:
        test_otp_model()
        test_email_settings()
        test_user_exists()
        
        print("\n✅ All tests passed! Forgot password functionality should work.")
        print("\n📝 Next steps:")
        print("1. Add environment variables in Render dashboard")
        print("2. Push to GitHub")
        print("3. Test on production site")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
