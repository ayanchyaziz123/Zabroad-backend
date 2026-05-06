from rest_framework import serializers
from .models import JobListing


class JobListingSerializer(serializers.ModelSerializer):
    poster    = serializers.SerializerMethodField()
    poster_id = serializers.SerializerMethodField()
    image     = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = JobListing
        fields = [
            'id', 'poster', 'poster_id',
            'title', 'company', 'location', 'category',
            'latitude', 'longitude',
            'description', 'plan', 'home_country', 'country_flag',
            'posted_from', 'image', 'image_url',
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

    def validate_location(self, value):
        v = value.strip()
        if len(v) < 2:
            raise serializers.ValidationError('Location must be at least 2 characters.')
        return v

    def create(self, validated_data):
        validated_data['is_hot'] = validated_data.get('plan') == 'premium'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'plan' in validated_data:
            validated_data['is_hot'] = validated_data['plan'] == 'premium'
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
