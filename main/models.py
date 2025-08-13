from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime

# from djongo import models as djongo_models  # Uncomment if using Djongo

# ✅ Custom User Model
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

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# # ✅ Moderator
# class Moderator(models.Model):
#     user = models.OneToOneField('main.User', on_delete=models.CASCADE, related_name='moderator_profile')
#     bio = models.TextField(blank=True, null=True)
#     expertise_areas = models.JSONField(default=list, blank=True)
#     is_active = models.BooleanField(default=True)
#     rating = models.FloatField(default=0.0)
#     total_events_moderated = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     last_active = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = 'moderators'

#     def __str__(self):
#         return f"{self.user.get_full_name()} ({self.user.username})"

# ✅ Chat
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    is_group_chat = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chats'
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group_chat:
            return self.name or f"Group Chat {self.id}"
        return f"Chat between {', '.join([user.username for user in self.participants.all()[:2]])}"


# ✅ Message
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    attachment = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

     
class BookingRequest(models.Model):
    """
    A draft booking submitted by a client. Used to notify admins and
    kick off chat/confirmation workflows.
    """
    # -- Meta --
    created_at   = models.DateTimeField(default=timezone.now, editable=False)
    updated_at   = models.DateTimeField(auto_now=True)
    status_choices = [
        ("draft",     "Draft / Pending"),
        ("confirmed", "Confirmed"),
        ("rejected",  "Rejected"),
    ]
    status       = models.CharField(max_length=10, choices=status_choices, default="draft")

    # -- Who made the booking --
    client       = models.ForeignKey(User, on_delete=models.CASCADE)

    # -- Main fields --
    event_date   = models.DateField()
    event_type   = models.CharField(max_length=60)
    pax          = models.PositiveIntegerField()
    location     = models.CharField(max_length=255)
    color_hex    = models.CharField(max_length=7)  # e.g., "#ff0000"
    package      = models.CharField(max_length=40)

    # -- Menu (stored as plain strings) --
    dishes       = models.TextField(help_text="Comma-separated list of dishes")
    pasta        = models.CharField(max_length=60)
    drink        = models.CharField(max_length=60)

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name="request_booking")

    # -- Raw backup (optional) --
    raw_payload  = models.JSONField(blank=True, null=True)

    def dish_list(self):
        """Returns dishes as a Python list."""
        return [d.strip() for d in self.dishes.split(",") if d.strip()]

    def short_label(self):
        d = self.event_date
        if isinstance(d, str):  # fallback if string sneaks in
            try:
                d = datetime.fromisoformat(d).date()
            except ValueError:
                return f"{self.event_type} ({self.pax}pax)"
        return f"{d.strftime('%b %d, %Y')} • {self.event_type} ({self.pax}pax)"

    def __str__(self):
        return f"[{self.pk}] {self.short_label()}  {self.client.get_full_name()}"

    class Meta:
        db_table = 'booking_request'
        ordering = ("-created_at",)
        

class EventStatusLog(models.Model):
    class Label(models.TextChoices):
        BACKDROP = 'BACKDROP', 'Backdrop'
        PAYMENT = 'PAYMENT', 'Payment'
        LOGISTICS = 'LOGISTICS', 'Logistics'
        CATERING = 'CATERING', 'Catering'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        DONE = 'DONE', 'Done'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'

    booking = models.ForeignKey(
        'BookingRequest',
        on_delete=models.CASCADE,
        related_name='event_logs'
    )

    label = models.CharField(
        max_length=30,
        choices=Label.choices
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    total_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total amount due for payment (only set for PAYMENT label)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_status_log'
        unique_together = ('booking', 'label')  # Prevent duplicate log steps per booking

    def __str__(self):
        return f"{self.label} - {self.status} for booking {self.booking_id}"


class EventStatusAttachment(models.Model):
    """
    Holds multiple file attachments for a specific EventStatusLog entry.
    """

    booking = models.ForeignKey(
        'BookingRequest',
        on_delete=models.CASCADE,
        related_name='event_status_attachments'
    )

    status_log = models.ForeignKey(  
        'EventStatusLog',
        on_delete=models.CASCADE,
        related_name='attachments' 
    )

    file = models.FileField(upload_to='event_attachments/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'event_status_attachment'
        unique_together = ('booking', 'status_log', 'file') 

    def __str__(self):
        return f"Attachment for {self.status_log}"
    
# ✅ Event
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    # access_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    # checkin_code = models.CharField(max_length=8, unique=True, null=True, blank=True)
    # moderators = models.JSONField(default=list, blank=True)
    booking = models.ForeignKey(
        BookingRequest, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'

    def __str__(self):
        return self.title

    def clean(self):
        if self.date and self.date < timezone.now():
            raise ValidationError({'date': "Event date cannot be in the past."})

class PaymentTransaction(models.Model):
    status_log = models.ForeignKey(EventStatusLog, on_delete=models.CASCADE, related_name='payment_transactions')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_transaction'

    def __str__(self):
        return f"Payment {self.amount_paid} on {self.payment_date.strftime('%Y-%m-%d')} for Booking {self.booking_id}"

# ✅ EventHistory
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


# # ✅ EventTracker
# class EventTracker(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     username = models.CharField(max_length=150)
#     interaction_type = models.CharField(max_length=50)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     db_table = 'event_trackers'

    # def __str__(self):
    #     return f"{self.username} - {self.interaction_type} at {self.timestamp}"


# # ✅ ModeratorAccess
# class ModeratorAccess(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     moderator_username = models.CharField(max_length=150)
#     granted_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.moderator_username} - {self.event.title}"


# ✅ Review
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
        


# ✅ ActivityLog
class ActivityLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null  =True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    # moderator = models.ForeignKey(Moderator, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.action} by {self.user.username if self.user else "System"} at {self.timestamp.strftime("%Y-%m-%d %H:%M")}'
    from django.db import models



class MobilePost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mobile_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mobile_post'
        ordering = ['-created_at']
        verbose_name = 'Mobile Post'
        verbose_name_plural = 'Mobile Posts'

    def __str__(self):
        return self.title


class MobilePostImage(models.Model):
    post = models.ForeignKey(MobilePost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='mobile_posts/')

    class Meta:
        db_table = 'mobile_post_image'
        verbose_name = 'Mobile Post Image'
        verbose_name_plural = 'Mobile Post Images'

    def __str__(self):
        return f"Image for {self.post.title}"

class Comment(models.Model):
    post = models.ForeignKey(MobilePost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mobile_post_comments'


class Like(models.Model):
    post = models.ForeignKey(MobilePost, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'mobile_post_likes'
        unique_together = ('post', 'user')  
        
   