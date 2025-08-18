# redirect_to_www.py
from django.http import HttpResponsePermanentRedirect


from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect

class RedirectToWwwMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host.startswith('nikescateringservices.com'):
            return HttpResponsePermanentRedirect('https://www.nikescateringservices.com' + request.get_full_path())
        return self.get_response(request)

# --- Custom Middleware to Bypass Referer Checking for Forgot Password Endpoints ---
class BypassRefererCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # List of paths that should be exempt from CSRF checks for mobile clients
        exempt_paths = [
            '/forgot-password/request/',
            '/forgot-password/verify-otp/',
            '/forgot-password/reset/',
            '/api/posts/',  # Mobile posts API
        ]
        
        # Check for API endpoints with dynamic IDs
        api_patterns = [
            '/api/posts/',
        ]
        
        # Mark request as CSRF exempt if it matches any pattern
        should_exempt = False
        
        # Direct path match
        if request.path in exempt_paths:
            should_exempt = True
        
        # Pattern matching for API endpoints with IDs
        for pattern in api_patterns:
            if request.path.startswith(pattern):
                should_exempt = True
                break
        
        if should_exempt:
            # Mark request as CSRF exempt
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return None
