"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views
from main import chatbot_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('moredesign/', views.moredesign, name='moredesign'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('moderator/reviews/', views.review_moderation, name='review_moderation'),
    path('moderator/reviews/approve/<int:review_id>/', views.approve_review, name='approve_review'),

    #Chatbot URL
    path('chatbot/', chatbot_views.chatbot_view, name='chatbot'),
    path('chatbot/save/', chatbot_views.save_chat_session, name='save_chat_session'),
    path('chatbot/list/', chatbot_views.list_chat_sessions, name='list_chat_sessions'),
    path('chatbot/load/<int:session_id>/', chatbot_views.load_chat_session, name='load_chat_session'),
    # path('chatbot/delete/<int:session_id>/', chatbot_views.delete_chat_session, name='delete_chat_session'),
    path('chatbot/new/', chatbot_views.new_chat_session, name='new_chat_session'),

]
