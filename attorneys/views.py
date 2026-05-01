from rest_framework import generics, permissions
from .models import AttorneyListing
from .serializers import AttorneyListingSerializer


class AttorneyListCreateView(generics.ListCreateAPIView):
    serializer_class   = AttorneyListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs      = AttorneyListing.objects.filter(is_active=True).select_related('posted_by')
        country = self.request.query_params.get('community')
        if country:
            qs = qs.filter(home_country__iexact=country)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class AttorneyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = AttorneyListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = AttorneyListing.objects.filter(is_active=True)
