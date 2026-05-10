from rest_framework import serializers
from .models import LocalShop, ShopProduct


class ShopProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image     = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model  = ShopProduct
        fields = [
            'id', 'shop', 'title', 'description', 'price', 'category',
            'stock_quantity', 'image', 'image_url', 'is_available', 'created_at',
        ]
        read_only_fields = ['id', 'shop', 'created_at']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class LocalShopSerializer(serializers.ModelSerializer):
    owner_name    = serializers.SerializerMethodField()
    owner_id      = serializers.SerializerMethodField()
    logo_url      = serializers.SerializerMethodField()
    cover_url     = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    logo          = serializers.ImageField(required=False, allow_null=True, write_only=True)
    cover_image   = serializers.ImageField(required=False, allow_null=True, write_only=True)
    is_mine       = serializers.SerializerMethodField()

    class Meta:
        model  = LocalShop
        fields = [
            'id', 'owner_id', 'owner_name',
            'shop_name', 'description', 'shop_type',
            'phone_number', 'email', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude',
            'logo', 'logo_url', 'cover_image', 'cover_url',
            'is_verified', 'is_featured', 'is_open', 'is_active',
            'product_count', 'is_mine',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner_id', 'owner_name', 'is_verified', 'is_featured', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username

    def get_owner_id(self, obj):
        return obj.owner_id

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url

    def get_cover_url(self, obj):
        if not obj.cover_image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url

    def get_product_count(self, obj):
        return obj.products.filter(is_available=True).count()

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.owner_id == request.user.id
        return False
