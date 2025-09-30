"""
Email debugging utility for SoireeWeb
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend


def test_email_configuration():
    """
    Test email configuration and return detailed status
    """
    try:
        print("=== EMAIL CONFIGURATION TEST ===")
        
        # Get email settings
        email_user = config('EMAIL_HOST_USER', default='')
        email_password = config('EMAIL_HOST_PASSWORD', default='')
        
        print(f"EMAIL_HOST_USER: {email_user}")
        print(f"EMAIL_HOST_PASSWORD: {'*' * len(email_password) if email_password else 'NOT SET'}")
        print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
        print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
        print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
        print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
        
        # Clean the password
        clean_password = email_password.strip().strip('"').strip("'")
        print(f"Cleaned password length: {len(clean_password)}")
        
        # Test SMTP connection manually
        print("\n=== TESTING SMTP CONNECTION ===")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, clean_password)
        print("✓ SMTP connection successful!")
        server.quit()
        
        # Test Django send_mail
        print("\n=== TESTING DJANGO SEND_MAIL ===")
        result = send_mail(
            'Test Email from SoireeWeb',
            'This is a test email to verify email configuration.',
            settings.DEFAULT_FROM_EMAIL,
            [email_user],  # Send to self
            fail_silently=False,
        )
        print(f"✓ Django send_mail result: {result}")
        
        return True, "Email configuration test passed!"
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication failed: {e}"
        print(f"✗ {error_msg}")
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {e}"
        print(f"✗ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"✗ {error_msg}")
        return False, error_msg


def send_test_email(to_email):
    """
    Send a test email with comprehensive error handling
    """
    try:
        print(f"=== SENDING TEST EMAIL TO {to_email} ===")
        
        subject = "SoireeWeb Email Test"
        message = """
This is a test email from SoireeWeb.

If you receive this email, the email configuration is working correctly.

Best regards,
SoireeWeb Team
        """
        
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        
        print(f"✓ Test email sent successfully! Result: {result}")
        return True, "Test email sent successfully!"
        
    except Exception as e:
        error_msg = f"Failed to send test email: {e}"
        print(f"✗ {error_msg}")
        return False, error_msg


def diagnose_email_password():
    """
    Diagnose email password configuration issues
    """
    print("=== EMAIL PASSWORD DIAGNOSIS ===")
    
    # Get raw password from environment
    raw_password = os.environ.get('EMAIL_HOST_PASSWORD', '')
    config_password = config('EMAIL_HOST_PASSWORD', default='')
    
    print(f"Raw environment variable: '{raw_password}'")
    print(f"Config password: '{config_password}'")
    print(f"Raw password length: {len(raw_password)}")
    print(f"Config password length: {len(config_password)}")
    
    # Check for common issues
    issues = []
    
    if not raw_password:
        issues.append("EMAIL_HOST_PASSWORD environment variable is not set")
    
    if raw_password.startswith('"') and raw_password.endswith('"'):
        issues.append("Password is wrapped in double quotes")
    
    if raw_password.startswith("'") and raw_password.endswith("'"):
        issues.append("Password is wrapped in single quotes")
    
    if ' ' in raw_password:
        issues.append("Password contains spaces")
    
    # Test different cleaning methods
    test_passwords = [
        raw_password,
        raw_password.strip(),
        raw_password.strip('"').strip("'"),
        raw_password.strip().strip('"').strip("'"),
        raw_password.replace('"', '').replace("'", ''),
    ]
    
    print("\n=== TESTING DIFFERENT PASSWORD CLEANING METHODS ===")
    for i, pwd in enumerate(test_passwords, 1):
        print(f"Method {i}: '{pwd}' (length: {len(pwd)})")
    
    if issues:
        print(f"\n⚠️  Potential issues found: {', '.join(issues)}")
    else:
        print("\n✓ No obvious password formatting issues detected")
    
    return issues