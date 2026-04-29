from rest_framework import serializers
from .models import JobListing


class JobListingSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()

    class Meta:
        model  = JobListing
        fields = [
            'id', 'poster', 'title', 'company', 'location',
            'description', 'plan', 'home_country', 'country_flag',
            'posted_from', 'is_hot', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at', 'poster', 'is_hot']

    def get_poster(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username

    def create(self, validated_data):
        # auto-set is_hot based on plan
        validated_data['is_hot'] = validated_data.get('plan') == 'premium'
        return super().create(validated_data)
