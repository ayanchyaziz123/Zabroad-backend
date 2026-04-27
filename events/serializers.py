from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = Event
        fields = ['id', 'posted_by_name', 'title', 'category', 'location',
                  'date', 'description', 'is_free', 'rsvp_count', 'created_at']
        read_only_fields = ['created_at', 'posted_by_name', 'rsvp_count']

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username
