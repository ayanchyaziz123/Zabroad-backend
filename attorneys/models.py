from django.db import models
from django.contrib.auth.models import User


class AttorneyListing(models.Model):
    PLAN_CHOICES = [('free', 'Free'), ('pro', 'Pro'), ('premium', 'Premium')]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='attorney_profile')
    name         = models.CharField(max_length=200)
    firm         = models.CharField(max_length=200, blank=True)
    location     = models.CharField(max_length=200)
    languages    = models.CharField(max_length=300)
    visa_types   = models.CharField(max_length=300, help_text='e.g. H-1B, Asylum, Green Card')
    bio          = models.TextField(blank=True)
    phone        = models.CharField(max_length=30, blank=True)
    website      = models.URLField(blank=True)
    free_consult = models.BooleanField(default=False)
    plan         = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    is_verified  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-plan', '-created_at']

    def __str__(self):
        return f'{self.name} — {self.visa_types}'
