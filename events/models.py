from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('legal', 'Legal Aid'), ('jobs', 'Jobs Fair'), ('community', 'Community'),
        ('health', 'Health'), ('cultural', 'Cultural'), ('networking', 'Networking'),
    ]

    posted_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title       = models.CharField(max_length=200)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location    = models.CharField(max_length=200)
    date        = models.DateTimeField()
    description = models.TextField()
    is_free     = models.BooleanField(default=True)
    rsvp_count  = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.title} — {self.date.strftime("%b %d")}'
