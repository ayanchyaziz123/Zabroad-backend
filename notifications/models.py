from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like',     'Like'),
        ('comment',  'Comment'),
        ('message',  'Message'),
        ('system',   'System'),
        ('job',      'Job'),
        ('housing',  'Housing'),
        ('attorney', 'Attorney'),
        ('event',    'Event'),
    ]

    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    title      = models.CharField(max_length=200)
    body       = models.CharField(max_length=500)
    post_id    = models.PositiveIntegerField(null=True, blank=True)  # for deep-link to post
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.type}] → {self.recipient.username}: {self.title}'
