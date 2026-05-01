from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'full_name', 'username']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class MessageSerializer(serializers.ModelSerializer):
    sender_name       = serializers.SerializerMethodField()
    sender_id         = serializers.IntegerField(source='sender.id', read_only=True)
    sender_avatar_url = serializers.SerializerMethodField()
    media_url         = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ['id', 'sender_id', 'sender_name', 'sender_avatar_url',
                  'text', 'media', 'media_url', 'is_read', 'created_at']
        read_only_fields = ['sender_id', 'sender_name', 'sender_avatar_url', 'is_read', 'created_at', 'media_url']
        extra_kwargs = {'media': {'write_only': True, 'required': False}}

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username

    def get_sender_avatar_url(self, obj):
        request = self.context.get('request')
        try:
            avatar = obj.sender.profile.avatar
            if avatar:
                return request.build_absolute_uri(avatar.url) if request else avatar.url
        except Exception:
            pass
        return None

    def get_media_url(self, obj):
        if not obj.media:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.media.url) if request else obj.media.url

    def validate(self, data):
        if not data.get('text') and not data.get('media'):
            raise serializers.ValidationError('A message must have text or media.')
        return data


class ConversationSerializer(serializers.ModelSerializer):
    participants  = UserBriefSerializer(many=True, read_only=True)
    last_message  = serializers.SerializerMethodField()
    unread_count  = serializers.SerializerMethodField()
    other_user    = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ['id', 'participants', 'other_user', 'last_message', 'unread_count', 'created_at']

    def get_last_message(self, obj):
        msg = obj.last_message
        if not msg:
            return None
        return {
            'text':       msg.text,
            'has_media':  bool(msg.media),
            'created_at': msg.created_at,
            'sender_id':  msg.sender_id,
        }

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()

    def get_other_user(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        other = obj.participants.exclude(id=request.user.id).first()
        if not other:
            return None
        avatar_url = None
        try:
            avatar = other.profile.avatar
            if avatar:
                avatar_url = request.build_absolute_uri(avatar.url)
        except Exception:
            pass
        return {
            'id':         other.id,
            'name':       other.get_full_name() or other.username,
            'username':   other.username,
            'avatar_url': avatar_url,
        }
