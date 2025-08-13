from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
# from ..models import Moderator

Users = get_user_model()


@login_required
def home(request):
    if request.user.username == 'admin':
        return redirect('/admin/dashboard')

    users = Users.objects.all()
    user_list = []

    for user in users:
        if user.username == 'admin':
            role = 'Admin'
        else:
            role = 'User'

        user_list.append({
            'username': user.username,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'role': role,
        })

    return render(request, 'main.html', {
        'logged_in': True,
        'user_list': user_list
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
                login(request, user)
                request.session['username'] = username
                request.session['logged_in'] = True

                print(f"[LOGIN SUCCESS] User: {user.username} | Superuser: {user.is_superuser}")

                # Admin redirect
                if user.is_superuser:
                    # request.session['is_moderator'] = False
                    return redirect('admin_dashboard')

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
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def is_admin(request):
    username = request.session.get('username')
    return username == 'admin'

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_admin(request):
            messages.error(request, 'You must be an admin to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

