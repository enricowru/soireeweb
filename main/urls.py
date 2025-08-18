from . import chatbot_urls
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .api import *


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='main'),  
   
    path('editprofile/', views.editprofile, name='editprofile'),
    path('moredesign/', views.moredesign, name='moredesign'),
    path('home/', views.home, name='home'),
    path('home/chatbot/', views.home, name='home'),
    path('signup/', signup, name='signup'),
    path('chatbot/', include('main.chatbot_urls')),
    path('api/update-profile/', update_profile, name='api_update_profile'),

    # ✅ Forgot Password Routes
    path('forgot-password/request/', views.forgot_password_request, name='forgot_password_request'),
    path('forgot-password/verify-otp/', views.forgot_password_verify_otp, name='forgot_password_verify_otp'),
    path('forgot-password/reset/', views.forgot_password_reset, name='forgot_password_reset'),


    # API endpoint for mobile review submission
    path('api/reviews/', submit_review, name='submit_review'),

    # Minimal mobile reviews API (list + submit with images)
    path('api/reviews/list/', list_mobile_reviews, name='mobile_reviews_list'),
    path('api/reviews/submit/', submit_mobile_review, name='mobile_reviews_submit'),
    path('api/me/', me, name='api_me'),

    # Moderator dashboard
    # path('moderator/reviews/', views.review_moderation, name='review_moderation'),
    # path('moderator/reviews/approve/<int:review_id>/', views.approve_review, name='approve_review'),
    # path('moderator/', views.moderator_access, name='moderator'),
    
    path('admin/', include('main.admin_urls')),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/create/', views.create_chat, name='create_chat'),
    path('chat/send-message/', views.send_message, name='send_message'),
    path("chat/<int:chat_id>/messages-json/", views.chat_messages_json, name="chat_messages_json"),
    
    path('bookhere/', views.bookhere, name='bookhere'),
    path('cloudImg', views.get_cloud_image_by_name, name='cloudImg'),
    path('bookhere_submit', views.bookhere_submit, name="bookhere_submit"),
    path('my_bookings', views.my_bookings, name='my_bookings'),
    
    # path('chatbot', include('main.chatbot_urls')),
    path('event-status/<int:id>/', views.event_status, name="event-status"),

    path('event-booking-send/<int:id>', views.send_booking_message, name="event-booking-send"),
    
    # API Exposing bookin
    
    path('api/event-status/<int:id>', views.api_booking_status, name="api-event-status"),
    path('api/my-bookings', views.api_booking_list, name="api-my-booking"),
    path('event-booking-send/<int:id>', views.send_booking_message, name="event-booking-send"),

    # Mobile posts API
    path('api/posts/', get_all_posts, name='api_posts_list'),
    path('api/posts/<int:post_id>/', get_post_detail, name='api_post_detail'),
    path('api/posts/<int:post_id>/like/', toggle_like, name='api_post_like'),
    path('api/posts/<int:post_id>/comments/', submit_comment, name='api_post_comment')
]


