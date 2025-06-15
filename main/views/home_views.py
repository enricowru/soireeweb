from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def home(request):
    return render(request, 'main.html')

@csrf_exempt
def redirect_home(request):
    return render(request, 'main.html')
