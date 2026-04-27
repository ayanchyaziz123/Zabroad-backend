from django.contrib import admin
from .models import JobListing


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display    = ['title', 'company', 'location', 'visa_sponsorship', 'is_active', 'created_at']
    list_filter     = ['visa_sponsorship', 'is_active']
    search_fields   = ['title', 'company', 'location', 'posted_by__email']
    readonly_fields = ['created_at']
    list_editable   = ['is_active']
