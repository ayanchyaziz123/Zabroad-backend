from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Post, Like, Comment, SavedPost
from .serializers import PostSerializer, CommentSerializer


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs       = Post.objects.select_related('author__profile').prefetch_related('topics', 'likes', 'comments')
        scope    = self.request.query_params.get('scope')
        topic    = self.request.query_params.get('topic')
        location = self.request.query_params.get('location')   # city filter, e.g. "Queens, NY"
        country  = self.request.query_params.get('country')    # home-country filter, e.g. "Bangladesh"
        if scope:
            qs = qs.filter(scope=scope)
        if topic:
            qs = qs.filter(topics__topic=topic)
        if location:
            qs = qs.filter(location__icontains=location)
        if country:
            qs = qs.filter(country__iexact=country)
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(body__icontains=search) |
                Q(topics__topic__icontains=search) |
                Q(location__icontains=search)
            ).distinct()
        return qs

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveDestroyAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = Post.objects.select_related('author__profile').prefetch_related('topics', 'likes', 'comments')

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_like(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        return Response({'liked': False, 'likes_count': post.likes_count})
    return Response({'liked': True, 'likes_count': post.likes_count})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def saved_posts(request):
    """Return all posts saved by the current user."""
    post_ids = SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)
    posts = (
        Post.objects
        .filter(id__in=post_ids)
        .select_related('author__profile')
        .prefetch_related('topics', 'likes', 'comments')
        .order_by('-created_at')
    )
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_save(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    save, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        save.delete()
        return Response({'saved': False})
    return Response({'saved': True})


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class   = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['pk']).select_related('author__profile')

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['pk'])
        serializer.save(author=self.request.user, post=post)
