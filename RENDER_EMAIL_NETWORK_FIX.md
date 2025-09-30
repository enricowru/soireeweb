# Render Email Fix Guide - Network Unreachable Error

## Problem
The error `[Errno 101] Network is unreachable` in Render logs indicates that your Django app cannot connect to Gmail's SMTP servers. This is a network connectivity issue, not necessarily a password formatting problem.

## Root Cause Analysis
The issue is likely one of these:
1. **Render firewall/network restrictions** blocking SMTP connections
2. **SMTP port blocking** - Port 587 (TLS) might be blocked
3. **DNS resolution issues** with Gmail SMTP servers
4. **App password formatting** with quotes or spaces

## Solutions (Try in Order)

### 1. Switch to SSL (Port 465) Instead of TLS (Port 587)
The updated settings in `config/settings.py` now automatically use SSL for production:

```python
# For production (Render)
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 60
```

### 2. Fix Gmail App Password in Render Environment Variables

**IMPORTANT**: Gmail app passwords have spaces by design (`abcd efgh ijkl mnop`), and Render auto-quotes environment variables with spaces.

1. **Go to Render Dashboard** → Your Service → Environment Tab

2. **Set EMAIL_HOST_PASSWORD** with the EXACT Gmail app password (with spaces):
   
   ✅ **Correct way to set in Render**:
   ```
   abcd efgh ijkl mnop
   ```
   (Paste exactly as Gmail provides it, with spaces)
   
   ❌ **Don't do this**:
   ```
   "abcd efgh ijkl mnop"  (don't add your own quotes)
   abcdefghijklmnop       (don't remove spaces manually)
   ```

3. **What happens**:
   - You enter: `abcd efgh ijkl mnop`
   - Render automatically stores as: `"abcd efgh ijkl mnop"` (quotes added by Render)
   - Django cleans it to: `abcd efgh ijkl mnop` (removes ONLY the quotes, keeps spaces)
   - **Key insight**: Gmail SMTP accepts passwords with spaces! The issue is only the quotes.

4. **Redeploy** your service after updating the environment variable

### 3. Generate a Fresh Gmail App Password

If the current password is corrupted:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled
3. Go to "App passwords" section
4. **Delete the old app password** for your email service
5. **Generate a new 16-character app password**
6. **Copy it exactly** (no spaces, no formatting)
7. **Update Render environment variable** with the new password
8. **Redeploy**

### 4. Test in Production

Use the new debug endpoints (admin only):

1. **Network Test**: `https://your-app.onrender.com/admin/debug/email/network/`
2. **Email Diagnosis**: `https://your-app.onrender.com/admin/debug/email/diagnosis/`  
3. **Send Test Email**: `https://your-app.onrender.com/admin/debug/email/test/`

### 5. Use Management Command (Alternative)

If you have access to Render shell:

```bash
python manage.py diagnose_email
python manage.py diagnose_email --test-send your-email@gmail.com
```

## Environment Variables Checklist

Make sure these are set correctly in Render:

```
EMAIL_HOST_USER=websoiree1@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=websoiree1@gmail.com
```

**Critical Understanding**: 
- ✅ Gmail SMTP accepts passwords WITH spaces (works in localhost)
- ✅ Problem is Render auto-quotes them: `"abcd efgh ijkl mnop"`
- ✅ Gmail rejects quoted passwords 
- ✅ Django removes ONLY the quotes, keeps the spaces
- ✅ Result: `abcd efgh ijkl mnop` (works with Gmail SMTP)

## Alternative SMTP Providers

If Gmail continues to have issues on Render, consider:

1. **SendGrid** (Render recommended)
2. **Mailjet**
3. **Amazon SES**
4. **PostMark**

## Testing Steps

1. **Deploy the updated code** with SSL configuration
2. **Update environment variables** in Render (no quotes!)
3. **Generate fresh Gmail app password** if needed
4. **Redeploy** the service
5. **Test with debug endpoints** or management command
6. **Try forgot password/email verification** features

## Expected Results

After fixing:
- ✅ Network connectivity test passes
- ✅ SMTP connection successful on port 465
- ✅ Email sending works in production
- ✅ OTP emails delivered for verification/forgot password

## Troubleshooting

If still not working:

1. **Check Render logs** for new error messages
2. **Try alternative SMTP provider** (SendGrid)
3. **Contact Render support** about SMTP restrictions
4. **Use debug endpoints** to get detailed diagnostic info

## Files Modified

- `config/settings.py` - Updated email configuration for Render
- `main/utils/email_debug.py` - Enhanced debugging utilities
- `main/management/commands/diagnose_email.py` - Management command
- `main/views/email_debug_views.py` - Production debug endpoints
- `main/admin_urls.py` - Debug endpoint routes