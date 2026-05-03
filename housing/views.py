from django.db.models import Q
from rest_framework import generics, permissions
from zabroad_backend.permissions import IsOwnerOrReadOnly
from zabroad_backend.geo import apply_location_sort
from .models import HousingListing
from .serializers import HousingListingSerializer


class HousingListCreateView(generics.ListCreateAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs     = HousingListing.objects.filter(is_active=True).select_related('posted_by')
        params = self.request.query_params

        country = params.get('community')
        search  = params.get('search', '').strip()

        if country:
            qs = qs.filter(home_country__iexact=country)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            ).distinct()

        return apply_location_sort(qs, self.request)

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class HousingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset           = HousingListing.objects.filter(is_active=True)

    def get_serializer_context(self):
        return {'request': self.request}
