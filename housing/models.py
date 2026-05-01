from django.db import models
from django.contrib.auth.models import User


class HousingListing(models.Model):
    PLAN_CHOICES = [
        ('free',     'Free'),
        ('standard', 'Standard'),
        ('premium',  'Premium'),
    ]

    posted_by       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='housing')
    title           = models.CharField(max_length=200)
    price           = models.CharField(max_length=50)          # e.g. "$1,450/mo"
    location        = models.CharField(max_length=200)
    description     = models.TextField()
    plan            = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    home_country    = models.CharField(max_length=100, blank=True)
    country_flag    = models.CharField(max_length=10,  blank=True)
    posted_from     = models.CharField(max_length=200, blank=True)
    latitude        = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_featured     = models.BooleanField(default=False)       # true for premium
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.price}'
