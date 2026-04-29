from django.contrib import admin
from .models import JobListing


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'company', 'location', 'plan', 'home_country', 'is_hot', 'is_active', 'created_at')
    list_filter   = ('plan', 'is_hot', 'is_active', 'home_country')
    search_fields = ('title', 'company', 'location', 'home_country', 'posted_by__username')
    ordering      = ('-created_at',)
    list_editable = ('is_active',)
