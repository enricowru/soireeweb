"""
Simple email test without Unicode characters
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_send():
    """Test sending email with SendGrid"""
    try:
        print("Testing SendGrid email sending...")
        print(f"   Backend: {settings.EMAIL_BACKEND}")
        print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
        print(f"   API Key: {settings.SENDGRID_API_KEY[:12]}...{settings.SENDGRID_API_KEY[-4:]}")
        
        result = send_mail(
            subject='SoireeWeb SendGrid Test - SUCCESS!',
            message='This is a test email from SoireeWeb using SendGrid Web API.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['shekaigarcia@gmail.com'],
            fail_silently=False,
        )
        
        if result:
            print("SUCCESS! Email sent successfully!")
            print("Check shekaigarcia@gmail.com inbox (and spam folder)")
            return True
        else:
            print("Email sending returned 0")
            return False
            
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

if __name__ == "__main__":
    test_email_send()
