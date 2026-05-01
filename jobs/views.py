from django.db.models import Case, When, Value, IntegerField, FloatField
from django.db.models.expressions import RawSQL
from rest_framework import generics, permissions
from .models import JobListing
from .serializers import JobListingSerializer

_DIST_SQL = """
    CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL
    THEN (CAST(latitude  AS REAL) - %s) * (CAST(latitude  AS REAL) - %s)
       + (CAST(longitude AS REAL) - %s) * (CAST(longitude AS REAL) - %s)
    ELSE 999999.0 END
"""

def _apply_sort(qs, user_lat, user_lng, near_city):
    if user_lat is not None and user_lng is not None:
        return qs.annotate(
            distance=RawSQL(_DIST_SQL, (user_lat, user_lat, user_lng, user_lng), output_field=FloatField())
        ).order_by('distance', '-created_at')
    if near_city:
        city_prefix = near_city.split(',')[0].strip()
        return qs.annotate(
            loc_score=Case(
                When(location__iexact=near_city,        then=Value(3)),
                When(location__istartswith=city_prefix, then=Value(2)),
                When(location__icontains=city_prefix,   then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-loc_score', '-created_at')
    return qs.order_by('-created_at')


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class   = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs        = JobListing.objects.filter(is_active=True).select_related('posted_by')
        country   = self.request.query_params.get('community')
        near_city = self.request.query_params.get('near_city', '').strip()
        try:
            user_lat = float(self.request.query_params['lat'])
            user_lng = float(self.request.query_params['lng'])
        except (KeyError, ValueError, TypeError):
            user_lat = user_lng = None
        if country:
            qs = qs.filter(home_country__iexact=country)
        return _apply_sort(qs, user_lat, user_lng, near_city)

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = JobListing.objects.filter(is_active=True)
