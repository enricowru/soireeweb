from django.urls import path
# from .views import chatbot_view, save_chat_session, list_chat_sessions, load_chat_session, delete_chat_session, new_chat_session
# from .views import chatbot_view, save_chat_session, list_chat_sessions, load_chat_session, delete_chat_session, new_chat_session
from . import chatbot_views


# urlpatterns = [
#     path('chatbot/', chatbot_view, name='chatbot'),
#     path('chatbot/save/', save_chat_session, name='save_chat_session'),
#     path('chatbot/list/', list_chat_sessions, name='list_chat_sessions'),
#     path('chatbot/load/<int:session_id>/', load_chat_session, name='load_chat_session'),
#     path('chatbot/delete/<int:session_id>/', delete_chat_session, name='delete_chat_session'),
#     path('chatbot/new/', new_chat_session, name='new_chat_session'),
# ]

urlpatterns = [
    path('', chatbot_views.chatbot_view, name='chatbot'),
    path('save/', chatbot_views.save_chat_session, name='save_chat_session'),
    path('list/', chatbot_views.list_chat_sessions, name='list_chat_sessions'),
    path('load/<int:session_id>/', chatbot_views.load_chat_session, name='load_chat_session'),
    path('delete/<int:session_id>/', chatbot_views.delete_chat_session, name='delete_chat_session'),
    path('new/', chatbot_views.new_chat_session, name='new_chat_session'),
]