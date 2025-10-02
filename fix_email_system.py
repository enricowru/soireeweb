"""
Complete email system fix for SoireeWeb
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def test_gmail_smtp_direct():
    """Test Gmail SMTP directly with app password"""
    try:
        print("=== TESTING GMAIL SMTP DIRECTLY ===")
        
        # Gmail SMTP settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_user = "websoiree1@gmail.com"
        email_password = "foxx uhhv hhbq ticf"  # App password
        
        print(f"Email: {email_user}")
        print(f"Password: {'*' * len(email_password)}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = "shekaigarcia@gmail.com"
        msg['Subject'] = "SoireeWeb Email Test - Direct SMTP"
        
        body = """
        <html>
        <body>
        <h2>SoireeWeb Email Test</h2>
        <p>This is a direct SMTP test email from SoireeWeb.</p>
        <p>If you receive this, the email system is working!</p>
        <p><strong>Test Type:</strong> Direct Gmail SMTP</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        
        text = msg.as_string()
        server.sendmail(email_user, "shekaigarcia@gmail.com", text)
        server.quit()
        
        print("✅ Email sent successfully via Gmail SMTP!")
        return True
        
    except Exception as e:
        print(f"❌ Gmail SMTP failed: {e}")
        return False

def update_django_settings_for_gmail():
    """Update Django settings to use Gmail SMTP instead of SendGrid"""
    settings_file = "config/settings.py"
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Replace SendGrid configuration with Gmail SMTP
    gmail_config = '''
# Email Configuration - Gmail SMTP (Working Solution)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='websoiree1@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='foxx uhhv hhbq ticf')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='websoiree1@gmail.com')

# SendGrid backup (if needed later)
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')
'''
    
    # Find and replace the email configuration section
    lines = content.split('\n')
    new_lines = []
    skip_section = False
    
    for line in lines:
        if 'Email Configuration' in line and 'SendGrid' in line:
            skip_section = True
            new_lines.append(gmail_config)
            continue
        elif skip_section and line.strip().startswith('#') and 'Email validation' in line:
            skip_section = False
            new_lines.append(line)
        elif not skip_section:
            new_lines.append(line)
    
    # Write updated settings
    with open(settings_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Updated Django settings to use Gmail SMTP")

if __name__ == "__main__":
    print("🔧 FIXING SOIREEWEB EMAIL SYSTEM")
    print("=" * 50)
    
    # Test 1: Direct Gmail SMTP
    if test_gmail_smtp_direct():
        print("\n✅ Gmail SMTP is working!")
        print("📝 Updating Django settings to use Gmail...")
        update_django_settings_for_gmail()
        print("\n🎉 Email system fixed!")
        print("\nNext steps:")
        print("1. Restart Django server")
        print("2. Test forgot password functionality")
        print("3. Test email verification")
    else:
        print("\n❌ Gmail SMTP failed. Check credentials.")