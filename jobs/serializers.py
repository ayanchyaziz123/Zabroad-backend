from rest_framework import serializers
from .models import JobListing


class JobListingSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = JobListing
        fields = ['id', 'posted_by_name', 'title', 'company', 'location',
                  'description', 'visa_sponsorship', 'salary_range',
                  'apply_link', 'is_active', 'created_at']
        read_only_fields = ['created_at', 'posted_by_name']

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username
