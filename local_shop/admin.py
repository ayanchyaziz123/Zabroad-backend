from django.contrib import admin
from .models import LocalShop, ShopProduct


class ShopProductInline(admin.TabularInline):
    model  = ShopProduct
    extra  = 0
    fields = ['title', 'price', 'category', 'stock_quantity', 'is_available']


@admin.register(LocalShop)
class LocalShopAdmin(admin.ModelAdmin):
    list_display   = ['shop_name', 'owner', 'shop_type', 'city', 'is_open', 'is_verified', 'is_active', 'created_at']
    list_filter    = ['shop_type', 'is_verified', 'is_featured', 'is_open', 'is_active']
    search_fields  = ['shop_name', 'owner__username', 'city', 'address']
    list_editable  = ['is_open', 'is_verified', 'is_active']
    inlines        = [ShopProductInline]


@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display  = ['title', 'shop', 'price', 'category', 'stock_quantity', 'is_available']
    list_filter   = ['category', 'is_available']
    search_fields = ['title', 'shop__shop_name']
