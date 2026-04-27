from rest_framework import generics, permissions
from .models import HousingListing
from .serializers import HousingListingSerializer


class HousingListCreateView(generics.ListCreateAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = HousingListing.objects.filter(is_active=True).select_related('posted_by')
        if self.request.query_params.get('no_credit_check'):
            qs = qs.filter(no_credit_check=True)
        if self.request.query_params.get('accepts_itin'):
            qs = qs.filter(accepts_itin=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class HousingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = HousingListing.objects.all()
