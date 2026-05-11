from django.db import models
from django.contrib.auth.models import User
from zabroad_backend.validators import validate_image_size, validate_image_type


class Post(models.Model):
    SCOPE_CHOICES = [
        ('local',   'Local'),
        ('country', 'My Country Community'),
        ('global',  'Global'),
    ]

    author       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    body         = models.TextField(max_length=500)
    location     = models.CharField(max_length=100, blank=True)   # GPS city, e.g. "Queens, NY"
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    country      = models.CharField(max_length=100, blank=True)   # author's home country, e.g. "Bangladesh"
    image        = models.ImageField(upload_to='posts/', null=True, blank=True, validators=[validate_image_size, validate_image_type])
    scope        = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='local')
    is_anonymous = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['country', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f'{self.author.username}: {self.body[:60]}'


class PostTopic(models.Model):
    post  = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='topics')
    topic = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.post_id} — {self.topic}'


class Like(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class SavedPost(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} saved post {self.post_id}'


class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body       = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} on post {self.post_id}'
