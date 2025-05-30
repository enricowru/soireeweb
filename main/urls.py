from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('moredesign/', views.moredesign, name='moredesign'),

    # API endpoint for mobile review submission
    path('api/reviews/', views.submit_review, name='submit_review'),

    # Moderator dashboard
    path('moderator/reviews/', views.review_moderation, name='review_moderation'),
    path('moderator/reviews/approve/<int:review_id>/', views.approve_review, name='approve_review'),
]
