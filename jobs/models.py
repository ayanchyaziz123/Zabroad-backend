from django.db import models
from django.contrib.auth.models import User


class JobListing(models.Model):
    VISA_SPONSORSHIP = [('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')]

    posted_by        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title            = models.CharField(max_length=200)
    company          = models.CharField(max_length=200)
    location         = models.CharField(max_length=100)
    description      = models.TextField()
    visa_sponsorship = models.CharField(max_length=10, choices=VISA_SPONSORSHIP, default='no')
    salary_range     = models.CharField(max_length=100, blank=True)
    apply_link       = models.URLField(blank=True)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} @ {self.company}'
