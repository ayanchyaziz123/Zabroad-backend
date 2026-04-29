from rest_framework import serializers
from .models import HousingListing


class HousingListingSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()

    class Meta:
        model  = HousingListing
        fields = [
            'id', 'poster', 'title', 'price', 'location',
            'description', 'plan', 'home_country', 'country_flag',
            'posted_from', 'is_featured', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at', 'poster', 'is_featured']

    def get_poster(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username

    def create(self, validated_data):
        validated_data['is_featured'] = validated_data.get('plan') == 'premium'
        return super().create(validated_data)
