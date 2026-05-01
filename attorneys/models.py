from django.db import models
from django.contrib.auth.models import User


class AttorneyListing(models.Model):
    PLAN_CHOICES = [
        ('free',     'Free'),
        ('standard', 'Standard'),
        ('premium',  'Premium'),
    ]

    posted_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attorney_listings')
    name         = models.CharField(max_length=200)
    firm         = models.CharField(max_length=200, blank=True)
    location     = models.CharField(max_length=200)
    languages    = models.CharField(max_length=300, blank=True)
    specialty    = models.CharField(max_length=300, blank=True, help_text='e.g. H-1B, Asylum, Green Card')
    price        = models.CharField(max_length=200, blank=True, help_text='e.g. Free consult · $200/hr')
    description  = models.TextField(blank=True)
    plan         = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    home_country = models.CharField(max_length=100, blank=True)
    country_flag = models.CharField(max_length=10,  blank=True)
    posted_from  = models.CharField(max_length=200, blank=True)
    is_featured  = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.firm}'
