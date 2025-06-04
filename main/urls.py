from . import chatbot_urls
from django.urls import path, include
from . import views
from . import chatbot_views
from .views import signup

urlpatterns = [
    path('chatbot/', include(chatbot_urls.urlpatterns)),
    path('', include('main.urls')),
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

    #Moderator URLs
    path('moderator/', views.moderator_access, name='moderator'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('admin/event/create/', views.create_event, name='create_event'),
    path('admin/event/<int:event_id>/grant-access/', views.grant_moderator_access, name='grant_moderator_access'),
    path('admin/event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('admin/moderator/create/', views.create_moderator, name='create_moderator'),
    path('admin/moderators/', views.view_all_moderators, name='view_all_moderators'),
    path('admin/users/', views.view_all_users, name='view_all_users'),
    path('admin/moderator/<int:moderator_id>/delete/', views.delete_moderator, name='delete_moderator'),
    path('admin/event/<int:event_id>/moderator-access/<int:access_id>/delete/', views.delete_moderator_access, name='delete_moderator_access'),

    #Moderaor CRUD URLs
    path('admin/moderator/list/', views.moderator_list, name='moderator_list'),
    path('admin/moderator/create/', views.moderator_create, name='moderator_create'),
    path('admin/moderator/<int:moderator_id>/edit/', views.moderator_edit, name='moderator_edit'),
    path('admin/moderator/<int:moderator_id>/delete/', views.moderator_delete, name='moderator_delete'),

    #Review Management URLs
    path('admin/reviews/', views.review_list, name='review_list'),
    path('admin/reviews/create/', views.review_create, name='review_create'),
    path('admin/reviews/<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('admin/reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),

    #User Management URLs
    path('admin/users/list/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('admin/users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
]

