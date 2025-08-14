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
        data = json.loads(request.body)
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname
        )

        return JsonResponse({'message': 'User registered successfully'}, status=201)
    except Exception as e:
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
