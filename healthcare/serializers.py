from rest_framework import serializers
from .models import DoctorListing


class DoctorListingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DoctorListing
        fields = ['id', 'name', 'specialty', 'location', 'languages',
                  'bio', 'phone', 'website', 'accepts_medicaid',
                  'plan', 'is_verified', 'created_at']
        read_only_fields = ['created_at', 'is_verified']
