from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from zabroad_backend.permissions import IsOwnerOrReadOnly
from .models import Event, EventRSVP
from .serializers import EventSerializer


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class   = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs       = Event.objects.prefetch_related('rsvps').select_related('posted_by')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset           = Event.objects.prefetch_related('rsvps').select_related('posted_by')


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
