from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
import json
from django.contrib.auth.decorators import login_required

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
            last_name=lastname
        )
        
        # Set mobile field separately since create_user doesn't handle custom fields
        if mobile:
            user.mobile = mobile
            user.save()
            
        print(f"[SIGNUP] User created successfully: {user.id}")

        return JsonResponse({'message': 'User registered successfully'}, status=201)
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
