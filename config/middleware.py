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
        if request.path in [
            '/forgot-password/request/',
            '/forgot-password/verify-otp/',
            '/forgot-password/reset/'
        ]:
            # Mark request as CSRF exempt
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
