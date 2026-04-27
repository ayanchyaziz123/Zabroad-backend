from rest_framework import generics, permissions
from .models import JobListing
from .serializers import JobListingSerializer


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class   = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs   = JobListing.objects.filter(is_active=True).select_related('posted_by')
        visa = self.request.query_params.get('visa_sponsorship')
        if visa:
            qs = qs.filter(visa_sponsorship=visa)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = JobListing.objects.all()
