from django.db import models
from django.contrib.auth.models import User
from zabroad_backend.validators import validate_image_size, validate_image_type


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        names = ', '.join(u.get_full_name() or u.username for u in self.participants.all())
        return f'Conversation: {names}'

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text         = models.TextField(blank=True, default='')
    media        = models.ImageField(upload_to='chat/media/', null=True, blank=True, validators=[validate_image_size, validate_image_type])
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.text[:60] or "[media]"}'
