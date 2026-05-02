from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from zabroad_backend.permissions import IsOwnerOrReadOnly
from zabroad_backend.geo import apply_location_sort
from .models import DoctorListing
from .serializers import DoctorListingSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class   = DoctorListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = DoctorListing.objects.select_related('user')
        if self.request.query_params.get('accepts_medicaid'):
            qs = qs.filter(accepts_medicaid=True)
        return apply_location_sort(qs, self.request, default_order=('-plan', '-created_at'), extra_order=('-plan',))

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'doctor_profile'):
            raise ValidationError({'detail': 'A doctor profile already exists for this account.'})
        serializer.save(user=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = DoctorListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset           = DoctorListing.objects.all()
