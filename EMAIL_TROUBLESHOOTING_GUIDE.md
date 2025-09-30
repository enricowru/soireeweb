# EMAIL TROUBLESHOOTING GUIDE

## ⚠️ CRITICAL SECURITY ISSUE
**Your SendGrid API key was exposed in documentation and needs immediate action:**

### 1. REVOKE EXPOSED API KEY IMMEDIATELY
1. Go to SendGrid Dashboard → Settings → API Keys
2. Find the exposed key and DELETE it immediately
3. Create a new API key with same permissions

### 2. REGENERATE NEW API KEY
1. In SendGrid dashboard, create new API Key
2. Name it "SoireeWeb Production Key"
3. Set permissions to "Restricted Access"
4. Under "Mail Send", select "Full Access"
5. Copy the new key (you'll only see it once!)

### 3. UPDATE RENDER ENVIRONMENT VARIABLES
In your Render dashboard, update the environment variable:
```
SENDGRID_API_KEY=new_api_key_here
```

## 🔧 EMAIL CONFIGURATION ISSUES

### Current Issues Identified:
1. **Security**: API key was exposed in documentation 
2. **Configuration**: Email debugging was pointing to Gmail instead of SendGrid
3. **Environment**: Need to verify environment variables are set correctly in Render

### Verification Steps:

#### Step 1: Check SendGrid API Key Status
```bash
# Test if API key is valid
curl -X "GET" "https://api.sendgrid.com/v3/user/profile" \
  -H "Authorization: Bearer YOUR_NEW_API_KEY"
```

#### Step 2: Verify Sender Authentication
1. In SendGrid Dashboard → Settings → Sender Authentication
2. Ensure `websoiree1@gmail.com` is verified
3. If not verified, verify it again with the new setup

#### Step 3: Test Email Sending
Create a test endpoint to verify email functionality:

```python
# Add to views/auth.py for testing only
@csrf_exempt
def test_email(request):
    """Test email sending - REMOVE IN PRODUCTION"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        send_mail(
            'Test Email from SoireeWeb',
            'This is a test email to verify SendGrid configuration.',
            settings.DEFAULT_FROM_EMAIL,
            ['your-test-email@example.com'],  # Replace with your email
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'Test email sent successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Email failed: {str(e)}'})
```

### Environment Variables Required in Render:
```
SENDGRID_API_KEY=your_new_sendgrid_api_key
DEFAULT_FROM_EMAIL=websoiree1@gmail.com
DJANGO_ENV=prod
```

### Common SendGrid Errors and Solutions:

1. **"Unauthorized" (401)**
   - API key is invalid or expired
   - Solution: Generate new API key

2. **"Forbidden" (403)**
   - API key doesn't have Mail Send permissions
   - Solution: Check API key permissions in SendGrid

3. **"Bad Request" (400)**
   - From email not verified in SendGrid
   - Solution: Verify sender authentication

4. **Connection Timeout**
   - Network/firewall issues (less likely with Render)
   - Solution: Check if Render allows outbound SMTP connections

### Testing Checklist:
- [ ] New API key generated and old one revoked
- [ ] New API key added to Render environment variables
- [ ] Sender email verified in SendGrid
- [ ] Application redeployed to Render
- [ ] Test forgot password functionality
- [ ] Test email verification functionality

### If Still Not Working:
1. Check Render logs for specific error messages
2. Verify SendGrid activity dashboard for failed sends
3. Consider switching to SendGrid Web API instead of SMTP (more reliable)

## Alternative: Switch to SendGrid Web API
If SMTP continues to fail, switch to Web API:

```python
# In settings.py, replace SMTP config with:
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')

# Install: pip install django-sendgrid-v5
```

This bypasses SMTP entirely and uses HTTP API calls, which are more reliable on cloud platforms.