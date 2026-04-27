from django.contrib import admin
from .models import OTPVerification, Profile


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display  = ['email', 'code', 'is_used', 'created_at']
    list_filter   = ['is_used']
    search_fields = ['email']
    readonly_fields = ['created_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ['handle', 'user', 'home_country', 'lives_in', 'visa_status', 'created_at']
    list_filter   = ['visa_status']
    search_fields = ['handle', 'user__email', 'user__first_name']
    readonly_fields = ['created_at']
