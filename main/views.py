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
