from django.contrib import admin
from .models import DoctorListing


@admin.register(DoctorListing)
class DoctorListingAdmin(admin.ModelAdmin):
    list_display    = ['name', 'specialty', 'location', 'plan', 'is_verified', 'accepts_medicaid', 'created_at']
    list_filter     = ['plan', 'is_verified', 'accepts_medicaid']
    search_fields   = ['name', 'specialty', 'location', 'user__email']
    readonly_fields = ['created_at']
    list_editable   = ['is_verified', 'plan']
