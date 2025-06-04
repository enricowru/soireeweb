from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import Review
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import json


@csrf_exempt
def redirect_home(request):
    return render(request, 'main.html')


@csrf_exempt
def home(request):
    return render(request, 'main.html')


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/home/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    # Handle GET requests (when visiting /login)
    return render(request, 'login.html')


def editprofile(request):
    return render(request, 'editprofile.html')
    

def moredesign(request):
    sets = {
        'themed_backdrop': [
            {
                'title': 'Kuromi and My Melody',
                'images': [
                    'images/upgraded balloon set-up/R1C.jpg',
                    'images/upgraded balloon set-up/R1A.jpg',
                    'images/upgraded balloon set-up/R1D.jpg',
                    'images/upgraded balloon set-up/R1B.jpg',
                ]
            },
            {
                'title': 'Teddy Bear',
                'images': [
                    'images/upgraded balloon set-up/R2C.jpg',
                    'images/upgraded balloon set-up/R2A.jpg',
                    'images/upgraded balloon set-up/R2D.jpg',
                    'images/upgraded balloon set-up/R2B.jpg',
                ]
            },
            {
                'title': 'Kuromi and My Melody (2)',
                'images': [
                    'images/upgraded balloon set-up/R3C.jpg',
                    'images/upgraded balloon set-up/R3A.jpg',
                    'images/upgraded balloon set-up/R3D.jpg',
                    'images/upgraded balloon set-up/R3B.jpg',
                ]
            },
            {
                'title': 'Baby Blue Bear',
                'images': [
                    'images/upgraded balloon set-up/R4C.jpg',
                    'images/upgraded balloon set-up/R4A.jpg',
                    'images/upgraded balloon set-up/R4D.jpg',
                    'images/upgraded balloon set-up/R4B.jpg',
                ]
            },
            {
                'title': 'Disney Princesses',
                'images': [
                    'images/upgraded balloon set-up/R5C.jpg',
                    'images/upgraded balloon set-up/R5A.jpg',
                    'images/upgraded balloon set-up/R5D.jpg',
                    'images/upgraded balloon set-up/R5B.jpg',
                ]
            },
            {
                'title': 'Safari Jungle',
                'images': [
                    'images/upgraded balloon set-up/R6C.jpg',
                    'images/upgraded balloon set-up/R6A.jpg',
                    'images/upgraded balloon set-up/R6D.jpg',
                    'images/upgraded balloon set-up/R6B.jpg',
                ]
            },
            {
                'title': 'Iron Man and Frozen',
                'images': [
                    'images/upgraded balloon set-up/R7C.jpg',
                    'images/upgraded balloon set-up/R7A.jpg',
                    'images/upgraded balloon set-up/R7D.jpg',
                    'images/upgraded balloon set-up/R7B.jpg',
                ]
            },
            {
                'title': 'Cinderella',
                'images': [
                    'images/upgraded balloon set-up/R8C.jpg',
                    'images/upgraded balloon set-up/R8A.jpg',
                    'images/upgraded balloon set-up/R8D.jpg',
                    'images/upgraded balloon set-up/R8B.jpg',
                ]
            },
            {
                'title': 'Blue Royalty',
                'images': [
                    'images/upgraded balloon set-up/R9C.jpg',
                    'images/upgraded balloon set-up/R9A.jpg',
                    'images/upgraded balloon set-up/R9D.jpg',
                    'images/upgraded balloon set-up/R9B.jpg',
                ]
            },
            {
                'title': 'Pink Floral',
                'images': [
                    'images/upgraded balloon set-up/R10C.jpg',
                    'images/upgraded balloon set-up/R10A.jpg',
                    'images/upgraded balloon set-up/R10D.jpg',
                    'images/upgraded balloon set-up/R10B.jpg',
                ]
            },
            {
                'title': 'Mermaid and Sea Life',
                'images': [
                    'images/upgraded balloon set-up/R11C.jpg',
                    'images/upgraded balloon set-up/R11A.jpg',
                    'images/upgraded balloon set-up/R11D.jpg',
                    'images/upgraded balloon set-up/R11B.jpg',
                ]
            },
            {
                'title': 'Barbie',
                'images': [
                    'images/upgraded balloon set-up/R12C.jpg',
                    'images/upgraded balloon set-up/R12A.jpg',
                    'images/upgraded balloon set-up/R12D.jpg',
                    'images/upgraded balloon set-up/R12B.jpg',
                ]
            },
            {
                'title': 'Butterfly Garden',
                'images': [
                    'images/upgraded balloon set-up/R13C.jpg',
                    'images/upgraded balloon set-up/R13A.jpg',
                    'images/upgraded balloon set-up/R13D.jpg',
                    'images/upgraded balloon set-up/R13B.jpg',
                ]
            },
        ],
        'minimalist_setup': [
            {
                'title': 'Red & White Roses',
                'images': [
                    'images/minimalist set-up/R1C.jpg',
                    'images/minimalist set-up/R1A.jpg',
                    'images/minimalist set-up/R1D.jpg',
                    'images/minimalist set-up/R1B.jpg',
                ]
            },
            {
                'title': 'Ivory Simplicity',
                'images': [
                    'images/minimalist set-up/R2C.jpg',
                    'images/minimalist set-up/R2A.jpg',
                    'images/minimalist set-up/R2D.jpg',
                    'images/minimalist set-up/R2B.jpg',
                ]
            },
            {
                'title': 'Modern Minimal',
                'images': [
                    'images/minimalist set-up/R3C.jpg',
                    'images/minimalist set-up/R3A.jpg',
                    'images/minimalist set-up/R3D.jpg',
                    'images/minimalist set-up/R3B.jpg',
                ]
            },
            {
                'title': 'Modern Minimal',
                'images': [
                    'images/minimalist set-up/R4C.jpg',
                    'images/minimalist set-up/R4A.jpg',
                    'images/minimalist set-up/R4D.jpg',
                    'images/minimalist set-up/R4B.jpg',
                ]
            },
            {
                'title': 'Modern Minimal',
                'images': [
                    'images/minimalist set-up/R5C.jpg',
                    'images/minimalist set-up/R5A.jpg',
                    'images/minimalist set-up/R5D.jpg',
                    'images/minimalist set-up/R5B.jpg',
                ]
            },
            {
                'title': 'Modern Minimal',
                'images': [
                    'images/minimalist set-up/R6C.jpg',
                    'images/minimalist set-up/R6A.jpg',
                    'images/minimalist set-up/R6D.jpg',
                    'images/minimalist set-up/R6B.jpg',
                ]
            },
            {
                'title': 'Modern Minimal',
                'images': [
                    'images/minimalist set-up/R7C.jpg',
                    'images/minimalist set-up/R7A.jpg',
                    'images/minimalist set-up/R7D.jpg',
                    'images/minimalist set-up/R7B.jpg',
                ]
            },
            {
                'title': 'Modern Minimal',
                'images': [
                    'images/minimalist set-up/R8C.jpg',
                    'images/minimalist set-up/R8A.jpg',
                    'images/minimalist set-up/R8D.jpg',
                    'images/minimalist set-up/R8B.jpg',
                ]
            },
            {
                'title': 'Modern Minimal',
                'images': [
                    'images/minimalist set-up/R9C.jpg',
                    'images/minimalist set-up/R9A.jpg',
                    'images/minimalist set-up/R9D.jpg',
                    'images/minimalist set-up/R9B.jpg',
                ]
            },
        ],
        'signature_setup': [
            {
                'title': 'Luxury Signature',
                'images': [
                    'images/signature set-up/R1C.jpg',
                    'images/signature set-up/R1A.jpg',
                    'images/signature set-up/R1E.jpg',
                    'images/signature set-up/R1F.jpg',
                    'images/signature set-up/R1B.jpg',
                    'images/signature set-up/R1D.jpg',
                ]
            },
            {
                'title': 'Luxury Signature',
                'images': [
                    'images/signature set-up/R2C.jpg',
                    'images/signature set-up/R2A.jpg',
                    'images/signature set-up/R2E.jpg',
                    'images/signature set-up/R2F.jpg',
                    'images/signature set-up/R2B.jpg',
                    'images/signature set-up/R2D.jpg',
                ]
            },
            {
                'title': 'Luxury Signature',
                'images': [
                    'images/signature set-up/R3C.jpg',
                    'images/signature set-up/R3A.jpg',
                    'images/signature set-up/R3E.jpg',
                    'images/signature set-up/R3F.jpg',
                    'images/signature set-up/R3B.jpg',
                    'images/signature set-up/R3D.jpg',
                ]
            },
            {
                'title': 'Luxury Signature',
                'images': [
                    'images/signature set-up/R4C.jpg',
                    'images/signature set-up/R4A.jpg',
                    'images/signature set-up/R4E.jpg',
                    'images/signature set-up/R4F.jpg',
                    'images/signature set-up/R4B.jpg',
                    'images/signature set-up/R4D.jpg',
                ]
            },
        ],
    }
    return render(request, 'moredesign.html', {'sets': sets})


# ✅ Moderator Permission Check
def is_moderator(user):
    return user.groups.filter(name='Moderators').exists()


# ✅ API for Mobile App to Submit Review
@csrf_exempt
def submit_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        message = data.get('message')

        if name and message:
            Review.objects.create(username=name, comment=message, is_approved=False)
            return JsonResponse({'message': 'Review submitted successfully'}, status=201)
        else:
            return JsonResponse({'error': 'Name and message are required'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# ✅ Moderator View for Pending Reviews
@user_passes_test(is_moderator)
def review_moderation(request):
    pending_reviews = Review.objects.filter(is_approved=False)
    return render(request, 'moderation/review_list.html', {'reviews': pending_reviews})


# ✅ Approve a Review by ID
@user_passes_test(is_moderator)
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()
    return redirect('review_moderation')


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
        mobile = data.get('mobile')  # Optional - only stored if you extend the User model

        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'Username already exists'}, status=400)

        user = User.objects.create_user(
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