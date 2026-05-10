# Django Local Shop Marketplace Model

from django.db import models
from django.contrib.auth.models import User


class LocalShop(models.Model):
    SHOP_TYPE_CHOICES = [
        ('grocery',      'Grocery Store'),
        ('restaurant',   'Restaurant'),
        ('electronics',  'Electronics'),
        ('fashion',      'Fashion & Clothing'),
        ('pharmacy',     'Pharmacy'),
        ('bookstore',    'Bookstore'),
        ('hardware',     'Hardware Store'),
        ('beauty',       'Beauty & Cosmetics'),
        ('services',     'Services'),
        ('other',        'Other'),
    ]

    owner         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    shop_name      = models.CharField(max_length=200)
    description    = models.TextField(blank=True)
    shop_type      = models.CharField(max_length=50, choices=SHOP_TYPE_CHOICES, default='other')

    # Contact Information
    phone_number   = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    website        = models.URLField(blank=True)

    # Location
    address        = models.CharField(max_length=255)
    city           = models.CharField(max_length=100)
    state          = models.CharField(max_length=100, blank=True)
    country        = models.CharField(max_length=100)
    postal_code    = models.CharField(max_length=20, blank=True)

    latitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Branding
    logo           = models.ImageField(upload_to='shops/logos/', null=True, blank=True)
    cover_image    = models.ImageField(upload_to='shops/covers/', null=True, blank=True)

    # Shop Status
    is_verified    = models.BooleanField(default=False, db_index=True)
    is_featured    = models.BooleanField(default=False, db_index=True)
    is_open        = models.BooleanField(default=True)
    is_active      = models.BooleanField(default=True, db_index=True)

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['shop_type', 'is_active']),
            models.Index(fields=['country', 'is_active']),
        ]

    def __str__(self):
        return self.shop_name


class ShopProduct(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('furniture',   'Furniture'),
        ('clothing',    'Clothing'),
        ('food',        'Food & Groceries'),
        ('beauty',      'Beauty Products'),
        ('books',       'Books'),
        ('services',    'Services'),
        ('other',       'Other'),
    ]

    shop           = models.ForeignKey(LocalShop, on_delete=models.CASCADE, related_name='products')
    title          = models.CharField(max_length=200)
    description    = models.TextField()
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    category       = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')

    stock_quantity = models.PositiveIntegerField(default=0)
    image          = models.ImageField(upload_to='shops/products/', null=True, blank=True)

    is_available   = models.BooleanField(default=True, db_index=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['shop', 'is_available']),
        ]

    def __str__(self):
        return f'{self.title} - {self.shop.shop_name}'
