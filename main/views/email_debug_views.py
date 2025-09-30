"""
Production email testing views
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.conf import settings
from main.utils.email_debug import (
    comprehensive_email_diagnosis, 
    send_test_email,
    test_network_connectivity,
    get_render_optimized_email_settings
)


@staff_member_required
@require_http_methods(["GET"])
def email_diagnosis_view(request):
    """
    Secure endpoint for email diagnosis - staff only
    """
    try:
        # Capture diagnosis output
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        output = io.StringIO()
        error_output = io.StringIO()
        
        with redirect_stdout(output), redirect_stderr(error_output):
            success = comprehensive_email_diagnosis()
        
        diagnosis_output = output.getvalue()
        error_output_text = error_output.getvalue()
        
        return JsonResponse({
            'success': success,
            'diagnosis_output': diagnosis_output,
            'error_output': error_output_text,
            'recommended_settings': get_render_optimized_email_settings() if not success else None,
            'current_environment': settings.ENVIRONMENT,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def test_email_view(request):
    """
    Secure endpoint for sending test emails - staff only
    """
    try:
        data = json.loads(request.body)
        to_email = data.get('to_email')
        
        if not to_email:
            return JsonResponse({
                'success': False,
                'error': 'to_email is required'
            }, status=400)
        
        # Capture test email output
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        output = io.StringIO()
        error_output = io.StringIO()
        
        with redirect_stdout(output), redirect_stderr(error_output):
            success, message = send_test_email(to_email)
        
        test_output = output.getvalue()
        error_output_text = error_output.getvalue()
        
        return JsonResponse({
            'success': success,
            'message': message,
            'test_output': test_output,
            'error_output': error_output_text,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def network_test_view(request):
    """
    Test network connectivity - staff only
    """
    try:
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        output = io.StringIO()
        error_output = io.StringIO()
        
        with redirect_stdout(output), redirect_stderr(error_output):
            success = test_network_connectivity()
        
        network_output = output.getvalue()
        error_output_text = error_output.getvalue()
        
        return JsonResponse({
            'success': success,
            'network_output': network_output,
            'error_output': error_output_text,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)