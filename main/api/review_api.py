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
        'email': user.email,
        'mobile': user.mobile,
        'profile_picture': user.profile_picture,
    }, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Handle multipart form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        
        # Validate required fields
        if not first_name or not last_name or not email:
            return JsonResponse({
                'error': 'First name, last name, and email are required'
            }, status=400)
        
        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.mobile = mobile if mobile else None
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            
            try:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    profile_picture,
                    folder="profile_pictures",
                    public_id=f"user_{user.id}_{uuid.uuid4().hex[:8]}",
                    transformation=[
                        {'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'},
                        {'quality': 'auto', 'fetch_format': 'auto'}
                    ]
                )
                
                # Save Cloudinary URL
                user.profile_picture = result['secure_url']
                print(f'[INFO] Profile picture uploaded to Cloudinary: {result["secure_url"]}')
                
            except Exception as e:
                print(f'[ERROR] Failed to upload profile picture to Cloudinary: {e}')
                return JsonResponse({
                    'error': 'Failed to upload profile picture'
                }, status=500)
        
        # Save user
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'mobile': user.mobile,
                'profile_picture': user.profile_picture,
            }
        }, status=200)
        
    except Exception as e:
        print(f'[ERROR] Profile update failed: {e}')
        return JsonResponse({
            'error': 'Profile update failed'
        }, status=500)

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
    print(f"[DEBUG] Received review submission request")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Content type: {request.content_type}")
    print(f"[DEBUG] POST data: {request.POST}")
    print(f"[DEBUG] FILES: {request.FILES}")
    
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

    print(f"[DEBUG] Processing rating: {rating}, comment: {comment}, client_id: {client_id}")

    if rating <= 0 or rating > 5 or not comment or not client_id:
        print(f"[ERROR] Validation failed - rating: {rating}, comment: {comment}, client_id: {client_id}")
        return JsonResponse({'error': 'rating (1-5), comment, and client_id are required'}, status=400)

    # Ensure numeric client id
    try:
        client_id_int = int(client_id)
        print(f"[DEBUG] Client ID parsed as: {client_id_int}")
    except (TypeError, ValueError):
        print(f"[ERROR] Client ID is not numeric: {client_id}")
        return JsonResponse({'error': 'client_id must be numeric'}, status=400)

    # Check if user exists
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=client_id_int)
        print(f"[DEBUG] Found user: {user.username}")
    except User.DoesNotExist:
        print(f"[ERROR] User with ID {client_id_int} does not exist")
        return JsonResponse({'error': 'User not found'}, status=404)

    # Create review directly (no event required since event field is commented out)
    review_data = {
        'user_id': client_id_int,
        'rating': rating,
        'comment': comment,
        'is_approved': False,
    }
    
    # Add image URLs to review data (up to 3)
    for i, url in enumerate(image_urls[:3]):
        review_data[f'image{i+1}'] = url
        print(f"[DEBUG] Added image{i+1}: {url}")
    
    try:
        r = Review.objects.create(**review_data)
        print(f"[DEBUG] Created review with ID: {r.id}")
        return JsonResponse({'message': 'Review submitted successfully', 'id': r.id}, status=201)
    except Exception as e:
        print(f"[ERROR] Failed to create review: {e}")
        return JsonResponse({'error': 'Failed to create review'}, status=500)
