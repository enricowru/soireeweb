import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .ai_estimations import analyze_floorplan_image, estimate_from_dimensions, validate_image_file
import logging

# Optional: only import cloudinary in prod
if settings.ENVIRONMENT == "prod":
    import cloudinary.uploader

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def analyze_uploaded_floorplan(request):
    """
    API endpoint to analyze uploaded floorplan image and return AI estimations.
    """
    try:
        if 'floorplan_image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)
        
        image_file = request.FILES['floorplan_image']
        
        # Get event type and pax from request
        event_type = request.POST.get('event_type', 'wedding')
        pax = int(request.POST.get('pax', 100))
        
        # Validate the image file
        is_valid, error_message = validate_image_file(image_file)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)
        
        # Upload image to Cloudinary first
        cloudinary_url = None
        filename = None
        
        try:
            # Generate unique filename
            ext = image_file.name.split('.')[-1] if '.' in image_file.name else 'jpg'
            filename = f"floorplan_{uuid.uuid4().hex[:12]}.{ext}"
            
            if settings.ENVIRONMENT == "prod":
                # Upload to Cloudinary in floorplan folder
                public_id = f"floorplan/{filename}"
                upload_result = cloudinary.uploader.upload(image_file, public_id=public_id)
                cloudinary_url = upload_result["secure_url"]
            else:
                # Save locally for development
                path = f"floorplan/{filename}"
                saved_path = default_storage.save(path, image_file)
                cloudinary_url = f"/media/{saved_path}"
                
        except Exception as e:
            logger.error(f"Error uploading image to Cloudinary: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to upload image. Please try again.'
            }, status=500)

        # Analyze the image using AI
        estimations = analyze_floorplan_image(image_file, event_type, pax)
        
        if estimations is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to analyze image. Please try again or enter room dimensions manually.'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'estimations': estimations,
            'cloudinary_url': cloudinary_url,
            'filename': filename,
            'message': 'Floorplan analyzed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_uploaded_floorplan: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred during analysis'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def estimate_from_room_dimensions(request):
    """
    API endpoint to generate estimations based on room dimensions.
    """
    try:
        data = json.loads(request.body)
        
        length = float(data.get('length', 0))
        width = float(data.get('width', 0))
        event_type = data.get('event_type', 'wedding')
        pax = int(data.get('pax', 100))
        
        if length <= 0 or width <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Please provide valid room dimensions (length and width must be greater than 0)'
            }, status=400)
        
        if length > 1000 or width > 1000:
            return JsonResponse({
                'success': False,
                'error': 'Room dimensions seem too large. Please check your measurements.'
            }, status=400)
        
        # Generate estimations using AI
        estimations = estimate_from_dimensions(length, width, event_type, pax)
        
        return JsonResponse({
            'success': True,
            'estimations': estimations,
            'message': 'Estimations generated successfully'
        })
        
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({
            'success': False,
            'error': 'Invalid input data. Please check your room dimensions.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in estimate_from_room_dimensions: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred during estimation'
        }, status=500)