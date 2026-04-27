from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display    = ['title', 'category', 'location', 'date', 'is_free', 'rsvp_count', 'created_at']
    list_filter     = ['category', 'is_free']
    search_fields   = ['title', 'location', 'posted_by__email']
    readonly_fields = ['created_at', 'rsvp_count']
