from django.urls import path
from . import moderator_views as views

urlpatterns = [
    path('moderator/login/', views.login_view, name='login'),
    path('moderator/access/', views.moderator_access, name='moderator-access'),
    path('moderator/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('moderator/event/<int:event_id>/', views.event_detail, name='event-detail'),
    path('moderator/event/create/', views.create_event, name='create-event'),
    path('moderator/reviews/', views.review_list, name='review-list'),
    path('logout/', views.logout_view, name='logout'),
]
