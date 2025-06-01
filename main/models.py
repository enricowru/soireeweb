from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # ✅ Needed for moderation

    def __str__(self):
        return f"{self.user.username} - {self.content[:30]}"

# Create your models here.

class Theme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='themes/')
    keywords = models.CharField(max_length=255, help_text="Comma-separated keywords that trigger this theme")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class ChatSession(models.Model):
    title = models.CharField(max_length=100)
    chat_history = models.JSONField(default=list)
    planner_state = models.CharField(max_length=50, default='start')
    planner_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']