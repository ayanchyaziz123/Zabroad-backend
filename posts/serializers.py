from rest_framework import serializers
from .models import Post, PostTopic, Comment


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PostTopic
        fields = ['topic']


class CommentSerializer(serializers.ModelSerializer):
    author_name       = serializers.SerializerMethodField()
    author_handle     = serializers.SerializerMethodField()
    author_avatar     = serializers.SerializerMethodField()
    author_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = Comment
        fields = ['id', 'author_name', 'author_handle', 'author_avatar', 'author_avatar_url', 'body', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username

    def get_author_handle(self, obj):
        return getattr(obj.author, 'profile', None) and obj.author.profile.handle or ''

    def get_author_avatar(self, obj):
        return getattr(obj.author, 'profile', None) and obj.author.profile.avatar_emoji or '🧑‍💻'

    def get_author_avatar_url(self, obj):
        profile = getattr(obj.author, 'profile', None)
        if not profile or not profile.avatar:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(profile.avatar.url) if request else profile.avatar.url


class PostSerializer(serializers.ModelSerializer):
    topics        = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    topics_list   = serializers.SerializerMethodField()
    author_name       = serializers.SerializerMethodField()
    author_handle     = serializers.SerializerMethodField()
    author_avatar     = serializers.SerializerMethodField()
    author_avatar_url = serializers.SerializerMethodField()
    author_country_flag = serializers.SerializerMethodField()
    author_id     = serializers.SerializerMethodField()
    likes_count   = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked      = serializers.SerializerMethodField()
    is_saved      = serializers.SerializerMethodField()
    image         = serializers.ImageField(required=False, allow_null=True, write_only=True)
    image_url     = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            'id', 'body', 'location', 'latitude', 'longitude', 'country', 'scope', 'is_anonymous',
            'image', 'image_url',
            'author_id', 'author_name', 'author_handle', 'author_avatar', 'author_avatar_url', 'author_country_flag',
            'topics', 'topics_list',
            'likes_count', 'comments_count', 'is_liked', 'is_saved',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Never expose precise coordinates on anonymous posts — they could de-anonymize the author.
        if instance.is_anonymous:
            data['latitude']  = None
            data['longitude'] = None
            data['location']  = ''
        return data

    def get_author_id(self, obj):
        return None if obj.is_anonymous else obj.author_id

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

    def get_author_avatar_url(self, obj):
        if obj.is_anonymous:
            return None
        profile = getattr(obj.author, 'profile', None)
        if not profile or not profile.avatar:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(profile.avatar.url) if request else profile.avatar.url

    def get_author_country_flag(self, obj):
        return getattr(obj.author, 'profile', None) and obj.author.profile.country_flag or ''

    def get_topics_list(self, obj):
        return [t.topic for t in obj.topics.all()]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saves.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        topics = validated_data.pop('topics', [])
        post = Post.objects.create(**validated_data)
        for topic in topics:
            PostTopic.objects.create(post=post, topic=topic)
        return post

    def update(self, instance, validated_data):
        topics = validated_data.pop('topics', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if topics is not None:
            instance.topics.all().delete()
            for topic in topics:
                PostTopic.objects.create(post=instance, topic=topic)
        return instance
