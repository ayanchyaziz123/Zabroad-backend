from django.contrib import admin
from .models import HousingListing


@admin.register(HousingListing)
class HousingListingAdmin(admin.ModelAdmin):
    list_display    = ['title', 'location', 'price', 'bedrooms', 'no_credit_check', 'accepts_itin', 'is_active', 'created_at']
    list_filter     = ['no_credit_check', 'accepts_itin', 'is_active', 'bedrooms']
    search_fields   = ['title', 'location', 'posted_by__email']
    readonly_fields = ['created_at']
    list_editable   = ['is_active']
