import re
from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from listings.models import Listing, HousingDetail


class HousingListingSerializer(serializers.ModelSerializer):
    poster      = serializers.SerializerMethodField()
    poster_id   = serializers.SerializerMethodField()
    image       = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url   = serializers.SerializerMethodField()
    is_featured = serializers.BooleanField(source='is_boosted', read_only=True)

    # HousingDetail fields
    price       = serializers.CharField(source='housing.price', max_length=50)
    posted_from = serializers.CharField(source='housing.posted_from', max_length=200, required=False, allow_blank=True, default='')

    class Meta:
        model  = Listing
        fields = [
            'id', 'poster', 'poster_id',
            'title', 'price', 'location', 'category',
            'latitude', 'longitude',
            'description', 'plan', 'home_country', 'country_flag',
            'posted_from', 'image', 'image_url',
            'is_featured', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at', 'poster', 'poster_id', 'is_featured', 'is_active']

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
        if len(v) < 20:
            raise serializers.ValidationError('Description must be at least 20 characters.')
        return v

    def validate_location(self, value):
        v = value.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Location must be at least 2 characters.')
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
        housing_data = validated_data.pop('housing', {})
        validated_data['listing_type'] = Listing.TYPE_HOUSING
        validated_data['is_boosted']   = validated_data.get('plan') == 'premium'
        listing = Listing.objects.create(**validated_data)
        HousingDetail.objects.create(listing=listing, **housing_data)
        return listing

    def update(self, instance, validated_data):
        housing_data = validated_data.pop('housing', {})
        if 'plan' in validated_data:
            validated_data['is_boosted'] = validated_data['plan'] == 'premium'
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if housing_data:
            housing = instance.housing
            for attr, value in housing_data.items():
                setattr(housing, attr, value)
            housing.save()
        return instance
