from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/edit/', views.admin_edit, name='admin_edit'),

    # Event Management
    path('event/history/', views.event_history, name='event_history'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('event/<int:event_id>/grant-access/', views.grant_moderator_access, name='grant_moderator_access'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:event_id>/moderator-access/<int:access_id>/delete/', views.delete_moderator_access, name='delete_moderator_access'),

    # Moderator Management
    path('moderators/', views.view_all_moderators, name='view_all_moderators'),
    path('moderator/create/', views.create_moderator, name='create_moderator'),
    path('moderator/<int:moderator_id>/edit/', views.moderator_edit, name='moderator_edit'),
    path('moderator/<int:moderator_id>/delete/', views.delete_moderator, name='delete_moderator'),
    
    path('users/', views.view_all_users, name='view_all_users'),
    
    # Post Management
    # Mobile Posts CRUD (ADMIN only)
    path('mobile-posts/', views.mobile_post_list, name='mobile_post_list'),
    path('mobile-posts/create/', views.mobile_post_create, name='mobile_post_create'),
    path('mobile-posts/<int:post_id>/', views.mobile_post_detail, name='mobile_post_detail'),
    path('mobile-posts/<int:post_id>/edit/', views.mobile_post_edit, name='mobile_post_edit'),
    path('mobile-posts/<int:post_id>/delete/', views.mobile_post_delete, name='mobile_post_delete'),
    
    # COMMENTED OUT HAVE NO VIEW YET
    # Review Management URLs
    # path('reviews/create/', views.review_create, name='review_create'),
    # path('reviews/<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),
     path("bookings/stream/", views.booking_notifications, name="booking_stream"),
    # User Management URLs
    # path('users/list/', views.user_list, name='user_list'),
    # path('users/create/', views.user_create, name='user_create'),
    # path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    # path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
        
    # Moderaor CRUD URLs 
    # path('moderator/list/', views.moderator_list, name='moderator_list'),
    # path('moderator/create/', views.moderator_create, name='moderator_create'),
    # path('moderator/<int:moderator_id>/edit/', views.moderator_edit, name='moderator_edit'),
    # path('moderator/<int:moderator_id>/delete/', views.moderator_delete, name='moderator_delete'),

]
