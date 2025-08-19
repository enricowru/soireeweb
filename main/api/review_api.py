from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Avg, Count
from ..models import Review, BookingRequest, Event
import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
import cloudinary.uploader
import base64
import uuid

@csrf_exempt
@require_http_methods(["GET"])
def me(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return JsonResponse({'authenticated': False}, status=200)
    return JsonResponse({
        'authenticated': True,
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
    }, status=200)

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
            'images': r.get_images(),  # Get the image URLs
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
    client_id = None
    
    # Handle images from request
    image_urls = []
    
    if request.content_type and 'application/json' in request.content_type:
        try:
            body = json.loads(request.body or '{}')
            rating = int(body.get('rating') or rating)
            comment = body.get('comment') or comment
            client_id = body.get('client_id')
            
            # Handle base64 images
            images = body.get('images', [])
            for i, img_data in enumerate(images[:3]):  # Max 3 images
                if img_data and img_data.startswith('data:image/'):
                    try:
                        # Extract base64 data
                        format_part, data_part = img_data.split(',', 1)
                        img_bytes = base64.b64decode(data_part)
                        
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            img_bytes,
                            public_id=f"review_{uuid.uuid4()}",
                            folder="reviews"
                        )
                        image_urls.append(result['secure_url'])
                    except Exception as e:
                        print(f"Error uploading image {i}: {e}")
                        
        except Exception:
            pass
    else:
        client_id = request.POST.get('client_id')
        
        # Handle file uploads
        for i in range(1, 4):  # image1, image2, image3
            file = request.FILES.get(f'image{i}')
            if file:
                try:
                    result = cloudinary.uploader.upload(
                        file,
                        public_id=f"review_{uuid.uuid4()}",
                        folder="reviews"
                    )
                    image_urls.append(result['secure_url'])
                except Exception as e:
                    print(f"Error uploading file image {i}: {e}")

    if rating <= 0 or rating > 5 or not comment or not client_id:
        return JsonResponse({'error': 'rating (1-5), comment, and client_id are required'}, status=400)

    # Ensure numeric client id
    try:
        client_id_int = int(client_id)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'client_id must be numeric'}, status=400)

    # Latest booking for this client (draft or confirmed) to infer event date
    booking = (
        BookingRequest.objects.filter(client_id=client_id_int)
        .order_by('-created_at')
        .first()
    )
    if not booking or not getattr(booking, 'event_date', None):
        return JsonResponse({'error': 'No booking with event date found for client'}, status=404)

    # Find corresponding event by date
    event = Event.objects.filter(date=booking.event_date).order_by('-date').first()
    if not event:
        return JsonResponse({'error': 'Event not found for booking date'}, status=404)

    # Create review (unapproved) tying to user and event with images
    review_data = {
        'user_id': client_id_int,
        'event': event,
        'rating': rating,
        'comment': comment,
        'is_approved': False,
    }
    
    # Add image URLs to review data (up to 3)
    for i, url in enumerate(image_urls[:3]):
        review_data[f'image{i+1}'] = url
    
    r = Review.objects.create(**review_data)
    return JsonResponse({'message': 'Review submitted', 'id': r.id}, status=201)
