from rest_framework import generics, permissions
from .models import AttorneyListing
from .serializers import AttorneyListingSerializer


class AttorneyListCreateView(generics.ListCreateAPIView):
    serializer_class   = AttorneyListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs        = AttorneyListing.objects.select_related('user')
        visa_type = self.request.query_params.get('visa_type')
        if visa_type:
            qs = qs.filter(visa_types__icontains=visa_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AttorneyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = AttorneyListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = AttorneyListing.objects.all()
