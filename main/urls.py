from . import chatbot_urls
from django.urls import path, include
from . import views
from . import chatbot_views

urlpatterns = [
    path('chatbot/', include(chatbot_urls.urlpatterns)),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('moredesign/', views.moredesign, name='moredesign'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup')


    #Chatbot URL
    path('chatbot/', chatbot_views.chatbot_view, name='chatbot'),
    path('chatbot/save/', chatbot_views.save_chat_session, name='save_chat_session'),
    path('chatbot/list/', chatbot_views.list_chat_sessions, name='list_chat_sessions'),
    path('chatbot/load/<int:session_id>/', chatbot_views.load_chat_session, name='load_chat_session'),
    path('chatbot/delete/<int:session_id>/', chatbot_views.delete_chat_session, name='delete_chat_session'),
    path('chatbot/new/', chatbot_views.new_chat_session, name='new_chat_session'),

    # API endpoint for mobile review submission
    path('api/reviews/', views.submit_review, name='submit_review'),

    # Moderator dashboard
    path('moderator/reviews/', views.review_moderation, name='review_moderation'),
    path('moderator/reviews/approve/<int:review_id>/', views.approve_review, name='approve_review'),
]
