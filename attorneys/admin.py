from django.contrib import admin
from .models import AttorneyListing


@admin.register(AttorneyListing)
class AttorneyListingAdmin(admin.ModelAdmin):
    list_display  = ('name', 'firm', 'location', 'plan', 'home_country', 'is_featured', 'is_active', 'created_at')
    list_filter   = ('plan', 'is_featured', 'is_active', 'home_country')
    search_fields = ('name', 'firm', 'location', 'home_country', 'posted_by__username')
    ordering      = ('-created_at',)
    list_editable = ('is_active',)
