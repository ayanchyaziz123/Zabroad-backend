from django.db.models import Case, When, Value, IntegerField
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from zabroad_backend.permissions import IsOwnerOrReadOnly
from zabroad_backend.geo import apply_location_sort
from .models import Post, Like, Comment, SavedPost
from .serializers import PostSerializer, CommentSerializer

_MAX_SEARCH_LEN = 100


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs     = Post.objects.select_related('author__profile').prefetch_related('topics', 'likes', 'comments')
        params = self.request.query_params

        scope    = params.get('scope')
        topic    = params.get('topic')
        location = params.get('location')
        country  = params.get('country')
        author   = params.get('author')
        search   = params.get('search', '').strip()

        if scope:
            qs = qs.filter(scope=scope)
        if topic:
            qs = qs.filter(topics__topic=topic)
        if location:
            qs = qs.filter(location__icontains=location)
        if country:
            qs = qs.filter(country__iexact=country)
        if author:
            if self.request.user.is_authenticated and str(self.request.user.id) == author:
                qs = qs.filter(author_id=author)
            else:
                qs = qs.filter(author_id=author, is_anonymous=False)
        if search:
            if len(search) > _MAX_SEARCH_LEN:
                raise ValidationError({'detail': f'Search term must be {_MAX_SEARCH_LEN} characters or fewer.'})
            from django.db.models import Q
            qs = qs.filter(
                Q(body__icontains=search) |
                Q(topics__topic__icontains=search) |
                Q(location__icontains=search)
            ).distinct()

        # Posts have an extra author.lives_in fallback score — handled inline here
        # because it references a related field not available in the generic geo helper.
        near_city = params.get('near_city', '').strip()
        lat_raw   = params.get('lat')
        lng_raw   = params.get('lng')

        if lat_raw is not None and lng_raw is not None:
            # delegate to shared helper (validates coords, annotates distance)
            return apply_location_sort(qs, self.request)

        if near_city:
            city_prefix = near_city.split(',')[0].strip()
            return qs.annotate(
                loc_score=Case(
                    When(location__iexact=near_city,                       then=Value(4)),
                    When(location__istartswith=city_prefix,                then=Value(3)),
                    When(location__icontains=city_prefix,                  then=Value(2)),
                    When(author__profile__lives_in__icontains=city_prefix, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by('-loc_score', '-created_at')

        return qs.order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset           = Post.objects.select_related('author__profile').prefetch_related('topics', 'likes', 'comments')

    def get_serializer_context(self):
        return {'request': self.request}


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
    post_ids = SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)
    posts = (
        Post.objects
        .filter(id__in=post_ids)
        .select_related('author__profile')
        .prefetch_related('topics', 'likes', 'comments')
        .order_by('-created_at')
    )
    return Response(PostSerializer(posts, many=True, context={'request': request}).data)


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
