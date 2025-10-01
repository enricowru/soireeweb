"""
SendGrid debugging utility to check email delivery status
"""
import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings
import json
import time

def test_sendgrid_delivery(to_email, subject="Test Email", content="This is a test email."):
    """
    Test SendGrid email delivery with detailed logging
    """
    try:
        print("=== SENDGRID DELIVERY TEST ===")
        
        # Initialize SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        
        # Create email
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">SoireeWeb Email Test</h2>
                <p>{content}</p>
                <p><strong>Timestamp:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><em>This is a test email from SoireeWeb to verify email delivery.</em></p>
            </div>
            """
        )
        
        print(f"From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"API Key: {settings.SENDGRID_API_KEY[:10]}...{settings.SENDGRID_API_KEY[-4:]}")
        
        # Send email
        response = sg.send(message)
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        
        if response.status_code == 202:
            print("✅ Email sent successfully to SendGrid!")
            return {
                'success': True,
                'status_code': response.status_code,
                'message': f'Email sent successfully to {to_email}',
                'response_body': response.body.decode('utf-8') if response.body else '',
                'headers': dict(response.headers)
            }
        else:
            print(f"❌ SendGrid returned status code: {response.status_code}")
            return {
                'success': False,
                'status_code': response.status_code,
                'message': f'SendGrid returned status {response.status_code}',
                'response_body': response.body.decode('utf-8') if response.body else '',
                'headers': dict(response.headers)
            }
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

def check_sender_authentication():
    """
    Check if sender email domain is authenticated in SendGrid
    """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        
        # Get sender authentication status
        response = sg.whitelabel.domains.get()
        print("=== SENDER AUTHENTICATION STATUS ===")
        print(f"Response: {response.status_code}")
        print(f"Body: {response.body}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error checking sender authentication: {e}")
        return False

def get_email_activity(email_address, limit=10):
    """
    Get recent email activity for debugging
    """
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        
        # Get email activity (requires Pro plan or higher)
        query_params = {
            'query': f'to_email="{email_address}"',
            'limit': limit
        }
        
        response = sg.activity.get(query_params=query_params)
        print("=== EMAIL ACTIVITY ===")
        print(f"Response: {response.status_code}")
        print(f"Body: {response.body}")
        
        return response.status_code == 200, response.body
        
    except Exception as e:
        print(f"Error getting email activity: {e}")
        return False, str(e)