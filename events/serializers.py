from rest_framework import serializers
from listings.models import Listing, EventDetail, EventRSVP


class EventSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()
    posted_by_id   = serializers.SerializerMethodField()
    is_rsvped      = serializers.SerializerMethodField()
    image          = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url      = serializers.SerializerMethodField()

    # EventDetail fields
    date    = serializers.DateTimeField(source='event_detail.date')
    is_free = serializers.BooleanField(source='event_detail.is_free', default=True)
    price   = serializers.DecimalField(source='event_detail.price', max_digits=10, decimal_places=2, required=False, allow_null=True, default=None)
    link    = serializers.URLField(source='event_detail.link', required=False, allow_blank=True, default='')

    # Computed from EventDetail
    rsvp_count = serializers.SerializerMethodField()

    class Meta:
        model  = Listing
        fields = [
            'id', 'posted_by_name', 'posted_by_id', 'title', 'category',
            'location', 'latitude', 'longitude', 'date', 'description',
            'is_free', 'price', 'link', 'image', 'image_url', 'rsvp_count',
            'is_rsvped', 'created_at',
        ]
        read_only_fields = ['created_at', 'posted_by_name', 'posted_by_id', 'rsvp_count', 'is_rsvped', 'image_url']

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username

    def get_posted_by_id(self, obj):
        return obj.posted_by_id

    def get_rsvp_count(self, obj):
        if hasattr(obj, 'event_detail'):
            return obj.event_detail.rsvp_count
        return 0

    def get_is_rsvped(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and hasattr(obj, 'event_detail'):
            return obj.event_detail.rsvps.filter(user=request.user).exists()
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

    def create(self, validated_data):
        event_data = validated_data.pop('event_detail', {})
        # Coerce empty-string price to None so DecimalField doesn't blow up
        if event_data.get('price') == '':
            event_data['price'] = None
        validated_data['listing_type'] = Listing.TYPE_EVENT
        listing = Listing.objects.create(**validated_data)
        EventDetail.objects.create(listing=listing, **event_data)
        return listing

    def update(self, instance, validated_data):
        event_data = validated_data.pop('event_detail', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if event_data:
            ed = instance.event_detail
            for attr, value in event_data.items():
                setattr(ed, attr, value)
            ed.save()
        return instance
