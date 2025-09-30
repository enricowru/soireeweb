# Alternative Email Services for Render Deployment

If Gmail SMTP continues to fail with "Network is unreachable" on Render, here are proven alternatives:

## Option 1: SendGrid (Recommended for Render)
SendGrid works very well with Render and other hosting platforms.

### Setup:
1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Get your API key from SendGrid dashboard
3. Add to Render environment variables:
   - `SENDGRID_API_KEY=your_api_key_here`
   - `DEFAULT_FROM_EMAIL=your_verified_sender@domain.com`

### Django Settings:
```python
# Add to settings.py
if ENVIRONMENT == 'prod':
    # Use SendGrid for production
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')
else:
    # Keep Gmail for development
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = 'rjyu jzts iegc vzvc'
```

### Install SendGrid:
```bash
pip install sendgrid-django
```

## Option 2: Mailgun
Another reliable service that works well with hosting platforms.

### Setup:
1. Sign up at https://www.mailgun.com (free tier: 5,000 emails/month)
2. Get your API credentials
3. Add to Render environment variables

### Django Settings:
```python
if ENVIRONMENT == 'prod':
    EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
    MAILGUN_API_KEY = config('MAILGUN_API_KEY', default='')
    MAILGUN_DOMAIN_NAME = config('MAILGUN_DOMAIN_NAME', default='')
```

## Option 3: SMTP2GO
Simple SMTP service with good Render compatibility.

### Django Settings:
```python
if ENVIRONMENT == 'prod':
    EMAIL_HOST = 'mail.smtp2go.com'
    EMAIL_PORT = 587  # or 2525, 25, 465
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = config('SMTP2GO_USERNAME', default='')
    EMAIL_HOST_PASSWORD = config('SMTP2GO_PASSWORD', default='')
```

## Current Issue Analysis:
The "Network is unreachable" error suggests Render's network infrastructure is blocking or restricting connections to Gmail's SMTP servers. This is common with shared hosting platforms that implement strict firewall rules.

## Quick Test:
Try the SSL configuration I just implemented first (port 465), as this often resolves the issue without needing a different email service.