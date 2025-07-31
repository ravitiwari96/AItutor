from django.contrib import admin
from .models import AIChat

@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'message_preview']
    list_filter = ['created_at']
    search_fields = ['user__email', 'message', 'ai_response']
    readonly_fields = ['created_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Conversation', {
            'fields': ('message', 'ai_response')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
