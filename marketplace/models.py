from django.db import models
from django.contrib.auth.models import User


class MarketplaceListing(models.Model):
    PLAN_CHOICES = [
        ('free',     'Free'),
        ('standard', 'Standard'),
        ('premium',  'Premium'),
    ]
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('furniture',   'Furniture'),
        ('clothing',    'Clothing & Accessories'),
        ('vehicles',    'Vehicles'),
        ('books',       'Books & Education'),
        ('services',    'Services'),
        ('food',        'Food & Groceries'),
        ('other',       'Other'),
    ]

    posted_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_listings')
    title        = models.CharField(max_length=200)
    description  = models.TextField()
    price        = models.CharField(max_length=50, blank=True)
    category     = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    location     = models.CharField(max_length=200, blank=True)
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    image        = models.ImageField(upload_to='marketplace/', null=True, blank=True)
    plan         = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    home_country = models.CharField(max_length=100, blank=True)
    country_flag = models.CharField(max_length=10,  blank=True)
    is_hot       = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.price}'
