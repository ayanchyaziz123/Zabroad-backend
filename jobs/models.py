from django.db import models
from django.contrib.auth.models import User


class JobListing(models.Model):
    PLAN_CHOICES = [
        ('free',     'Free'),
        ('standard', 'Standard'),
        ('premium',  'Premium'),
    ]
    CATEGORY_CHOICES = [
        ('tech',         'Technology'),
        ('healthcare',   'Healthcare'),
        ('hospitality',  'Hospitality'),
        ('retail',       'Retail'),
        ('construction', 'Construction'),
        ('education',    'Education'),
        ('finance',      'Finance'),
        ('transport',    'Transport'),
        ('legal',        'Legal'),
        ('other',        'Other'),
    ]

    posted_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title        = models.CharField(max_length=200)
    company      = models.CharField(max_length=200)
    location     = models.CharField(max_length=200)
    description  = models.TextField()
    category     = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    plan         = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    home_country = models.CharField(max_length=100, blank=True, db_index=True)
    country_flag = models.CharField(max_length=10,  blank=True)
    posted_from  = models.CharField(max_length=200, blank=True)
    image        = models.ImageField(upload_to='jobs/', null=True, blank=True)
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_hot       = models.BooleanField(default=False, db_index=True)
    is_active    = models.BooleanField(default=True,  db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['home_country', 'is_active']),
        ]

    def __str__(self):
        return f'{self.title} @ {self.company}'
