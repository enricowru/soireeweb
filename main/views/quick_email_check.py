"""
Quick email configuration check view for immediate diagnosis
"""
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from decouple import config


@staff_member_required
@require_http_methods(["GET"])
def quick_email_config_check(request):
    """
    Quick check of email configuration - shows what Render is actually providing
    """
    try:
        # Get raw environment variable
        raw_password = os.environ.get('EMAIL_HOST_PASSWORD', '')
        config_password = config('EMAIL_HOST_PASSWORD', default='')
        cleaned_password = settings.EMAIL_HOST_PASSWORD
        
        return JsonResponse({
            'render_env_analysis': {
                'raw_env_var': f"'{raw_password}'",  # Show with quotes to see what Render provides
                'raw_length': len(raw_password),
                'has_quotes': raw_password.startswith('"') and raw_password.endswith('"'),
                'has_spaces': ' ' in raw_password,
                'config_decouple': f"'{config_password}'",
                'config_length': len(config_password),
                'cleaned_password': f"'{cleaned_password}'",
                'cleaned_length': len(cleaned_password),
                'is_16_chars': len(cleaned_password) == 16,
            },
            'email_settings': {
                'EMAIL_HOST': settings.EMAIL_HOST,
                'EMAIL_PORT': settings.EMAIL_PORT,
                'EMAIL_USE_TLS': settings.EMAIL_USE_TLS,
                'EMAIL_USE_SSL': settings.EMAIL_USE_SSL,
                'EMAIL_TIMEOUT': settings.EMAIL_TIMEOUT,
                'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
                'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
            },
            'environment': settings.ENVIRONMENT,
            'render_diagnosis': {
                'render_auto_quoted': raw_password.startswith('"') and raw_password.endswith('"'),
                'password_format_correct': len(cleaned_password) == 16 and cleaned_password.isalnum(),
                'explanation': 'Gmail passwords have spaces. Render auto-quotes them. Django removes quotes+spaces.',
                'process_flow': {
                    'step1_gmail_provides': 'abcd efgh ijkl mnop (with spaces)',
                    'step2_render_stores': '"abcd efgh ijkl mnop" (auto-quoted due to spaces)',
                    'step3_django_cleans': 'abcdefghijklmnop (removes quotes and spaces)'
                },
                'recommendation': 'Set Gmail password WITH spaces in Render. Let Render auto-quote it. Django will clean it.'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)