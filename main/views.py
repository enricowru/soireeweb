from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from .models import Review  # Make sure Review model is defined in models.py


@csrf_exempt
def home(request):
    return render(request, 'main.html')


@csrf_exempt
def login_view(request):
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

# ✅ Moderator Check
def is_moderator(user):
    return user.groups.filter(name='Moderators').exists()


# ✅ Moderation Page – List of Pending Reviews
@user_passes_test(is_moderator)
def review_moderation(request):
    pending_reviews = Review.objects.filter(is_approved=False)
    return render(request, 'moderation/review_list.html', {'reviews': pending_reviews})


# ✅ Approve Individual Review
@user_passes_test(is_moderator)
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()
    return redirect('review_moderation')
