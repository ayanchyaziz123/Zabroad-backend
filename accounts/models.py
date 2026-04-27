from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random


class OTPVerification(models.Model):
    email      = models.EmailField()
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 600  # 10 min

    @classmethod
    def generate(cls, email):
        cls.objects.filter(email=email, is_used=False).update(is_used=True)
        code = str(random.randint(100000, 999999))
        return cls.objects.create(email=email, code=code)

    def __str__(self):
        return f'{self.email} — {self.code}'


class Profile(models.Model):
    VISA_CHOICES = [
        ('OPT', 'OPT'), ('CPT', 'CPT'), ('H1B', 'H-1B'), ('H4', 'H-4 EAD'),
        ('L1', 'L-1'), ('O1', 'O-1'), ('GC', 'Green Card'), ('CITIZEN', 'Citizen'),
        ('F1', 'F-1'), ('ASYLUM', 'Asylum'), ('OTHER', 'Other'),
    ]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    handle       = models.CharField(max_length=50, unique=True)
    avatar_emoji = models.CharField(max_length=10, default='🧑‍💻')
    home_country = models.CharField(max_length=100, default='Bangladesh')
    country_flag = models.CharField(max_length=10, default='🇧🇩')
    lives_in     = models.CharField(max_length=100, default='Queens, NY')
    visa_status  = models.CharField(max_length=20, choices=VISA_CHOICES, default='OPT')
    bio          = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.handle})'
