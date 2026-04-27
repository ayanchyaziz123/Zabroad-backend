from rest_framework import generics, permissions
from .models import DoctorListing
from .serializers import DoctorListingSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class   = DoctorListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = DoctorListing.objects.select_related('user')
        if self.request.query_params.get('accepts_medicaid'):
            qs = qs.filter(accepts_medicaid=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = DoctorListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = DoctorListing.objects.all()
