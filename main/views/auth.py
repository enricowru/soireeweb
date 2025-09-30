from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import smtplib
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
import json
from ..models import Review, PasswordResetOTP, User

Users = get_user_model()

def home(request):
    # If user is authenticated and is admin, redirect to dashboard
    if request.user.is_authenticated and request.user.username == 'admin':
        print("Redirecting admin to dashboard")
        return redirect('/admin/dashboard')

    # Get user list only if authenticated
    user_list = []
    if request.user.is_authenticated:
        users = Users.objects.all()
        for user in users:
            if user.username == 'admin':
                role = 'Admin'
            else:
                role = 'User'

            entry = {
                'username': user.username,
                'firstname': user.first_name,
                'lastname': user.last_name,
                'role': role,
            }
            user_list.append(entry)
            # Debug log each user
            print(f"Loaded user: {entry}")

    # Get top reviews (available for all users) - only bookmarked reviews
    top_reviews = (
        Review.objects.filter(is_approved=True, is_bookmarked=True)
        .order_by('-rating', '-created_at')[:10]
    )

    print(f"Top reviews count: {top_reviews.count()}")
    for r in top_reviews:
        print(f"Review by {r.user}: {r.rating} stars, created at {r.created_at}")

    return render(request, 'main.html', {
        'logged_in': request.user.is_authenticated,
        'user_list': user_list,
        'top_reviews': top_reviews
    })

def menu(request):
    """Display the full menu page"""
    return render(request, 'menu.html', {
        'logged_in': request.user.is_authenticated,
    })
    
def login_view(request):
    message = ''
    show_register = False

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"[LOGIN ATTEMPT] Username: {username}")

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if user is verified
                if not user.is_verified:
                    
                    print(f"[LOGIN FAILED] User {username} not verified")
                    # Don't login, but show different message
                    return render(request, 'login.html', {
                        'message': message,
                        'show_verification': True,
                        'user_email': user.email
                    })
                
                login(request, user)
                request.session['username'] = username
                request.session['logged_in'] = True

                print(f"[LOGIN SUCCESS] User: {user.username} | Superuser: {user.is_superuser}")

                # Admin redirect
                if user.is_superuser:
                    # request.session['is_moderator'] = False
                    return redirect('/admin/dashboard/')

                # # Moderator redirect
                # if hasattr(user, 'moderator_profile'):
                #     request.session['is_moderator'] = True
                #     return redirect('moderator')

                # Default user
                # request.session['is_moderator'] = False
                return redirect('main')
            else:
                message = 'Invalid username or password.'
                print(f"[LOGIN FAILED] Invalid credentials for {username}")

    logged_in = request.user.is_authenticated
    return render(request, 'login.html', {
        'message': message,
        'show_register': show_register,
        'logged_in': logged_in
    })


def logout_view(request):
    request.session.flush()
    return redirect('login')

def is_admin(request):
    # Check if user is authenticated and is either superuser or has username 'admin'
    if not request.user.is_authenticated:
        return False
    
    # Check if user is superuser OR has username 'admin'
    return request.user.is_superuser or request.user.username == 'admin'

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_admin(request):
            messages.error(request, 'You must be an admin to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ✅ FORGOT PASSWORD FUNCTIONALITY

@csrf_exempt
@require_http_methods(["POST"])
def forgot_password_request(request):
    """Handle forgot password email submission"""
    try:
        # Handle both JSON (mobile) and form data (web)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            email = data.get('email', '').strip()
        else:
            email = request.POST.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required.'})
        
        # Check if user with this email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return JsonResponse({'success': True, 'message': 'If this email exists, an OTP has been sent.'})
        
        # Invalidate any existing OTPs for this email
        PasswordResetOTP.objects.filter(email=email, is_used=False).update(is_used=True)
        
        # Create new OTP
        otp = PasswordResetOTP.objects.create(email=email)
        
        # Send email with OTP
        try:
            subject = 'SoireeWeb - Password Reset OTP'
            message = f"""
Hi {user.first_name or 'User'},

You have requested to reset your password for SoireeWeb.

Your OTP code is: {otp.otp_code}

This code will expire in 15 minutes.

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
            
            return JsonResponse({'success': True, 'message': 'OTP has been sent to your email.'})
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication failed: {e}")
            print(f"Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD settings")
            return JsonResponse({'success': False, 'message': 'Email configuration error. Please contact support.'})
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {e}")
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again.'})
        except Exception as e:
            print(f"Email sending failed: {e}")
            print(f"Email settings - User: {settings.EMAIL_HOST_USER}, From: {settings.DEFAULT_FROM_EMAIL}")
            print(f"Email Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}")
            print(f"TLS: {settings.EMAIL_USE_TLS}, SSL: {settings.EMAIL_USE_SSL}")
            print(f"Error type: {type(e).__name__}")
            
            # Try to identify the specific network issue
            import socket
            try:
                socket.gethostbyname('smtp.gmail.com')
                print("✓ DNS resolution for smtp.gmail.com works")
            except socket.gaierror as dns_error:
                print(f"✗ DNS resolution failed: {dns_error}")
            
            try:
                sock = socket.create_connection(('smtp.gmail.com', 587), timeout=10)
                sock.close()
                print("✓ TCP connection to smtp.gmail.com:587 works")
            except Exception as conn_error:
                print(f"✗ TCP connection failed: {conn_error}")
            
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again.'})
    
    except Exception as e:
        print(f"Error in forgot_password_request: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})


@csrf_exempt
@require_http_methods(["POST"])
def forgot_password_verify_otp(request):
    """Handle OTP verification"""
    try:
        # Handle both JSON (mobile) and form data (web)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            otp_code = data.get('otp', '').strip()
        else:
            email = request.POST.get('email', '').strip()
            otp_code = request.POST.get('otp_code', '').strip()
        
        if not email or not otp_code:
            return JsonResponse({'success': False, 'message': 'Email and OTP are required.'})
        
        # Find valid OTP
        try:
            otp = PasswordResetOTP.objects.get(
                email=email,
                otp_code=otp_code,
                is_used=False
            )
            
            if not otp.is_valid():
                return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})
            
            # For mobile, return success immediately
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'message': 'OTP verified successfully!'})
            
            # For web, store email in session for password reset
            request.session['reset_email'] = email
            request.session['otp_verified'] = True
            
            return JsonResponse({'success': True, 'message': 'OTP verified successfully!'})
            
        except PasswordResetOTP.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid OTP code.'})
    
    except Exception as e:
        print(f"Error in forgot_password_verify_otp: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})


@csrf_exempt
@require_http_methods(["POST"])
def forgot_password_reset(request):
    """Handle new password submission"""
    try:
        # Handle both JSON (mobile) and form data (web)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            new_password = data.get('new_password', '').strip()
            confirm_password = data.get('confirm_password', '').strip()
            email = data.get('email', '').strip()
            otp_code = data.get('otp', '').strip()
            
            # For mobile, verify OTP again in this step
            if not email or not otp_code:
                return JsonResponse({'success': False, 'message': 'Email and OTP are required.'})
            
            # Verify OTP is still valid
            try:
                otp = PasswordResetOTP.objects.get(
                    email=email,
                    otp_code=otp_code,
                    is_used=False
                )
                
                if not otp.is_valid():
                    return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})
                    
            except PasswordResetOTP.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid OTP code.'})
        else:
            # Web form submission
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            
            # Check if OTP was verified for web
            if not request.session.get('otp_verified', False):
                return JsonResponse({'success': False, 'message': 'OTP verification required.'})
            
            email = request.session.get('reset_email')
            if not email:
                return JsonResponse({'success': False, 'message': 'Session expired. Please start over.'})
        
        if not new_password or not confirm_password:
            return JsonResponse({'success': False, 'message': 'All fields are required.'})
        
        if len(new_password) < 8 or len(new_password) > 16:
            return JsonResponse({'success': False, 'message': 'Password must be 8 to 16 characters long.'})
        
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match.'})
        
        try:
            # Update user password
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            PasswordResetOTP.objects.filter(email=email, is_used=False).update(is_used=True)
            
            # Clear session for web
            if request.content_type != 'application/json':
                request.session.pop('reset_email', None)
                request.session.pop('otp_verified', None)
            
            return JsonResponse({'success': True, 'message': 'Password reset successfully! You can now login.'})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})
        except Exception as e:
            print(f"Password reset failed: {e}")
            return JsonResponse({'success': False, 'message': 'Failed to reset password. Please try again.'})
    
    except Exception as e:
        print(f"Error in forgot_password_reset: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})

