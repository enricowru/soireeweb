"""
Test SendGrid email sending with the new API key
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
        print("📧 Testing SendGrid email sending...")
        print(f"   Backend: {settings.EMAIL_BACKEND}")
        print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")
        print(f"   API Key: {settings.SENDGRID_API_KEY[:12]}...{settings.SENDGRID_API_KEY[-4:]}")
        
        result = send_mail(
            subject='🎉 SoireeWeb SendGrid Test - SUCCESS!',
            message='This is a test email from SoireeWeb using SendGrid Web API.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['shekaigarcia@gmail.com'],
            html_message='''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: #4CAF50; text-align: center;">🎉 SoireeWeb Email System is Working!</h2>
                <p style="font-size: 16px;">Congratulations! Your SendGrid email configuration is now fully functional.</p>
                
                <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">✅ What's Working Now:</h3>
                    <ul style="color: #555;">
                        <li><strong>Forgot password emails</strong> - Users can reset passwords</li>
                        <li><strong>Email verification</strong> - New registrations will be verified</li>
                        <li><strong>Localhost development</strong> - Works on your local machine</li>
                        <li><strong>Render production</strong> - Will work on deployed site</li>
                    </ul>
                </div>
                
                <p style="color: #666; font-style: italic; text-align: center;">
                    Test sent from SoireeWeb Django application<br>
                    From: websoiree1@gmail.com via SendGrid
                </p>
            </div>
            ''',
            fail_silently=False,
        )
        
        if result:
            print("🎉 SUCCESS! Email sent successfully!")
            print("📬 Check shekaigarcia@gmail.com inbox (and spam folder)")
            return True
        else:
            print("❌ Email sending returned 0")
            return False
            
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

if __name__ == "__main__":
    test_email_send()