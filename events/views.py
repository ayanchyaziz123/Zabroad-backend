import math
from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from zabroad_backend.permissions import IsOwnerOrReadOnly
from listings.models import Listing, EventDetail, EventRSVP
from .serializers import EventSerializer


def _haversine_filter(qs, lat, lng, radius_mi=50):
    # Bounding box narrows candidates in the DB before doing precise math in Python
    delta_lat = radius_mi / 69.0
    delta_lng = radius_mi / (69.0 * math.cos(math.radians(lat)))

    no_coords   = list(qs.filter(latitude__isnull=True))
    with_coords = qs.filter(
        latitude__isnull=False,
        latitude__gte=lat - delta_lat,
        latitude__lte=lat + delta_lat,
        longitude__gte=lng - delta_lng,
        longitude__lte=lng + delta_lng,
    )

    results = no_coords
    for e in with_coords:
        dlat = math.radians(float(e.latitude)  - lat)
        dlng = math.radians(float(e.longitude) - lng)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat))
             * math.cos(math.radians(float(e.latitude)))
             * math.sin(dlng / 2) ** 2)
        if 3958.8 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) <= radius_mi:
            results.append(e)
    return results


_BASE_QS = (
    Listing.objects
    .filter(listing_type=Listing.TYPE_EVENT)
    .select_related('posted_by', 'event_detail')
    .prefetch_related('event_detail__rsvps')
)


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class   = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs       = _BASE_QS.all()
        category = self.request.query_params.get('category')
        search   = self.request.query_params.get('search', '').strip()
        upcoming = self.request.query_params.get('upcoming', 'true')

        if category and category != 'all':
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            ).distinct()
        if upcoming == 'true':
            qs = qs.filter(event_detail__date__gte=timezone.now())

        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        if lat and lng:
            try:
                return _haversine_filter(list(qs), float(lat), float(lng))
            except (ValueError, TypeError):
                pass
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset           = _BASE_QS
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rsvp_event(request, pk):
    try:
        listing = Listing.objects.select_related('event_detail').get(
            pk=pk, listing_type=Listing.TYPE_EVENT
        )
    except Listing.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    event_detail = listing.event_detail
    rsvp, created = EventRSVP.objects.get_or_create(event=event_detail, user=request.user)
    if not created:
        rsvp.delete()
        return Response({'is_rsvped': False, 'rsvp_count': event_detail.rsvp_count})
    return Response({'is_rsvped': True, 'rsvp_count': event_detail.rsvp_count})
