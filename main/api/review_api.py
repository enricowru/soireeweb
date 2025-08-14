from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Avg, Count
from ..models import Review, MobileReview, MobileReviewImage
import json
from django.views.decorators.http import require_http_methods

@csrf_exempt
def submit_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        message = data.get('message')

        if name and message:
            Review.objects.create(username=name, comment=message, is_approved=False)
            return JsonResponse({'message': 'Review submitted successfully'}, status=201)
        return JsonResponse({'error': 'Name and message are required'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# ---- Minimal JSON list endpoint for mobile ----
@csrf_exempt
@require_http_methods(["GET"])
def list_mobile_reviews(request):
    qs = MobileReview.objects.all().order_by('-created_at')[:50]
    data = []
    for r in qs:
        data.append({
            'user': r.display_name(),
            'avatar': None,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat(),
            'images': [img.image.url for img in r.images.all()],
        })
    aggs = MobileReview.objects.aggregate(average=Avg('rating'), count=Count('id'))
    avg = float(aggs['average'] or 0)
    cnt = int(aggs['count'] or 0)
    return JsonResponse({'average': round(avg, 1), 'count': cnt, 'reviews': data}, status=200)




# ---- Minimal submit endpoint with optional images (multipart) ----
@csrf_exempt
@require_http_methods(["POST"])
def submit_mobile_review(request):
    # Accept application/json or multipart/form-data
    rating = int(request.POST.get('rating') or request.GET.get('rating') or 0)
    comment = request.POST.get('comment') or ''
    name = request.POST.get('name') or 'Mobile User'
    if request.content_type and 'application/json' in request.content_type:
        try:
            body = json.loads(request.body or '{}')
            rating = int(body.get('rating') or rating)
            comment = body.get('comment') or comment
            name = body.get('name') or name
        except Exception:
            pass

    if rating <= 0 or rating > 5 or not comment:
        return JsonResponse({'error': 'rating (1-5) and comment are required'}, status=400)

    mr = MobileReview.objects.create(
        user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
        name=None if getattr(request, 'user', None) and request.user.is_authenticated else name,
        rating=rating,
        comment=comment,
    )

    for f in request.FILES.getlist('images'):
        MobileReviewImage.objects.create(review=mr, image=f)

    return JsonResponse({'message': 'Review submitted', 'id': mr.id}, status=201)
