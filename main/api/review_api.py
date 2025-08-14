from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Avg, Count
from ..models import Review, BookingRequest, Event
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
    # Only approved reviews
    qs = Review.objects.filter(is_approved=True).order_by('-created_at')[:50]
    data = []
    for r in qs:
        data.append({
            'user': r.user.get_full_name() if r.user else 'Guest',
            'avatar': None,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at.isoformat(),
            'images': [],  # No images for main Review
        })
    aggs = Review.objects.filter(is_approved=True).aggregate(average=Avg('rating'), count=Count('id'))
    avg = float(aggs['average'] or 0)
    cnt = int(aggs['count'] or 0)
    return JsonResponse({'average': round(avg, 1), 'count': cnt, 'reviews': data}, status=200)


# ---- Minimal submit endpoint with optional images (multipart) ----
@csrf_exempt
@require_http_methods(["POST"])
def submit_mobile_review(request):
    # Accept application/json or form-data
    rating = int(request.POST.get('rating') or request.GET.get('rating') or 0)
    comment = request.POST.get('comment') or ''
    event_id = None
    if request.content_type and 'application/json' in request.content_type:
        try:
            body = json.loads(request.body or '{}')
            rating = int(body.get('rating') or rating)
            comment = body.get('comment') or comment
            event_id = body.get('event_id')
        except Exception:
            pass
    else:
        event_id = request.POST.get('event_id')

    if rating <= 0 or rating > 5 or not comment or not event_id:
        return JsonResponse({'error': 'rating (1-5), comment, and event_id are required'}, status=400)

    # Save review as unapproved
    user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

    r = Review.objects.create(
        user=user,
        event=event,
        rating=rating,
        comment=comment,
        is_approved=False,
    )
    return JsonResponse({'message': 'Review submitted', 'id': r.id}, status=201)
