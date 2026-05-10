from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()
    posted_by_id   = serializers.SerializerMethodField()
    is_rsvped      = serializers.SerializerMethodField()
    image_url      = serializers.SerializerMethodField()

    class Meta:
        model  = Event
        fields = [
            'id', 'posted_by_name', 'posted_by_id', 'title', 'category',
            'location', 'latitude', 'longitude', 'date', 'description',
            'is_free', 'price', 'link', 'image_url', 'rsvp_count',
            'is_rsvped', 'created_at',
        ]
        read_only_fields = ['created_at', 'posted_by_name', 'posted_by_id', 'rsvp_count', 'is_rsvped', 'image_url']

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username

    def get_posted_by_id(self, obj):
        return obj.posted_by_id

    def get_is_rsvped(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.rsvps.filter(user=request.user).exists()
        return False

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        from django.conf import settings
        base = getattr(settings, 'SITE_URL', '').rstrip('/')
        return f"{base}{obj.image.url}"
