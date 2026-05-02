from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender_name   = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()

    class Meta:
        model  = Notification
        fields = [
            'id', 'type', 'title', 'body',
            'sender_name', 'sender_avatar',
            'post_id', 'is_read', 'created_at',
        ]
        read_only_fields = ['id', 'type', 'title', 'body', 'sender_name',
                            'sender_avatar', 'post_id', 'created_at']

    def get_sender_name(self, obj):
        if not obj.sender:
            return 'Zabroad'
        return obj.sender.get_full_name() or obj.sender.username

    def get_sender_avatar(self, obj):
        if not obj.sender:
            return '🔔'
        return getattr(obj.sender, 'profile', None) and obj.sender.profile.avatar_emoji or '🧑‍💻'
