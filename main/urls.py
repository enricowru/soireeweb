from . import chatbot_urls
from django.urls import path, include
from . import views
from . import chatbot_views
from django.contrib.auth import views as auth_views
from .views import *
from django.shortcuts import redirect


urlpatterns = [
    path('chatbot/', include(chatbot_urls.urlpatterns)),
    # path('', views.home),  # instead of views.redirect_home
    path('', views.home, name='main'),  # ✅ FIXED: now matches {% url 'main' %}
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
   
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

    #Moderator URLs
    path('moderator/', views.moderator_access, name='moderator'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/profile/edit/', views.admin_edit, name='admin_edit'),
    path('admin/event/history/', views.event_history, name='event_history'),
    path('admin/event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('admin/event/create/', views.create_event, name='create_event'),
     path('admin/event/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('admin/event/<int:event_id>/grant-access/', views.grant_moderator_access, name='grant_moderator_access'),
    path('admin/event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('admin/moderator/<int:moderator_id>/edit/', views.moderator_edit, name='moderator_edit'),
    path('admin/moderator/create/', views.create_moderator, name='create_moderator'),
    path('admin/moderators/', views.view_all_moderators, name='view_all_moderators'),
    path('admin/users/', views.view_all_users, name='view_all_users'),
    path('admin/moderator/<int:moderator_id>/delete/', views.delete_moderator, name='delete_moderator'),
    path('admin/event/<int:event_id>/moderator-access/<int:access_id>/delete/', views.delete_moderator_access, name='delete_moderator_access'),

    # COMMENTED OUT HAVE NO VIEW YET
    #Moderaor CRUD URLs 
    # path('admin/moderator/list/', views.moderator_list, name='moderator_list'),
    # path('admin/moderator/create/', views.moderator_create, name='moderator_create'),
    # path('admin/moderator/<int:moderator_id>/edit/', views.moderator_edit, name='moderator_edit'),
    # path('admin/moderator/<int:moderator_id>/delete/', views.moderator_delete, name='moderator_delete'),

    #Review Management URLs
    path('admin/reviews/', views.review_list, name='review_list'),
    # path('admin/reviews/create/', views.review_create, name='review_create'),
    # path('admin/reviews/<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('admin/reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),

    #User Management URLs
    # path('admin/users/list/', views.user_list, name='user_list'),
    # path('admin/users/create/', views.user_create, name='user_create'),
    # path('admin/users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    # path('admin/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/create/', views.create_chat, name='create_chat'),
    path('chat/send-message/', views.send_message, name='send_message'),
]

