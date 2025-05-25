from django.shortcuts import render

def home(request):
    return render(request, 'main.html')

def login_view(request):
    return render(request, 'login.html')