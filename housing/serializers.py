from rest_framework import serializers
from .models import HousingListing


class HousingListingSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = HousingListing
        fields = ['id', 'posted_by_name', 'title', 'location', 'price',
                  'description', 'no_credit_check', 'accepts_itin',
                  'bedrooms', 'available_from', 'contact', 'is_active', 'created_at']
        read_only_fields = ['created_at', 'posted_by_name']

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username
