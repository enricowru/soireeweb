from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # match chat room by booking/chat id:
    re_path(r"ws/chat/(?P<chat_id>\d+)/$", consumers.EventBookingConsumer.as_asgi()),
]