"""
Email debugging utility for SoireeWeb
"""
import os
import socket
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


def test_network_connectivity():
    """
    Test network connectivity to Gmail SMTP servers
    """
    print("=== NETWORK CONNECTIVITY TEST ===")
    
    # Test DNS resolution
    try:
        print("Testing DNS resolution for smtp.gmail.com...")
        addresses = socket.getaddrinfo('smtp.gmail.com', 587)
        print(f"✓ DNS resolution successful. Found {len(addresses)} addresses:")
        for addr in addresses[:3]:  # Show first 3
            print(f"  - {addr[4][0]}:{addr[4][1]}")
    except Exception as e:
        print(f"✗ DNS resolution failed: {e}")
        return False
    
    # Test raw socket connection
    try:
        print("\nTesting raw socket connection to smtp.gmail.com:587...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 587))
        sock.close()
        
        if result == 0:
            print("✓ Raw socket connection successful")
        else:
            print(f"✗ Raw socket connection failed with error code: {result}")
            return False
    except Exception as e:
        print(f"✗ Raw socket connection failed: {e}")
        return False
    
    # Test alternative SMTP servers
    alternative_servers = [
        ('smtp.gmail.com', 465),  # SSL
        ('smtp.gmail.com', 25),   # Standard SMTP (might be blocked)
    ]
    
    print("\nTesting alternative SMTP ports...")
    for server, port in alternative_servers:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server, port))
            sock.close()
            
            if result == 0:
                print(f"✓ Connection to {server}:{port} successful")
            else:
                print(f"✗ Connection to {server}:{port} failed (error code: {result})")
        except Exception as e:
            print(f"✗ Connection to {server}:{port} failed: {e}")
    
    return True


def test_smtp_with_different_configs():
    """
    Test SMTP with different configuration settings for Render compatibility
    """
    print("=== TESTING DIFFERENT SMTP CONFIGURATIONS ===")
    
    # Get credentials
    email_user = config('EMAIL_HOST_USER', default='')
    email_password = config('EMAIL_HOST_PASSWORD', default='').strip().strip('"').strip("'")
    
    configurations = [
        {
            'name': 'Standard TLS (587)',
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'timeout': 30
        },
        {
            'name': 'SSL (465)',
            'host': 'smtp.gmail.com',
            'port': 465,
            'use_tls': False,
            'use_ssl': True,
            'timeout': 30
        },
        {
            'name': 'TLS with longer timeout',
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False,
            'timeout': 60
        }
    ]
    
    for config_test in configurations:
        try:
            print(f"\nTesting {config_test['name']}...")
            
            if config_test['use_ssl']:
                server = smtplib.SMTP_SSL(config_test['host'], config_test['port'], timeout=config_test['timeout'])
            else:
                server = smtplib.SMTP(config_test['host'], config_test['port'], timeout=config_test['timeout'])
                if config_test['use_tls']:
                    server.starttls()
            
            server.login(email_user, email_password)
            print(f"✓ {config_test['name']} connection successful!")
            server.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ {config_test['name']} authentication failed: {e}")
        except smtplib.SMTPException as e:
            print(f"✗ {config_test['name']} SMTP error: {e}")
        except socket.timeout as e:
            print(f"✗ {config_test['name']} timeout error: {e}")
        except Exception as e:
            print(f"✗ {config_test['name']} failed: {e}")


def comprehensive_email_diagnosis():
    """
    Run all diagnostic tests
    """
    print("=== COMPREHENSIVE EMAIL DIAGNOSIS ===")
    print("Running on Render environment...\n")
    
    # Test network connectivity first
    if not test_network_connectivity():
        print("\n❌ Network connectivity test failed. This is likely the root cause.")
        print("Recommendations:")
        print("1. Check if Render has firewall restrictions")
        print("2. Try using port 465 with SSL instead of 587 with TLS")
        print("3. Contact Render support about SMTP connectivity")
        return False
    
    # Test password configuration
    print("\n" + "="*50)
    diagnose_email_password()
    
    # Test different SMTP configurations
    print("\n" + "="*50)
    test_smtp_with_different_configs()
    
    # Test email configuration
    print("\n" + "="*50)
    return test_email_configuration()


def get_render_optimized_email_settings():
    """
    Get email settings optimized for Render environment
    """
    return {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': 465,  # Use SSL port instead of TLS
        'EMAIL_USE_TLS': False,
        'EMAIL_USE_SSL': True,  # Use SSL instead of TLS
        'EMAIL_TIMEOUT': 60,  # Longer timeout for Render
        'EMAIL_HOST_USER': config('EMAIL_HOST_USER', default=''),
        'EMAIL_HOST_PASSWORD': config('EMAIL_HOST_PASSWORD', default='').strip().strip('"').strip("'"),
    }