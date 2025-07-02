from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

User = get_user_model()

# In-memory user store
USERS = {
    'admin': {
        'password': 'admin123',
        'firstname': 'Admin',
        'lastname': 'User',
        'email': 'admin@example.com',
        'mobile': '',
        'is_admin': True,
    },
    'moderator': {
        'password': 'moderator123',
        'firstname': 'Mod',
        'lastname': 'Erator',
        'email': 'moderator@example.com',
        'mobile': '',
        'is_moderator': True,
    }
}

def home(request):
    if not request.session.get('logged_in', False):
        return redirect('login')
    
    user_list = []
    for username, user in USERS.items():
        role = 'Admin' if user.get('is_admin') else 'Moderator' if user.get('is_moderator') else 'User'
        user_list.append({
            'username': username,
            'firstname': user.get('firstname', ''),
            'lastname': user.get('lastname', ''),
            'role': role
        })
    return render(request, 'main.html', {'logged_in': True, 'user_list': user_list})


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
                login(request, user)
                request.session['username'] = username
                request.session['logged_in'] = True

                print(f"[LOGIN SUCCESS] User: {user.username} | Superuser: {user.is_superuser}")

                # Admin redirect
                if user.is_superuser:
                    request.session['is_moderator'] = False
                    return redirect('admin_dashboard')

                # Moderator redirect
                if hasattr(user, 'moderator_profile'):
                    request.session['is_moderator'] = True
                    return redirect('moderator')

                # Default user
                request.session['is_moderator'] = False
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
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def is_admin(request):
    username = request.session.get('username')
    user = USERS.get(username)
    return user and user.get('is_admin')

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_admin(request):
            messages.error(request, 'You must be an admin to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# @csrf_exempt
# @require_http_methods(["POST"])
# def signup(request):
#     try:
#         data = json.loads(request.body)
#         firstname = data.get('firstname')
#         lastname = data.get('lastname')
#         username = data.get('username')
#         email = data.get('email')
#         password = data.get('password')
#         mobile = data.get('mobile')  # Optional - only stored if you extend the User model

#         if User.objects.filter(username=username).exists():
#             return JsonResponse({'message': 'Username already exists'}, status=400)

#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password,
#             first_name=firstname,
#             last_name=lastname
#         )

#         response = JsonResponse({'message': 'User registered successfully'}, status=201)
#     except Exception as e:
#         response = JsonResponse({'message': 'Server error', 'error': str(e)}, status=500)

#     response["Access-Control-Allow-Origin"] = "https://nikescateringservices.com"
#     response["Access-Control-Allow-Credentials"] = "true"
#     return response