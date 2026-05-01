from django.db import models
from django.contrib.auth.models import User


class JobListing(models.Model):
    PLAN_CHOICES = [
        ('free',     'Free'),
        ('standard', 'Standard'),
        ('premium',  'Premium'),
    ]

    posted_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title        = models.CharField(max_length=200)
    company      = models.CharField(max_length=200)
    location     = models.CharField(max_length=200)
    description  = models.TextField()
    plan         = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    home_country = models.CharField(max_length=100, blank=True)   # poster's home country name
    country_flag = models.CharField(max_length=10,  blank=True)   # emoji flag
    posted_from  = models.CharField(max_length=200, blank=True)   # poster's current city/area
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_hot       = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} @ {self.company}'
