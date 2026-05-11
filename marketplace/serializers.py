import re
from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from listings.models import Listing, MarketplaceDetail


class MarketplaceListingSerializer(serializers.ModelSerializer):
    poster    = serializers.SerializerMethodField()
    poster_id = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    image     = serializers.ImageField(required=False, allow_null=True, write_only=True)
    is_hot    = serializers.BooleanField(source='is_boosted', read_only=True)

    # MarketplaceDetail fields
    price = serializers.CharField(source='marketplace.price', max_length=50, required=False, allow_blank=True, default='')

    class Meta:
        model  = Listing
        fields = [
            'id', 'poster', 'poster_id',
            'title', 'description', 'price', 'category',
            'location', 'latitude', 'longitude',
            'image', 'image_url',
            'plan', 'home_country', 'country_flag',
            'is_hot', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at', 'poster', 'poster_id', 'is_hot', 'is_active']

    def get_poster(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username

    def get_poster_id(self, obj):
        return obj.posted_by_id

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

    def validate_title(self, value):
        v = value.strip()
        if len(v) < 3:
            raise serializers.ValidationError('Title must be at least 3 characters.')
        return v

    def validate_description(self, value):
        v = value.strip()
        if len(v) < 10:
            raise serializers.ValidationError('Description must be at least 10 characters.')
        return v

    def validate_price(self, value):
        if not value or str(value).strip() == '':
            return None
        cleaned = re.sub(r'[^\d.]', '', str(value))
        if not cleaned:
            return None
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None

    def create(self, validated_data):
        marketplace_data = validated_data.pop('marketplace', {})
        validated_data['listing_type'] = Listing.TYPE_MARKETPLACE
        validated_data['is_boosted']   = validated_data.get('plan') == 'premium'
        listing = Listing.objects.create(**validated_data)
        MarketplaceDetail.objects.create(listing=listing, **marketplace_data)
        return listing

    def update(self, instance, validated_data):
        marketplace_data = validated_data.pop('marketplace', {})
        if 'plan' in validated_data:
            validated_data['is_boosted'] = validated_data['plan'] == 'premium'
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if marketplace_data:
            mp = instance.marketplace
            for attr, value in marketplace_data.items():
                setattr(mp, attr, value)
            mp.save()
        return instance
