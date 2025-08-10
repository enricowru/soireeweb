from django.conf import settings

def global_settings(request):
    return {
        'PROD_HOST': settings.PROD_HOST,
        'LOCAL_HOST': settings.LOCAL_HOST,
    }