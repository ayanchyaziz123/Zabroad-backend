from rest_framework import generics, permissions
from .models import HousingListing
from .serializers import HousingListingSerializer


class HousingListCreateView(generics.ListCreateAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs      = HousingListing.objects.filter(is_active=True).select_related('posted_by')
        country = self.request.query_params.get('community')
        if country:
            qs = qs.filter(home_country__iexact=country)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class HousingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = HousingListing.objects.filter(is_active=True)
