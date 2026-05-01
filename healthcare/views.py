from django.db.models import Case, When, Value, IntegerField
from rest_framework import generics, permissions
from .models import DoctorListing
from .serializers import DoctorListingSerializer


def apply_near_city(qs, near_city):
    if not near_city:
        return qs.order_by('-plan', '-created_at')
    city_prefix = near_city.split(',')[0].strip()
    return qs.annotate(
        loc_score=Case(
            When(location__iexact=near_city,        then=Value(3)),
            When(location__istartswith=city_prefix, then=Value(2)),
            When(location__icontains=city_prefix,   then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('-loc_score', '-plan', '-created_at')


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class   = DoctorListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs        = DoctorListing.objects.select_related('user')
        near_city = self.request.query_params.get('near_city', '').strip()
        if self.request.query_params.get('accepts_medicaid'):
            qs = qs.filter(accepts_medicaid=True)
        return apply_near_city(qs, near_city)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = DoctorListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = DoctorListing.objects.all()
