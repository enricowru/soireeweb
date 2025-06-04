from . import chatbot_urls
from django.urls import path, include
from . import views
from . import chatbot_views
from .views import signup
from django.shortcuts import redirect


urlpatterns = [
    path('chatbot/', include(chatbot_urls.urlpatterns)),
    path('', views.home),  # instead of views.redirect_home
    path('login/', views.login_view, name='login'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('moredesign/', views.moredesign, name='moredesign'),
    path('home/', views.home, name='home'),
    path('home/chatbot/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),

    # API endpoint for mobile review submission
    path('api/reviews/', views.submit_review, name='submit_review'),

    # Moderator dashboard
    path('moderator/reviews/', views.review_moderation, name='review_moderation'),
    path('moderator/reviews/approve/<int:review_id>/', views.approve_review, name='approve_review'),
]
