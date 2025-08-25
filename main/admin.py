from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Event, EventHistory, Chat, Message

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_group_chat', 'created_at', 'updated_at')
    list_filter = ('is_group_chat', 'created_at')
    search_fields = ('name', 'participants__username')
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat', 'content_preview', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'chat')
    search_fields = ('content', 'sender__username', 'chat__name')
    readonly_fields = ('timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

# Custom User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'mobile', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'mobile')
    readonly_fields = ('date_joined', 'last_login', 'created_at')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'mobile', 'profile_picture')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )
    
    # Customize how mobile number is displayed
    def get_mobile_display(self, obj):
        if obj.mobile:
            return obj.mobile
        return '-'
    get_mobile_display.short_description = 'Phone Number'

# Register other models
# admin.site.register(Moderator)
admin.site.register(Event)
admin.site.register(EventHistory)
# admin.site.register(EventTracker)
# admin.site.register(ModeratorAccess)
