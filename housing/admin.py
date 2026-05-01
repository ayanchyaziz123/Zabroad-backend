from django.contrib import admin
from .models import HousingListing


@admin.register(HousingListing)
class HousingListingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'price', 'location', 'plan', 'home_country', 'is_featured', 'is_active', 'created_at')
    list_filter   = ('plan', 'is_featured', 'is_active', 'home_country')
    search_fields = ('title', 'location', 'home_country', 'posted_by__username')
    ordering      = ('-created_at',)
    list_editable = ('is_active',)
