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
    # path('home/chatbot/', views.home, name='home'),
    path('signup/', signup, name='signup'),
    path('chatbot/', include(chatbot_urls.urlpatterns)),

    # API endpoint for mobile review submission
    path('api/reviews/', submit_review, name='submit_review'),

    # Moderator dashboard
    path('moderator/reviews/', views.review_moderation, name='review_moderation'),
    path('moderator/reviews/approve/<int:review_id>/', views.approve_review, name='approve_review'),
    path('moderator/', views.moderator_access, name='moderator'),
    
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
    path('bookhere_submit', views.bookhere_submit, name="bookhere_submit"),
    path('my_bookings', views.my_bookings, name='my_bookings'),
    
    path('chatbot', include('main.chatbot_urls')),
    path('event-status/<int:id>/', views.event_status, name="event-status"),

    path('event-booking-stream/<int:id>', views.event_booking_stream, name="event-booking-stream"),
    path('event-booking-send/<int:id>', views.send_booking_message, name="event-booking-send")
]


