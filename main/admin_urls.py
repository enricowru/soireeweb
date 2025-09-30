from django.urls import path
from . import views
from .views.admin import send_notification_to_user_view, send_notification_to_all_users_view
from .views import reviews as reviews_views
from .views import email_debug_views
from .views.quick_email_check import quick_email_config_check

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/edit/', views.admin_edit, name='admin_edit'),

    # Event Management
    path('event/history/', views.event_history, name='event_history'),
    path('event/history/export-csv/', views.export_event_history_csv, name='export_event_history_csv'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    # path('event/<int:event_id>/grant-access/', views.grant_moderator_access, name='grant_moderator_access'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    # path('event/<int:event_id>/moderator-access/<int:access_id>/delete/', views.delete_moderator_access, name='delete_moderator_access'),

    # Moderator Management
    # path('moderators/', views.view_all_moderators, name='view_all_moderators'),
    # path('moderator/create/', views.create_moderator, name='create_moderator'),
    # path('moderator/<int:moderator_id>/edit/', views.moderator_edit, name='moderator_edit'),
    # path('moderator/<int:moderator_id>/delete/', views.delete_moderator, name='delete_moderator'),
    
    path('users/', views.view_all_users, name='view_all_users'),
    path('users/export-csv/', views.export_users_csv, name='export_users_csv'),
    
    # Post Management
    path('mobile-posts/', views.mobile_post_list, name='mobile_post_list'),
    path('mobile-posts/create/', views.mobile_post_create, name='mobile_post_create'),
    path('mobile-posts/<int:post_id>/', views.mobile_post_detail, name='mobile_post_detail'),
    path('mobile-posts/<int:post_id>/edit/', views.mobile_post_edit, name='mobile_post_edit'),
    path('mobile-posts/<int:post_id>/delete/', views.mobile_post_delete, name='mobile_post_delete'),
    
    # COMMENTED OUT HAVE NO VIEW YET
    # Review Management URLs
    # path('reviews/create/', views.review_create, name='review_create'),
    # path('reviews/<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('load-chats/', views.admin_booking_list, name="load-chats"),
    path('reviews/', reviews_views.review_list, name='review_list'),
    path('reviews/<int:review_id>/', reviews_views.review_detail, name='review_detail'),
    path('reviews/<int:review_id>/bookmark/', reviews_views.review_bookmark_toggle, name='review_bookmark_toggle'),
    path('bookmark-count/', reviews_views.bookmark_count, name='bookmark_count'),
    path('reviews/<int:review_id>/approve/', reviews_views.review_approve, name='review_approve'),
    path('reviews/<int:review_id>/delete/', reviews_views.review_delete, name='review_delete'),
    path("bookings/stream/", views.booking_notifications, name="booking_stream"),
    path("request-bookings/", views.booking_requests, name = "request_bookings"),
    path("request-bookings/status/<int:id>", views.booking_requests_status, name = "booking_request_status"),
    
    # Email Debug Endpoints (Admin Only)
    path('debug/email/diagnosis/', email_debug_views.email_diagnosis_view, name='email_diagnosis'),
    path('debug/email/test/', email_debug_views.test_email_view, name='test_email'),
    path('debug/email/network/', email_debug_views.network_test_view, name='network_test'),
    path('debug/email/quick-check/', quick_email_config_check, name='quick_email_check'),
    
    path("request-bookings/status/<int:id>/mark-as-done", views.mark_step_done, name ="mark_step_done"),
    path("request-bookings/status/<int:id>/undo-step", views.undo_step, name ="undo_step"),
    
    # Notification Management URLs
    path('notifications/', views.admin_notifications, name='admin_notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-booking-read/', views.mark_booking_notifications_read, name='mark_booking_notifications_read'),
    path('notifications/stream/', views.admin_notifications_stream, name='admin_notifications_stream'),
    
    # User Notification Management URLs (Admin sends to users)
    path('send-notification/user/', send_notification_to_user_view, name='send_notification_to_user'),
    path('send-notification/all-users/', send_notification_to_all_users_view, name='send_notification_to_all_users'),
    
    # Booking Details API
    path('api/booking/<int:booking_id>/details/', views.booking_details_api, name='booking_details_api'),
    
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
