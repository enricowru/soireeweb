from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import json
from django.contrib.auth.decorators import login_required
from ..models import EmailVerificationOTP

@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    try:
        print(f"[SIGNUP] Request received: {request.method}")
        print(f"[SIGNUP] Request headers: {dict(request.headers)}")
        print(f"[SIGNUP] Request body: {request.body}")
        print(f"[SIGNUP] Content-Type: {request.content_type}")
        
        data = json.loads(request.body)
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        mobile = data.get('mobile')  # Add mobile field handling

        print(f"[SIGNUP] Data parsed - Username: {username}, Email: {email}, Mobile: {mobile}")

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            print(f"[SIGNUP] Username {username} already exists")
            return JsonResponse({'message': 'Username already exists'}, status=400)

        if User.objects.filter(email=email).exists():
            print(f"[SIGNUP] Email {email} already exists")
            return JsonResponse({'message': 'Email already exists'}, status=400)

        print(f"[SIGNUP] Creating user...")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname,
            is_verified=False  # User starts as unverified
        )
        
        # Set mobile field separately since create_user doesn't handle custom fields
        if mobile:
            user.mobile = mobile
            user.save()
        
        print(f"[SIGNUP] User created successfully: {user.id}")
        
        # Invalidate any existing email verification OTPs for this email
        EmailVerificationOTP.objects.filter(email=email, is_used=False).update(is_used=True)
        
        # Create new email verification OTP
        verification_otp = EmailVerificationOTP.objects.create(email=email)
        
        # Send verification email
        try:
            subject = 'SoireeWeb - Email Verification Required'
            message = f"""
Hi {firstname or 'User'},

Welcome to SoireeWeb! To complete your registration, please verify your email address.

Your verification code is: {verification_otp.otp_code}

This code will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
SoireeWeb Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            print(f"[SIGNUP] Verification email sent to {email}")
            
        except Exception as e:
            print(f"[SIGNUP] Email sending failed: {e}")
            # Don't fail the registration if email fails
            
        return JsonResponse({
            'message': 'Registration successful! Please check your email for verification code.',
            'needs_verification': True
        }, status=201)
    except json.JSONDecodeError as e:
        print(f"[SIGNUP ERROR] JSON Decode Error: {str(e)}")
        return JsonResponse({'message': 'Invalid JSON format', 'error': str(e)}, status=400)
    except Exception as e:
        print(f"[SIGNUP ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'message': 'Server error', 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return JsonResponse({'error': 'Auth required'}, status=401)
    try:
        body = json.loads(request.body or '{}')
    except Exception:
        body = {}
    first_name = body.get('first_name')
    last_name = body.get('last_name')
    email = body.get('email')
    phone = body.get('phone') or body.get('phone_number')
    password = body.get('password')
    dirty = False
    if isinstance(first_name, str):
        user.first_name = first_name.strip()
        dirty = True
    if isinstance(last_name, str):
        user.last_name = last_name.strip()
        dirty = True
    if isinstance(email, str):
        user.email = email.strip()
        dirty = True
    # Attempt to store phone if user model has field
    if phone is not None and hasattr(user, 'phone'):
        try:
            setattr(user, 'phone', str(phone).strip())
            dirty = True
        except Exception:
            pass
    if password:
        user.set_password(password)
        dirty = True
    if dirty:
        user.save()
    return JsonResponse({'updated': dirty})


@csrf_exempt
@require_http_methods(["POST"])
def email_verification_request(request):
    """Send or resend email verification OTP"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'})
        
        # Check if user with this email exists
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return JsonResponse({'success': True, 'message': 'If this email exists and is unverified, a verification code has been sent.'})
        
        # Check if already verified
        if user.is_verified:
            return JsonResponse({'success': False, 'message': 'This email is already verified.'})
        
        # Invalidate any existing email verification OTPs for this email
        EmailVerificationOTP.objects.filter(email=email, is_used=False).update(is_used=True)
        
        # Create new email verification OTP
        verification_otp = EmailVerificationOTP.objects.create(email=email)
        
        # Send verification email
        try:
            subject = 'SoireeWeb - Email Verification Code'
            message = f"""
Hi {user.first_name or 'User'},

You have requested email verification for your SoireeWeb account.

Your verification code is: {verification_otp.otp_code}

This code will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
SoireeWeb Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return JsonResponse({'success': True, 'message': 'Verification code has been sent to your email.'})
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again.'})
    
    except Exception as e:
        print(f"Error in email_verification_request: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})


@csrf_exempt
@require_http_methods(["POST"])
def email_verification_verify(request):
    """Verify email with OTP code"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        otp_code = data.get('otp', '').strip()
        
        if not email or not otp_code:
            return JsonResponse({'success': False, 'message': 'Email and OTP code are required.'})
        
        # Check if user with this email exists
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid email or OTP code.'})
        
        # Check if already verified
        if user.is_verified:
            return JsonResponse({'success': False, 'message': 'This email is already verified.'})
        
        # Verify OTP
        try:
            verification_otp = EmailVerificationOTP.objects.get(
                email=email,
                otp_code=otp_code,
                is_used=False
            )
            
            if not verification_otp.is_valid():
                return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})
            
            # Mark OTP as used
            verification_otp.is_used = True
            verification_otp.save()
            
            # Mark user as verified
            user.is_verified = True
            user.save()
            
            # Invalidate any other unused OTPs for this email
            EmailVerificationOTP.objects.filter(email=email, is_used=False).update(is_used=True)
            
            return JsonResponse({'success': True, 'message': 'Email verified successfully! You can now login.'})
            
        except EmailVerificationOTP.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or expired OTP code.'})
    
    except Exception as e:
        print(f"Error in email_verification_verify: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})
