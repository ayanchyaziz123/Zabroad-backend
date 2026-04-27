from rest_framework import serializers
from .models import AttorneyListing


class AttorneyListingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AttorneyListing
        fields = ['id', 'name', 'firm', 'location', 'languages',
                  'visa_types', 'bio', 'phone', 'website',
                  'free_consult', 'plan', 'is_verified', 'created_at']
        read_only_fields = ['created_at', 'is_verified']
