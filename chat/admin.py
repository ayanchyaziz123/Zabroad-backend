from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display  = ('id', 'created_at')
    filter_horizontal = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('sender', 'conversation', 'text', 'is_read', 'created_at')
    list_filter   = ('is_read',)
    search_fields = ('sender__username', 'text')
