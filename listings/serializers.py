from rest_framework import serializers
from .models import Listing


class SavedListingSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    company   = serializers.SerializerMethodField()
    price     = serializers.SerializerMethodField()
    currency  = serializers.SerializerMethodField()

    class Meta:
        model  = Listing
        fields = [
            'id', 'listing_type', 'title', 'description', 'location',
            'category', 'is_boosted', 'created_at', 'updated_at',
            'latitude', 'longitude', 'image_url', 'company', 'price', 'currency',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_company(self, obj):
        try:
            return obj.job.company
        except Exception:
            return None

    def _get_detail(self, obj):
        for rel in ('housing', 'marketplace'):
            detail = getattr(obj, rel, None)
            if detail is not None:
                return detail
        event = getattr(obj, 'event_detail', None)
        if event is not None and not event.is_free:
            return event
        return None

    def get_price(self, obj):
        detail = self._get_detail(obj)
        return str(detail.price) if detail and detail.price is not None else None

    def get_currency(self, obj):
        detail = self._get_detail(obj)
        return detail.currency if detail else None
