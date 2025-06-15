from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


@csrf_exempt
def login_view(request):
    return render(request, 'login.html')

def editprofile(request):
    return render(request, 'editprofile.html')

@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        firstname = data.get('firstname')
        lastname = data.get('lastname')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists'}, status=400)

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname
        )

        response = JsonResponse({'message': 'User registered successfully'}, status=201)
    except Exception as e:
        response = JsonResponse({'message': 'Server error', 'error': str(e)}, status=500)

    response["Access-Control-Allow-Origin"] = "https://nikescateringservices.com"
    response["Access-Control-Allow-Credentials"] = "true"
    return response
