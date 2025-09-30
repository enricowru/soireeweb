# Email Configuration Troubleshooting Guide

## Issue: Email OTP verification and forgot password not working in production (Render)

### Root Cause Analysis
The issue is likely related to how the Gmail app password is being handled in the production environment. Gmail app passwords are sensitive and need special handling.

### Solution Implemented

#### 1. Robust Password Cleaning in Settings
- Updated `settings.py` with a dedicated function to clean the email password
- Handles various quote formats and whitespace issues
- Added debug logging (only in development)

#### 2. Enhanced Error Handling
- Added specific SMTP error handling in all email sending functions
- Distinguishes between authentication errors and other SMTP issues
- Provides better debugging information

#### 3. Email Testing Tools
- Created `main/utils/email_debug.py` with comprehensive email testing functions
- Added Django management command `test_email` for production testing
- Added email password diagnosis functionality

### How to Test and Fix

#### Step 1: Test Locally First
```bash
python manage.py test_email --diagnose --to=your-email@example.com
```

#### Step 2: Check Environment Variables on Render
1. Go to your Render dashboard
2. Navigate to your web service
3. Go to Environment tab
4. Verify `EMAIL_HOST_PASSWORD` is set correctly
5. The password should be set WITHOUT quotes: `foxx uhhv hhbq ticf`
6. NOT with quotes: `"foxx uhhv hhbq ticf"`

#### Step 3: Test in Production
After deploying, run this command in Render's shell or via a temporary endpoint:
```bash
python manage.py test_email --diagnose --to=your-email@example.com
```

#### Step 4: Check Gmail Settings
1. Ensure 2-factor authentication is enabled on the Gmail account
2. Generate a new app password if needed:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate new password for "Mail"
3. Use the generated app password (without spaces) in Render environment

### Environment Variable Format on Render

Set these environment variables on Render:
```
EMAIL_HOST_USER=websoiree1@gmail.com
EMAIL_HOST_PASSWORD=foxx uhhv hhbq ticf
DEFAULT_FROM_EMAIL=websoiree1@gmail.com
```

**Important**: Do NOT wrap the password in quotes on Render!

### Debugging Commands

1. **Test email configuration:**
   ```bash
   python manage.py test_email --diagnose
   ```

2. **Send test email:**
   ```bash
   python manage.py test_email --to=test@example.com
   ```

3. **Check password format issues:**
   ```bash
   python manage.py shell
   >>> from main.utils.email_debug import diagnose_email_password
   >>> diagnose_email_password()
   ```

### Common Issues and Solutions

1. **Password wrapped in quotes**: Remove quotes from Render environment variable
2. **Spaces in app password**: Gmail app passwords have spaces - they should be kept
3. **Old app password**: Generate a new app password from Gmail
4. **2FA not enabled**: Enable 2-factor authentication on Gmail account
5. **Wrong Gmail account**: Ensure using the correct Gmail account

### Monitoring

After implementing these changes:
1. Monitor Django logs for specific SMTP error messages
2. Use the test command regularly to verify email functionality
3. Check Render logs for authentication errors

### Rollback Plan

If issues persist, the changes are minimal and can be easily reverted:
1. The original `settings.py` email configuration is preserved in the function
2. Error handling improvements are backward compatible
3. New files can be removed if not needed

### Additional Notes

- The email debugging tools are only active in development mode to avoid security issues
- All sensitive information is masked in logs
- The system gracefully handles email failures without breaking user registration