from rest_framework import serializers
from .models import Post, PostTopic, Comment


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PostTopic
        fields = ['topic']


class CommentSerializer(serializers.ModelSerializer):
    author_name   = serializers.SerializerMethodField()
    author_handle = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model  = Comment
        fields = ['id', 'author_name', 'author_handle', 'author_avatar', 'body', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def get_author_handle(self, obj):
        return getattr(obj.author, 'profile', None) and obj.author.profile.handle or ''

    def get_author_avatar(self, obj):
        return getattr(obj.author, 'profile', None) and obj.author.profile.avatar_emoji or '🧑‍💻'


class PostSerializer(serializers.ModelSerializer):
    topics        = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    topics_list   = serializers.SerializerMethodField()
    author_name   = serializers.SerializerMethodField()
    author_handle = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()
    author_country_flag = serializers.SerializerMethodField()
    likes_count   = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked      = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            'id', 'body', 'location', 'country', 'scope', 'is_anonymous',
            'author_name', 'author_handle', 'author_avatar', 'author_country_flag',
            'topics', 'topics_list',
            'likes_count', 'comments_count', 'is_liked',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def get_author_name(self, obj):
        if obj.is_anonymous:
            return 'Anonymous'
        return obj.author.get_full_name() or obj.author.username

    def get_author_handle(self, obj):
        if obj.is_anonymous:
            return None
        return getattr(obj.author, 'profile', None) and obj.author.profile.handle or ''

    def get_author_avatar(self, obj):
        if obj.is_anonymous:
            return '🕵️'
        return getattr(obj.author, 'profile', None) and obj.author.profile.avatar_emoji or '🧑‍💻'

    def get_author_country_flag(self, obj):
        return getattr(obj.author, 'profile', None) and obj.author.profile.country_flag or ''

    def get_topics_list(self, obj):
        return [t.topic for t in obj.topics.all()]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        topics = validated_data.pop('topics', [])
        post = Post.objects.create(**validated_data)
        for topic in topics:
            PostTopic.objects.create(post=post, topic=topic)
        return post
