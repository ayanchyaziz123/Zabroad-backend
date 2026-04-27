from django.db import models
from django.contrib.auth.models import User


class DoctorListing(models.Model):
    PLAN_CHOICES = [('free', 'Free'), ('pro', 'Pro'), ('premium', 'Premium')]

    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    name             = models.CharField(max_length=200)
    specialty        = models.CharField(max_length=200)
    location         = models.CharField(max_length=200)
    languages        = models.CharField(max_length=300, help_text='Comma-separated list of languages')
    bio              = models.TextField(blank=True)
    phone            = models.CharField(max_length=30, blank=True)
    website          = models.URLField(blank=True)
    accepts_medicaid = models.BooleanField(default=False)
    plan             = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    is_verified      = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-plan', '-created_at']

    def __str__(self):
        return f'Dr. {self.name} — {self.specialty}'
