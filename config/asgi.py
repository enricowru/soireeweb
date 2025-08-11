import os
import django
from django.core.asgi import get_asgi_application

# This line must be at the very top, before other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# You should also add this line to ensure all apps are loaded
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from main.ws import websocket_urlpatterns

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket":  URLRouter(
        websocket_urlpatterns
    )
})