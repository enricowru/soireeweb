# redirect_to_www.py
from django.http import HttpResponsePermanentRedirect

class RedirectToWwwMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host.startswith('nikescateringservices.com'):
            return HttpResponsePermanentRedirect('https://www.nikescateringservices.com' + request.get_full_path())
        return self.get_response(request)
