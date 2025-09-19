from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..themes import get_themes_for_event_type, get_all_themes
import json

@require_http_methods(["GET"])
def api_themes_by_event_type(request):
    """
    API endpoint to get themes based on event type.
    Usage: /api/themes/?event_type=WEDDING
    """
    event_type = request.GET.get('event_type', '')
    
    if not event_type:
        return JsonResponse({'error': 'event_type parameter is required'}, status=400)
    
    themes = get_themes_for_event_type(event_type)
    
    # Convert to list format expected by frontend
    themes_list = []
    for theme_name, image_urls in themes.items():
        themes_list.append({
            'name': theme_name,
            'images': image_urls
        })
    
    return JsonResponse({
        'event_type': event_type.upper(),
        'themes': themes_list
    })

@require_http_methods(["GET"])
def api_all_themes(request):
    """
    API endpoint to get all available themes grouped by event type.
    Usage: /api/themes/all/
    """
    all_themes = get_all_themes()
    
    # Convert to format expected by frontend
    formatted_themes = {}
    for event_type, themes in all_themes.items():
        formatted_themes[event_type] = []
        for theme_name, image_urls in themes.items():
            formatted_themes[event_type].append({
                'name': theme_name,
                'images': image_urls
            })
    
    return JsonResponse({
        'themes': formatted_themes
    })