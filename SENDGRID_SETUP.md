# SendGrid Setup for SoireeWeb Email

## Issue
Render blocks direct SMTP connections to Gmail, causing "Network is unreachable" errors.

## Solution: SendGrid
SendGrid is an email delivery service that works perfectly with Render and other hosting platforms.

## Setup Steps

### 1. Create SendGrid Account
1. Go to https://sendgrid.com
2. Sign up for free account (100 emails/day free)
3. Verify your email address

### 2. Create API Key
1. In SendGrid dashboard, go to Settings > API Keys
2. Click "Create API Key"
3. Choose "Restricted Access"
4. Give it a name like "SoireeWeb Render"
5. Under "Mail Send", select "Full Access"
6. Click "Create & View"
7. **COPY THE API KEY** (you can only see it once!)

### 3. Verify Sender Identity
1. Go to Settings > Sender Authentication
2. Click "Verify a Single Sender"
3. Use: `websoiree1@gmail.com`
4. Fill in the form and verify

### 4. Add to Render Environment Variables
In your Render dashboard, add these environment variables:

```
SENDGRID_API_KEY=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
DEFAULT_FROM_EMAIL=websoiree1@gmail.com
EMAIL_HOST_USER=websoiree1@gmail.com
```

### 5. Deploy
Deploy your updated code to Render with the new SendGrid configuration.

## Testing
Once deployed, test the forgot password functionality. It should now work!

## Why This Works
- SendGrid uses API-based email delivery instead of SMTP
- Render allows HTTP/HTTPS connections to SendGrid's API
- No firewall/network restrictions like with direct Gmail SMTP

## Cost
- Free tier: 100 emails/day (perfect for testing and small apps)
- Paid plans start at $15/month for 40K emails if you need more

## Current Configuration
The code is now set to:
- **Production (Render)**: Use SendGrid
- **Development (Local)**: Use SendGrid

SendGrid is now used everywhere - no more SMTP configuration needed! This ensures consistent email delivery across all environments.