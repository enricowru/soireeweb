from django.contrib import admin
from .models import User, Moderator, Event, EventHistory, EventTracker, ModeratorAccess, Chat, Message

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

# Register other models
admin.site.register(User)
admin.site.register(Moderator)
admin.site.register(Event)
admin.site.register(EventHistory)
admin.site.register(EventTracker)
admin.site.register(ModeratorAccess)
