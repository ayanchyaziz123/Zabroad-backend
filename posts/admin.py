from django.contrib import admin
from .models import Post, PostTopic, Like, Comment


class PostTopicInline(admin.TabularInline):
    model = PostTopic
    extra = 1


class CommentInline(admin.TabularInline):
    model           = Comment
    extra           = 0
    readonly_fields = ['author', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display    = ['id', 'author', 'scope', 'is_anonymous', 'likes_count', 'comments_count', 'created_at']
    list_filter     = ['scope', 'is_anonymous']
    search_fields   = ['body', 'author__email', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines         = [PostTopicInline, CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display    = ['id', 'author', 'post', 'created_at']
    search_fields   = ['body', 'author__email']
    readonly_fields = ['created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display    = ['user', 'post', 'created_at']
    readonly_fields = ['created_at']
