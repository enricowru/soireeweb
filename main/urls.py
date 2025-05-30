from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),

    # ✅ Moderation Routes
    path('moderation/', views.review_moderation, name='review_moderation'),
    path('moderation/approve/<int:review_id>/', views.approve_review, name='approve_review'),
]
