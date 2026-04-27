from django.contrib import admin
from .models import AttorneyListing


@admin.register(AttorneyListing)
class AttorneyListingAdmin(admin.ModelAdmin):
    list_display    = ['name', 'firm', 'location', 'visa_types', 'plan', 'is_verified', 'free_consult', 'created_at']
    list_filter     = ['plan', 'is_verified', 'free_consult']
    search_fields   = ['name', 'firm', 'location', 'visa_types', 'user__email']
    readonly_fields = ['created_at']
    list_editable   = ['is_verified', 'plan']
