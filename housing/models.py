from django.db import models
from django.contrib.auth.models import User


class HousingListing(models.Model):
    posted_by       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='housing')
    title           = models.CharField(max_length=200)
    location        = models.CharField(max_length=100)
    price           = models.PositiveIntegerField(help_text='Monthly rent in USD')
    description     = models.TextField()
    no_credit_check = models.BooleanField(default=False)
    accepts_itin    = models.BooleanField(default=False)
    bedrooms        = models.PositiveSmallIntegerField(default=1)
    available_from  = models.DateField(null=True, blank=True)
    contact         = models.CharField(max_length=200, blank=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — ${self.price}/mo'
