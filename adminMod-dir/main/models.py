from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from djongo import models as djongo_models
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    mobile = models.CharField(
        max_length=11,
        validators=[RegexValidator(regex=r'^09\d{9}$', message='Mobile number must be 11 digits and start with 09')],
        blank=True,
        null=True
    )
    profile_picture = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

class Moderator(models.Model):
    user = models.OneToOneField('main.User', on_delete=models.CASCADE, related_name='moderator_profile')
    bio = models.TextField(blank=True, null=True)
    expertise_areas = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    total_events_moderated = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'moderators'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    checkin_code = models.CharField(max_length=8, unique=True, null=True, blank=True)
    moderators = models.JSONField(default=list, blank=True)
    participants = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'events'

    def __str__(self):
        return self.title

    def clean(self):
        # Check if the event date is in the past
        if self.date and self.date < timezone.now():
            raise ValidationError({'date': "Event date cannot be in the past."})

class EventHistory(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    access_code = models.CharField(max_length=6, null=True, blank=True)
    checkin_code = models.CharField(max_length=8, null=True, blank=True)
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ForeignKey('main.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Deleted: {self.title}"

class EventTracker(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    interaction_type = models.CharField(max_length=50)  # e.g., 'checkin', 'comment'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'event_trackers'

    def __str__(self):
        return f"{self.username} - {self.interaction_type} at {self.timestamp}"

class ModeratorAccess(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    moderator_username = models.CharField(max_length=150)
    granted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.moderator_username} - {self.event.title}"

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group_chat = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'chats'
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group_chat:
            return self.name or f"Group Chat {self.id}"
        return f"Chat between {', '.join([user.username for user in self.participants.all()[:2]])}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachment = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.event.title}"

class ActivityLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    moderator = models.ForeignKey(Moderator, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.action} by {self.user.username if self.user else "System"} at {self.timestamp.strftime("%Y-%m-%d %H:%M")}'
