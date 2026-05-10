import math
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from zabroad_backend.permissions import IsOwnerOrReadOnly
from .models import Event, EventRSVP
from .serializers import EventSerializer


def _haversine_sql_filter(qs, lat, lng, radius_mi=50):
    """Python-side distance filter (SQLite compat)."""
    results = []
    for e in qs:
        if e.latitude is None or e.longitude is None:
            results.append(e)
            continue
        dlat = math.radians(e.latitude  - lat)
        dlng = math.radians(e.longitude - lng)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(e.latitude)) * math.sin(dlng/2)**2
        d = 3958.8 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        if d <= radius_mi:
            results.append(e)
    return results


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class   = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs       = Event.objects.prefetch_related('rsvps').select_related('posted_by')
        category = self.request.query_params.get('category')
        search   = self.request.query_params.get('search', '').strip()
        upcoming = self.request.query_params.get('upcoming', 'true')

        if category and category != 'all':
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(description__icontains=search) | qs.filter(location__icontains=search)
        if upcoming == 'true':
            from django.utils import timezone
            qs = qs.filter(date__gte=timezone.now())

        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        if lat and lng:
            try:
                qs = _haversine_sql_filter(list(qs), float(lat), float(lng))
                return qs  # already a list
            except (ValueError, TypeError):
                pass
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset           = Event.objects.prefetch_related('rsvps').select_related('posted_by')
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rsvp_event(request, pk):
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    rsvp, created = EventRSVP.objects.get_or_create(event=event, user=request.user)
    if not created:
        rsvp.delete()
        return Response({'rsvped': False, 'rsvp_count': event.rsvp_count})
    return Response({'rsvped': True, 'rsvp_count': event.rsvp_count}, status=status.HTTP_201_CREATED)
