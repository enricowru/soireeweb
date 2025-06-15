from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from ..utils import is_moderator
from ..models import Review
import json

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


@user_passes_test(is_moderator)
def review_moderation(request):
    pending_reviews = Review.objects.filter(is_approved=False)
    return render(request, 'moderation/review_list.html', {'reviews': pending_reviews})

@user_passes_test(is_moderator)
def approve_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_approved = True
    review.save()
    return redirect('review_moderation')
